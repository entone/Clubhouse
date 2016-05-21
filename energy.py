import datetime
import requests
import pytz
import os
import re

class HamiltonEnergy(object):

    base_url = "https://www.chshamilton.com"
    target = "C012$btnlogin"
    username = None
    password = None
    level = 0
    last_fill = None
    level_pattern = "drawChart\((\d+\.\d+)\)"
    last_gallons_pattern = "Last delivery\: (\d+) gallons on (.+)"
    last_price_pattern = "Current Price\: \$(\d+\.\d+)"
    last_payment_amount_pattern = "Last Payment Amount:</div><div class=\"de\">\$(\d+\.\d+)</div>"
    last_payment_date_pattern = "Last Payment Date:</div><div class=\"de\">(\d+/\d+/\d+)</div>"
    event_validation_pattern = "id=\"__EVENTVALIDATION\" value=\"(.+?)\""
    viewstate_pattern = "id=\"__VIEWSTATE\" value=\"(.+?)\""
    local_timezone = None


    content = None

    def __init__(self, username, password, timezone=None):
        self.username = username
        self.password = password
        self.local_timezone = timezone or pytz.timezone("US/Eastern")

    def get_state(self):
        res = requests.get(self.base_url)
        content = res.content
        e = re.search(self.event_validation_pattern, content)
        v = re.search(self.viewstate_pattern, content)
        event = e.group(1)
        viewstate = v.group(1)
        return (event, viewstate)


    def get_data(self, refresh=False, test=False):
        if test: return open("./data_test.html").read()
        if not self.content or refresh:
            event, viewstate = self.get_state()
            res = requests.post(self.base_url, data={
                'C012$txtusername':self.username,
                'C012$txtpassword':self.password,
                '__EVENTTARGET':self.target,
                '__EVENTVALIDATION':event,
                '__VIEWSTATE':viewstate
            }, verify=False, timeout=10)
            self.content = res.content
            print self.content
        return self.content

    def convert_date(self, naive):
        local_dt = self.local_timezone.localize(naive)
        return local_dt.astimezone(pytz.utc)

    def tank_level(self, refresh=False):
        data = self.get_data(refresh)
        m = re.search(self.level_pattern, data)
        self.level = float(m.group(1))
        return self.level

    def last_payment(self, refresh=False):
        data = self.get_data(refresh)
        m = re.search(self.last_payment_date_pattern, data)
        d = m.group(1)
        d = self.convert_date(datetime.datetime.strptime(d.strip(), "%m/%d/%Y"))
        f = re.search(self.last_payment_amount_pattern, data)
        return {'amount':float(f.group(1)), 'date':d}

    def last_fill(self, refresh=False):
        data = self.get_data(refresh)
        m = re.search(self.last_gallons_pattern, data)
        d = m.group(2)
        d = self.convert_date(datetime.datetime.strptime(d.strip(), "%A, %B %d, %Y"))
        f = re.search(self.last_price_pattern, data)
        return {'units':float(m.group(1)), 'date':d, 'ppu':float(f.group(1))}
