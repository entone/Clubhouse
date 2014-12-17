from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan, bulk
from itertools import imap

OLD_INDEX = "clubhouse"
NEW_INDEX = "clubhouse2"
DOC_TYPES = []

ES = Elasticsearch()

def change_index(obj):
	obj['_index'] = NEW_INDEX	
	return obj

sc = scan(ES, index=OLD_INDEX, scroll="10m")
res = imap(change_index, sc)
b = bulk(ES, actions=res)

for i in b:
	print i