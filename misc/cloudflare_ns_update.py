#!/usr/bin/env python
import os
import re
import sys
import time
import logging
import CloudFlare

# Function to check if should i deal with this dns entry


def check_entry(entry):
    logging.info("Checking zone pattern for: {0}".format(entry))
    return re.match(r"[a-z]+[0-9]+\.bbb\.lokalni.pl", entry)


# Setup basic logger
logging.basicConfig(level=logging.DEBUG)

# Get cloudflare settings from environment
CF_KEY = os.getenv('CF_KEY')  # API Key
CF_ZONE_ID = os.getenv('CF_ZONE_ID')  # Zone identifier

# Setup Cloudflare
cf = CloudFlare.CloudFlare(token=CF_KEY)

if None in [CF_KEY, CF_ZONE_ID]:
    logging.critical("Please set CF_KEY and CF_ZONE_ID")
    sys.exit(1)

# Define dict of entries, that should be in cloudflare
entries = {}

# Populate entries dict with items from file
try:
    with open('/var/tmp/cf_entries', 'r') as zone_list:
        for zone_entry in zone_list.readlines():
            entries[zone_entry.split()[0].strip()] = zone_entry.split()[
                1].strip()
except IOError:
    logging.critical("Cannot open zone entries file /var/tmp/cf_entries")
    sys.exit(1)

logging.info("Loaded {0} entries from /var/tmp/cf_entries".format(
    len(entries)
))

# Add missing items
for entry in entries:
    dns_record = cf.zones.dns_records.get(
        CF_ZONE_ID, params={'name': entry, 'match': 'all', 'type': 'A'})
    # No entry - add
    if len(dns_record) == 0:
        cf.zones.dns_records.post(CF_ZONE_ID, data={
            'name': entry,
            'type': 'A',
            'content': entries[entry],
            'proxied': False
        })
        logging.info("Created: {0}".format(entry))
    else:
        # Entry in place - update if needed
        if dns_record[0]['content'] != entries[entry]:
            cf.zones.dns_records.put(CF_ZONE_ID, dns_record[0]['id'], data={
                'name': entry,
                'type': 'A',
                'content': entries[entry],
                'proxied': False
            })
            logging.info("Updated: {0}".format(entry))
        else:
            logging.info("No changes: {0}".format(entry))
# Now we are going to sleep for 30s, next ansible step must wait for CF propagation which takes around 15sec
logging.info("Sleeping for 30s".format(entry))
time.sleep(30.0)
