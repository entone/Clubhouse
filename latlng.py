import math
import random
import requests

def rad2deg(arg):
    return (360 * arg / (2 * math.pi))

def sinh (arg):
    return (math.exp(arg) - math.exp(-arg))/2

def sec (arg):
    return 1 / math.cos(arg)


def lat_lng():
    x = -math.pi/2;
    y = math.pi/2; #[-PI;PI]
    lat = False;
    lng = False;
    distortion = 0;
    floats = [random.random(), random.random()]
    x = floats[0] * 2.0 * math.pi - math.pi
    y = floats[1] * 2.0 - 1.0
    lng = rad2deg(x)
    latrad = math.pi/2 - math.acos(y)
    lat = rad2deg(latrad)
    return (lat, lng)