from elasticsearch import Elasticsearch
from energy import HamiltonEnergy
from nest import Nest
from river import USGSWaterServices
from wunderground import Wunderground
from airvision import AirVision
from pnut import PNUT
from model import TimeSeriesMetric
import datetime
from pprint import pprint
import settings
import md5
import logging
import gevent
import schedule
import os

logging.basicConfig(level=logging.DEBUG)



def energy():
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

def run_pnut():
    try:
        n = PNUT()
        status = n.get_status()
        pprint(status)
        for ups,vals in status.iteritems():
            for k,v in vals.iteritems():
                tm = TimeSeriesMetric(k, v).save()
    except Exception as e:
        logging.exception(e)

def nest():
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

def nest_usage():
    #Nest Usage
    print "woot"
    try:
        un = settings.NEST_USERNAME
        pw = settings.NEST_PASSWORD
        n = Nest(un, pw)
        n.login()
        n.get_status()
        usage = n.get_usage()
        for day in usage:          
            for k, cycles in usage[day].iteritems():
                for use in cycles:
                    logging.info("{} ran at: {} for {}".format(k, use['timestamp'], use['duration']))
                    it = TimeSeriesMetric('{}-usage'.format(k), use['duration'], use['timestamp']).save()
    except Exception as e:
        logging.exception(e)


def river():
    #River
    try:
        kzoo_river = USGSWaterServices(site=settings.USGS_SITE)
        pprint(kzoo_river.content)
        for k,v in kzoo_river.values().iteritems():
            logging.info("{}: {}".format(k, v))
            t = TimeSeriesMetric(k, v.get('value'), v.get('timestamp')).save()
    except Exception as e:
        logging.exception(e)

def wunderground():
    #Wunderground
    try:
        wg = Wunderground(settings.WUNDERGROUND_API_KEY, settings.WUNDERGROUND_STATION_ID)
        for k,v in wg.values().iteritems():
            logging.info("{}: {}".format(k,v))
            t = TimeSeriesMetric(k, v).save()
    except Exception as e:
        logging.exception(e)

def airvision():
    av = AirVision()
    r = av.get_recordings()
    for camera, recordings in r.iteritems():   
        logging.info(camera)     
        for rec in recordings:
            logging.info("{}: {}".format(rec['length'],rec['timestamp']))
            t = TimeSeriesMetric(camera, rec['length'], rec['timestamp']).save()


#Register events
schedule.every(6).hours.do(energy)
schedule.every(10).minutes.do(nest)
schedule.every(12).hours.do(nest_usage)
schedule.every(15).minutes.do(river)
schedule.every(3).minutes.do(wunderground)
schedule.every(5).minutes.do(airvision)
schedule.every(1).minute.do(run_pnut)

energy()
nest()
nest_usage()
river()
wunderground()
airvision()
run_pnut()

while True:
    schedule.run_pending()
    gevent.sleep(60)


