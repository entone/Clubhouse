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
                'C012$txtusername':self.username,
                'C012$txtpassword':self.password,
                '__EVENTTARGET':self.target,
                '__EVENTVALIDATION':'/wEdAAixajrIZlNj001ZCV+m6lQKHoM9t7hqPaUQE97abnwoi6CZa5hTyH84HHe34Te4p4/RAtsBqO8WzwzLHXCMch8ggNjXp5guGoNW5VAytZOxoeUI7sGl1euM09DHmP1FIIxQ4DHenw3+Ng5DiOdrAzrfxGZVd7rh3RUlaUuxePQah0HjPsBU9+iPDQaGk5eeUZ6PTtQBqddYrkidh9I1Nzyq',
                '__VIEWSTATE':'/wEPDwUJNzA1OTYwNjQ3ZBgEBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUjQzAyOSRjdGwwMCRjdGwwMCRjdGwwMCRsaXN0c0NvbnRyb2wFOkMwMjkkY3RsMDAkY3RsMDAkY3RsMDAkbGlzdHNDb250cm9sJGN0cmwwJGxpc3RJdGVtc0NvbnRyb2wFKkMwMzYkbmV3c0Zyb250ZW5kTGlzdCRjdGwwMCRjdGwwMCROZXdzTGlzdA8UKwAFZBQrAABkFgIeAl9jZmRkBTpDMDI5JGN0bDAwJGN0bDAwJGN0bDAwJGxpc3RzQ29udHJvbCRjdHJsMCRsaXN0SXRlbXNDb250cm9sDxQrAAVkFCsAAw8FBl8hRFNJQwIGDwULXyFJdGVtQ291bnQCBg8FCF8hUENvdW50ZGQWAh8AZmRkBSNDMDI5JGN0bDAwJGN0bDAwJGN0bDAwJGxpc3RzQ29udHJvbA8UKwAFZBQrAAMPBQZfIURTSUMCAQ8FC18hSXRlbUNvdW50AgEPBQhfIVBDb3VudGRkFgIfAGZkZCGtKlCgg6cYXVksNb4WfIbnVjOpq9gUguhQeM38po7T',
            }, verify=False)
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
