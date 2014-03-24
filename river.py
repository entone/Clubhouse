import requests
import datetime

def slugify(value):
    return "river-{}".format(value.split(",")[0].lower().replace(" ", "-"))

class USGSWaterServices(object):
    
    site = "04108660"
    format = "json"
    base_url = "http://waterservices.usgs.gov/nwis/iv/"
    date_format = "%Y-%m-%dT%H:%M:%S" #2014-03-04T15:00:00.000-05:00

    content = None

    def __init__(self, site="04108660", format="json"):
        self.site = site
        self.format = format

    def get_data(self, refresh=False):
        if not self.content or refresh:
            res = requests.get("{}?format={}&site={}".format(self.base_url, self.format, self.site))
            self.content = res.json()

        return self.content

    def preview(self):
        data = self.get_data()
        for v in data.get("value", {}).get("timeSeries"):
            print "Description:"
            print v.get("variable", {}).get("variableDescription")
            abbrv = v.get("variable", {}).get("unit", {}).get("unitAbbreviation")
            for i in v.get("values"):
                for vi in i.get("value"):
                    print "{}{}".format(vi.get("value"), abbrv)
                    pos = vi.get("dateTime").rfind(':')
                    ts = vi.get("dateTime").split(".")[0]
                    print "Timestamp: {}".format(datetime.datetime.strptime(ts, self.date_format))

    def values(self):
        values = {}
        data = self.get_data()
        for v in data.get("value", {}).get("timeSeries"):
            print "Description:"
            print v.get("variable", {}).get("variableDescription")
            abbrv = v.get("variable", {}).get("unit", {}).get("unitAbbreviation")
            for i in v.get("values"):
                for vi in i.get("value"):                    
                    print "{}{}".format(vi.get("value"), abbrv)
                    pos = vi.get("dateTime").rfind(':')
                    ts = vi.get("dateTime").split(".")[0]
                    print "Timestamp: {}".format(datetime.datetime.strptime(ts, self.date_format))
                    values[slugify(v.get("variable", {}).get("variableDescription"))] = {'value':float(vi.get("value")), 'timestamp':datetime.datetime.strptime(ts, self.date_format)}


        return values
