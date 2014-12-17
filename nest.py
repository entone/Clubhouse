import os
import json
import requests
import datetime
import pytz

class Nest(object):

    base_url = "https://home.nest.com"    

    def __init__(self, username, password, serial=None, index=0, units="C", timezone=None):
        self.local_timezone = timezone or pytz.timezone("US/Eastern")
        self.serial = serial
        self.units = units
        self.index = index
        self.transport_url = None
        self.access_token = None
        self.userid = None
        self.structure_id = None
        self.device_id = None
        self.status = None
        self.username = username
        self.password = password
        self.version = None
        self.timestamp = None

    def login(self):
        res = requests.post(
            self.base_url+"/user/login",
            data={"username": self.username, "password": self.password},
            headers={"user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4"},
            timeout=10
        )

        j = res.json()
        self.transport_url = j["urls"]["transport_url"]
        self.access_token = j["access_token"]
        self.userid = j["userid"]

    def convert_date(self, naive):
        local_dt = self.local_timezone.localize(naive)
        return local_dt.astimezone(pytz.utc)

    def get_status(self):
        res = requests.get(
            "{}/v2/mobile/user.{}".format(self.transport_url, self.userid),
            headers={
                "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization":"Basic " + self.access_token,
                "X-nl-user-id": self.userid,
                "X-nl-protocol-version": "1"
            },
	    timeout=10
        )

        j = res.json()
        self.structure_id = j["structure"].keys()[0]        

        if (self.serial is None):
            self.device_id = j["structure"][self.structure_id]["devices"][self.index]
            self.serial = self.device_id.split(".")[1]
            self.version = j['device'][self.serial]['$version']
            self.timestamp = j['device'][self.serial]['$timestamp']

        self.status = j

    def get_usage(self):
        print self.transport_url
        res = requests.post(
            "{}/v5/subscribe".format(self.transport_url),
            headers={
                "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization":"Basic " + self.access_token,
                "X-nl-protocol-version": "1",
                "Content-Type":"application/json",
                "X-nl-user-id": self.userid,
                "X-nl-subscribe-timeout":60,
                "X-Requested-With":"XMLHttpRequest"
            },
            data=json.dumps({'objects':[{'object_key':'energy_latest.02AA01AC201303YM'}]}),
	    timeout=10
        )
        j = res.json()
        days = {}
        for day in j['objects'][0]['value']['days']:
            day_start = datetime.datetime.strptime(day['day'], "%Y-%m-%d")
            days[day['day']] = {'furnace':[], 'ac':[]}
            for c in day['cycles']:
                ts = self.convert_date(day_start+datetime.timedelta(seconds=int(c['start'])))
                duration = int(c['duration'])
                if c['type'] == 1:
                    days[day['day']]['furnace'].append({'timestamp':ts, 'duration':float(duration)})
                else:
                    days[day['day']]['ac'].append({'timestamp':ts, 'duration':float(duration)})

        return days




    def temp_in(self, temp):
        if (self.units == "F"):
            return (temp - 32.0) / 1.8
        else:
            return temp

    def temp_out(self, temp):
        if (self.units == "F"):
            return temp*1.8 + 32.0
        else:
            return temp

    def show_status(self):
        shared = self.status["shared"][self.serial]
        device = self.status["device"][self.serial]

        allvars = shared
        allvars.update(device)

        for k in sorted(allvars.keys()):
             print k + "."*(32-len(k)) + ":", allvars[k]

    def show_curtemp(self):
        temp = self.status["shared"][self.serial]["current_temperature"]
        temp = self.temp_out(temp)

        return float(temp)

    def show_curhumidity(self):
        return float(self.status["device"][self.serial]["current_humidity"])

    def set_temperature(self, temp):
        temp = self.temp_in(temp)

        res = requests.post(
            "{}/v2/put/shared.{}".format(self.transport_url, self.serial),
            data='{"target_change_pending":true,"target_temperature":{}}'.format('%0.1f' % temp),
            headers={
                "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization":"Basic " + self.access_token,
                "X-nl-protocol-version": "1"
            }
        )
        return res.text

    def set_fan(self, state):
        res = requests.post(
            "{}/v2/put/device.{}".format(self.transport_url, self.serial),
            data='{"fan_mode":"{}"}'.format(state),
            headers={
                "user-agent":"Nest/1.1.0.10 CFNetwork/548.0.4",
                "Authorization":"Basic " + self.access_token,
                "X-nl-protocol-version": "1"
            }
        )
        return res.text
