import settings
from nest import Nest
from pprint import pprint

un = settings.NEST_USERNAME
pw = settings.NEST_PASSWORD
n = Nest(un, pw)
n.login()
n.get_status()
pprint(n.get_usage())