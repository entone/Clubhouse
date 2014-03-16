import requests
import settings

class Wunderground(object):

    def __init__(self, api_key, station_id):
        current_conditions = "http://api.wunderground.com/api/{}/conditions/q/pws:{}.json".format(api_key, station_id)
        daily_history = "http://api.wunderground.com/api/{}/history_20130304/q/pws:{}.json".format(api_key, station_id)
        res = requests.get(current_conditions)
        self.data = res.json()