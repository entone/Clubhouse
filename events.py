import gevent
import time
import datetime
import random
import logging
from latlng import lat_lng
from elasticsearch import Elasticsearch

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)

ES = Elasticsearch()

SENSORS = [
    "WaterLevel",
    "SoilMoisture",
    "IndoorTemperature",
    "OutdoorTemperature",
    "IndoorHumidity",
    "OutdoorHumidity",
    "Windspeed"
]

while True:
    obj = {
        '@timestamp':datetime.datetime.utcnow(),
        '@message':random.randint(70, 100),
        '@location':lat_lng()
    }
    logging.info(obj)
    res = ES.index(index="clubhouse", doc_type=SENSORS[random.randint(0, len(SENSORS)-1)], body=obj)
    logging.info(res)
    gevent.sleep(.2)
