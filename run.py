from elasticsearch import Elasticsearch
from energy import HamiltonEnergy
from nest import Nest
from river import USGSWaterServices
from wunderground import Wunderground
from pprint import pprint
import settings
import gevent

es = Elasticsearch()

while True:
    #Energy
    unit = "Gallon(s)"
    un = settings.HAMILTON_ENERGY_UN
    pw = settings.HAMILTON_ENERGY_PW
    he = HamiltonEnergy(username=un, password=pw)
    print "Current Level:"
    print "{}% of 500 {}".format(he.tank_level(), unit)
    print "Last Filled On:"
    lf =  he.last_fill()
    print lf.get('date')
    print "Last Fill Amount:"
    print "{} {}".format(lf.get('units'), unit)
    print "Last Price per {}:".format(unit)
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
    print "Current Humidity:"
    print n.show_curhumidity()
    #River
    kzoo_river = USGSWaterServices(site=settings.USGS_SITE)
    kzoo_river.preview()
    #Wunderground
    wg = Wunderground(settings.WUNDERGROUND_API_KEY, settings.WUNDERGROUND_STATION_ID)
    pprint(wg.data)
    gevent.sleep(20)







doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime(2010, 10, 10, 10, 10, 10)
}
res = es.index(index="test-index", doc_type='tweet', id=1, body=doc)