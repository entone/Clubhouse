import datetime
import requests
import pytz
import os
import re

class HamiltonEnergy(object):

    base_url = "https://www.myhamiltonenergy.com/Default.aspx"
    target = "ctl00$mLogin$btnlogin"
    username = None
    password = None
    level = 0
    last_fill = None
    level_pattern = "drawChart\((\d+)\)"
    last_gallons_pattern = "Last delivery\: (\d+) gallons on (.+)"
    last_price_pattern = "Current Price\: \$(\d+\.\d+)"
    last_payment_amount_pattern = "Last Payment Amount:</div><div class=\"de\">\$(\d+\.\d+)</div>"
    last_payment_date_pattern = "Last Payment Date:</div><div class=\"de\">(\d+/\d+/\d+)</div>"
    local_timezone = None


    content = None

    def __init__(self, username, password, timezone=None):
        self.username = username
        self.password = password
        self.local_timezone = timezone or pytz.timezone("US/Eastern")

    def get_data(self, refresh=False, test=False):
        if test: return open("./data_test.html").read()
        if not self.content or refresh:
            res = requests.post(self.base_url, data={
                'ctl00$mLogin$txtusername':self.username, 
                'ctl00$mLogin$txtpassword':self.password,
                '__EVENTTARGET':self.target
            }, verify=False)
            self.content = res.content
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



