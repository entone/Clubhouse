import requests
import settings

KEYS = ['UV', 'dewpoint_c', 'feelslike_c', 'heatindex_c', 'precip_1hr_metric',
        'precip_today_metric', 'pressure_in', 'pressure_mb', 'relative_humidity',
        'solarradiation', 'temp_c', 'visibility_km', 'wind_degrees', 'wind_gust_kph', 'wind_kph', 'windchill_c']

def slugify(value):
    return "weatherstation-{}".format(value.replace("_", "-"))

class Wunderground(object):

    def __init__(self, api_key, station_id):
        current_conditions = "http://api.wunderground.com/api/{}/conditions/q/pws:{}.json".format(api_key, station_id)
        daily_history = "http://api.wunderground.com/api/{}/history_20130304/q/pws:{}.json".format(api_key, station_id)
        res = requests.get(current_conditions, timeout=10)
        self.data = res.json()

    def values(self):
        vals = {}
        for k,v in self.data.get('current_observation').iteritems():
            if k in KEYS:
                try:
                    value = float(v)
                except:
                    try:
                        value = float(v[0:-1])
                    except: value = 0
                vals[slugify(k)] = value

        return vals
