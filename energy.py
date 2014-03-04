import datetime
import requests
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
    content = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

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
        
    def tank_level(self, refresh=False):
        data = self.get_data(refresh)
        m = re.search(self.level_pattern, data)
        self.level = int(m.group(1))
        return self.level

    def last_fill(self, refresh=False):
        data = self.get_data(refresh)
        m = re.search(self.last_gallons_pattern, data)
        d = m.group(2)
        d = datetime.datetime.strptime(d.strip(), "%A, %B %d, %Y")
        f = re.search(self.last_price_pattern, data)
        return {'units':int(m.group(1)), 'date':d, 'ppu':float(f.group(1))}

        

unit = "Gallon(s)"

un = os.environ.get('ENERGY_USERNAME')
pw = os.environ.get('ENERGY_PASSWORD')

he = HamiltonEnergy(username=un, password=pw)
print "Current Level:"
print "{}% of 500 {}".format(he.tank_level(), unit)
print "Last Filled On:"
lf =  he.last_fill()
print lf.get('date')
print "Last Fill Amount:"
print "{} {}".format(lf.get('units'), unit)
print "Last Price per {}:".format(unit)
print "${}".format(lf.get('ppu'))


