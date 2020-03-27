#!/usr/bin/env python
import os
import re
import sys
import time
import logging
import requests

# Function to check if should i deal with this dns entry
def check_entry(entry):
    logging.info("Checking zone pattern for: {0}".format(entry))
    return re.match(r"[a-z]+[0-9]+\.(turn|bbb)\.lokalni.pl", entry)

# Setup basic logger
logging.basicConfig(level=logging.DEBUG)

# Get cloudflare settings from environment
CF_KEY = os.getenv('CF_KEY') # API Key
CF_ZONE_ID = os.getenv('CF_ZONE_ID') # Zone identifier

if None in [CF_KEY, CF_ZONE_ID]:
    logging.critical("Please set CF_KEY and CF_ZONE_ID")
    sys.exit(1)

# Define dict of entries, that should be in cloudflare
entries = {}

# Populate entries dict with items from file
try:
    with open('/var/tmp/cf_entries', 'r') as zone_list:
        for zone_entry in zone_list.readlines():
            entries[zone_entry.split()[0].strip()] = zone_entry.split()[1].strip()
except IOError:
    logging.critical("Cannot open zone entries file /var/tmp/cf_entries")
    sys.exit(1)
    
logging.info("Loaded {0} entries from /var/tmp/cf_entries".format(
        len(entries)
    ))

# Ask cloudflare for current list of entries

cf_entries = requests.get(
        "https://api.cloudflare.com/client/v4/zones/{0}/dns_records".format(CF_ZONE_ID), 
        headers = {
            "Authorization": "Bearer {0}".format(CF_KEY),
            "Content-Type": "application/json"
        }
).json().get('result', [])

# Dict with cloudflare items that are relevant for us
cloudflare_items = {}

# Go thru each CF entry
for entry in entries:
    for cf_entry in cf_entries:
        if check_entry(cf_entry['name']) and cf_entry['type']=='A':
            cloudflare_items[cf_entry['name']] = {
                    "ip": cf_entry['content'],
                    "id": cf_entry['id']
                }
# Add missing items
for entry in entries:
    if not entry in cloudflare_items:
        # Add CF entry
        requests.post(
                "https://api.cloudflare.com/client/v4/zones/{0}/dns_records".format(CF_ZONE_ID),
                headers = {
                    "Authorization": "Bearer {0}".format(CF_KEY),
                    "Content-Type": "application/json"
                },
                json = {
                    "type": "A",
                    "proxied": False,
                    "ttl": 1,
                    "content": entries[entry],
                    "name": entry,
                    "priority": 10
                }
        )
        logging.info("Added {} to CF".format(entry))
    else:
        if cloudflare_items[entry]['ip'] != entries[entry]:
            # We need to update this entry
            requests.put(
                    "https://api.cloudflare.com/client/v4/zones/{0}/dns_records/{1}".format(CF_ZONE_ID, cloudflare_items[entry]['id']),
                    headers = {
                        "Authorization": "Bearer {0}".format(CF_KEY),
                        "Content-Type": "application/json"
                    },
                    json = {
                        "type": "A",
                        "proxied": False,
                        "ttl": 1,
                        "content": entries[entry],
                        "name": entry,
                    }
            )
            logging.info("Updated {} CF entry".format(entry))

# Now we are going to sleep for 30s, next ansible step must wait for CF propagation which takes around 15sec
time.sleep(30.0)
