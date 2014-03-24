from elasticsearch import Elasticsearch
from energy import HamiltonEnergy
from nest import Nest
from river import USGSWaterServices
from wunderground import Wunderground
import datetime
from pprint import pprint
import settings
import logging
import gevent

logging.basicConfig(level=logging.DEBUG)

es = Elasticsearch()

class TimeSeriesMetric(object):
    _type = None
    value = 0
    timestamp = None

    def __init__(self, type, value, timestamp=None):
        self._type = type
        self.value = value
        self.timestamp = timestamp

    def save(self):
        doc = dict(
            value=self.value,
            timestamp=self.timestamp or datetime.datetime.utcnow()
        )
        res = es.index(index=settings.ES_INDEX, doc_type=self._type, body=doc)
        print res



while True:
    #Energy
    try:
        unit = "Gallon(s)"
        un = settings.HAMILTON_ENERGY_UN
        pw = settings.HAMILTON_ENERGY_PW
        he = HamiltonEnergy(username=un, password=pw)
        logging.info("Current Level: {}% of 500 {}".format(he.tank_level(), unit))
        gl = TimeSeriesMetric('propane-level', he.tank_level()).save()        
        lf =  he.last_fill()
        logging.info("Last Filled On: {}".format(lf.get('date')))        
        logging.info("Last Fill Amount: {} {}".format(lf.get('units'), unit))
        logging.info("Last Price per {}: {}".format(unit, lf.get('ppu')))
        fill = TimeSeriesMetric('propane-fill', lf.get('units'), lf.get('date')).save()
        ppu = TimeSeriesMetric('propane-ppu', lf.get('ppu'), lf.get('date')).save()
        lp = he.last_payment()
        logging.info("Last Payment: ${} on {}".format(lp['amount'], lp['date']))
        lsp = TimeSeriesMetric('propane-last-payment', lp['amount'], lp['date']).save()
    except Exception as e:
        logging.exception(e)
    #Nest
    try:
        un = settings.NEST_USERNAME
        pw = settings.NEST_PASSWORD
        n = Nest(un, pw)
        n.login()
        n.get_status()
        logging.info("Current Temperature: {}".format(n.show_curtemp()))
        it = TimeSeriesMetric('indoor-temperature', n.show_curtemp()).save()
        logging.info("Current Humidity: {}".format(n.show_curhumidity()))
        ih = TimeSeriesMetric('indoor-humidity', n.show_curhumidity()).save()
    except Exception as e:
        logging.exception(e)
    #River
    try:
        kzoo_river = USGSWaterServices(site=settings.USGS_SITE)
        for k,v in kzoo_river.values().iteritems():
            logging.info("{}: {}".format(k, v))
            t = TimeSeriesMetric(k, v.get('value'), v.get('timestamp')).save()
    except Exception as e:
        logging.exception(e)
    #Wunderground
    try:
        wg = Wunderground(settings.WUNDERGROUND_API_KEY, settings.WUNDERGROUND_STATION_ID)
        for k,v in wg.values().iteritems():
            logging.info("{}: {}".format(k,v))
            t = TimeSeriesMetric(k, v).save()
    except Exception as e:
        logging.exception(e)
    

    gevent.sleep(10*60)#update data every 10 minutes