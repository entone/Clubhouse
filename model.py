from elasticsearch import Elasticsearch
import datetime
import md5
import settings

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
        id = md5.new("{}{}{}".format(self._type, self.value, str(doc['timestamp']))).hexdigest()
        print id
        res = es.index(index=settings.ES_INDEX, doc_type=self._type, id=id, body=doc)
        print res