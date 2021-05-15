#!/usr/bin/env python
import requests
import sys
import random
import time

APP_ENDPOINT="https://app.teleklasa.lokalni.pl"

def get_cores():
     return int(open(
               '/proc/cpuinfo'
           ).read().split(
               'processor	: '
           )[-1].split("\n")[0].strip())+1

def get_load():
    return float(open('/proc/loadavg').read().split()[1])

def get_host():
    return open(
               '/etc/bigbluebutton/bbb-web.properties'
           ).read().split(
               'bigbluebutton.web.serverURL=https://'
           )[1].split("\n")[0].strip()

def get_secret():
    return open(
               '/etc/bigbluebutton/bbb-web.properties'
           ).read().split(
               'securitySalt='
           )[1].split("\n")[0].strip()

def get_region():
    return open('/etc/region').read().strip()

def heartbeat():
    requests.post(
        "{}/api/v1/nodes/keepalive/".format(APP_ENDPOINT),
        json={
            "cpu_count": get_cores(),
            "load_5m": get_load(),
            "api_secret": get_secret(),
            "hostname": get_host(),
            "region": get_region()
        }
    )

def register():
    requests.post(
        "{}/api/v1/nodes/".format(APP_ENDPOINT),
        json={
            "hostname": get_host(),
            "api_secret": get_secret()
        }
    )

if __name__=="__main__":
    # Random sleep to not hit app server too hard
    time.sleep(random.uniform(0.0,3.0))
    if sys.argv[1] == "heartbeat":
        heartbeat()
    elif "register":
        register()
