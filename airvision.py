from pymongo import MongoReplicaSetClient, MongoClient
import datetime
import pytz

def slugify(value):
    return value.replace(".", "-")


class AirVision(object):

    def __init__(self):
        self.conn = MongoClient("localhost", 7444)
        self.db = self.conn['ubnt-video']

    def get_recordings(self):
        events = {}
        for d in self.db.recording.find():
            typ = events.setdefault(slugify(d['cameraName']), [])            
            start = datetime.datetime.fromtimestamp(d['startTime'], tz=pytz.utc)
            typ.append({'length':float(d['length']), 'timestamp':start})

        return events
    
