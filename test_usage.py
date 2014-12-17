import settings
import logging
from energy import HamiltonEnergy
from pprint import pprint

logging.basicConfig(level=logging.DEBUG)

def energy():
    #Energy
    try:
        unit = "Gallon(s)"
        un = 'entone@gmail.com'#settings.HAMILTON_ENERGY_UN
        pw = 'abudabu!'#settings.HAMILTON_ENERGY_PW
        he = HamiltonEnergy(username=un, password=pw)
        logging.info("Current Level: {}% of 500 {}".format(he.tank_level(), unit))
        #gl = TimeSeriesMetric('propane-level', he.tank_level()).save()
        lf =  he.last_fill()
        logging.info("Last Filled On: {}".format(lf.get('date')))
        logging.info("Last Fill Amount: {} {}".format(lf.get('units'), unit))
        logging.info("Last Price per {}: {}".format(unit, lf.get('ppu')))
        #fill = TimeSeriesMetric('propane-fill', lf.get('units'), lf.get('date')).save()
        #ppu = TimeSeriesMetric('propane-ppu', lf.get('ppu'), lf.get('date')).save()
        lp = he.last_payment()
        logging.info("Last Payment: ${} on {}".format(lp['amount'], lp['date']))
        #lsp = TimeSeriesMetric('propane-last-payment', lp['amount'], lp['date']).save()
    except Exception as e:
        logging.exception(e)

energy()
