from lib.PyNUT import PyNUTClient

KEYS = ['battery.charge', 'battery.voltage', 'battery.runtime', 'input.voltage', 'ups.load']

def slugify(ups, name):
    return "{}-{}".format(ups, name.replace(".", "-"))

class PNUT(object):

    def __init__(self):
        self._pnut = PyNUTClient(login='clubhouse', password='abudabu1', debug=True)

    def get_status(self):
        ups = self._pnut.GetUPSList()
        upss = {}
        for u,v in ups.iteritems():
            up = upss.setdefault(u, {})
            for c,v in self._pnut.GetUPSVars(u).iteritems():
                if c in KEYS:
                    up[slugify(u, c)] = float(v)

        return upss