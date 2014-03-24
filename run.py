from elasticsearch import Elasticsearch
from energy import HamiltonEnergy
from nest import Nest
from river import USGSWaterServices
from wunderground import Wunderground
import datetime
from pprint import pprint
import settings
import gevent

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
    unit = "Gallon(s)"
    un = settings.HAMILTON_ENERGY_UN
    pw = settings.HAMILTON_ENERGY_PW
    he = HamiltonEnergy(username=un, password=pw)
    print "Current Level:"
    print "{}% of 500 {}".format(he.tank_level(), unit)
    gl = TimeSeriesMetric('propane-level', he.tank_level()).save()
    print "Last Filled On:"
    lf =  he.last_fill()
    print lf.get('date')
    fill = TimeSeriesMetric('propane-fill', lf.get('units'), lf.get('date')).save()
    print "Last Fill Amount:"
    print "{} {}".format(lf.get('units'), unit)
    print "Last Price per {}:".format(unit)
    ppu = TimeSeriesMetric('propane-ppu', lf.get('ppu'), lf.get('date')).save()
    print "${}".format(lf.get('ppu'))
    #Nest
    un = settings.NEST_USERNAME
    pw = settings.NEST_PASSWORD
    n = Nest(un, pw)
    n.login()
    n.get_status()
    n.show_status()
    print "Current Temperature:"
    print n.show_curtemp()
    it = TimeSeriesMetric('indoor-temperature', n.show_curtemp()).save()
    print "Current Humidity:"
    print n.show_curhumidity()
    ih = TimeSeriesMetric('indoor-humidity', n.show_curhumidity()).save()
    #River
    kzoo_river = USGSWaterServices(site=settings.USGS_SITE)
    for k,v in kzoo_river.values().iteritems():
        print "{}: {}".format(k, v)
        t = TimeSeriesMetric(k, v.get('value'), v.get('timestamp')).save()
    #Wunderground
    wg = Wunderground(settings.WUNDERGROUND_API_KEY, settings.WUNDERGROUND_STATION_ID)
    for k,v in wg.values().iteritems():
        print "{}: {}".format(k,v)
        t = TimeSeriesMetric(k, v).save()
    gevent.sleep(20)