import os
import requests
from pprint import pprint

API_KEY = os.environ.get("WUNDERGROUND_KEY")

current_conditions = "http://api.wunderground.com/api/{}/conditions/q/pws:KMIHOLLA1.json".format(API_KEY)

daily_history = "http://api.wunderground.com/api/{}/history_20130304/q/pws:KMIHOLLA1.json".format(API_KEY)

res = requests.get(current_conditions)

pprint(res.json())