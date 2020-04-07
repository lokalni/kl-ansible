#!/usr/bin/env python
import requests
import hashlib

def get_host():
    return open(
               '/usr/share/bbb-web/WEB-INF/classes/bigbluebutton.properties'
           ).read().split(
               'bigbluebutton.web.serverURL=https://'
           )[1].split("\n")[0].strip()

def get_secret():
    return hashlib.sha1("getMeetings{}".format(open(
               '/usr/share/bbb-web/WEB-INF/classes/bigbluebutton.properties'
           ).read().split(
               'securitySalt='
           )[1].split("\n")[0].strip())).hexdigest()

def get_metrics():
    metrics = {
        "participantCount": 0,
        "voiceParticipantCount": 0,
        "videoCount": 0,
        "listenerCount": 0
    }
    for line in requests.get("https://{}/bigbluebutton/api/getMeetings?checksum={}".format(
               get_host(),
               get_secret()
           )).text.split("\n"):
        for key in metrics.keys():
            if key in line:
                metrics[key] += int(line.split(">")[1].split("<")[0])
    return metrics

def save_stats():
    filecontents = ""
    for metric, value in get_metrics().iteritems():
        filecontents += "bbb_{} {}\n".format(metric, value)
    with open("/var/tmp/metrics/bbb_stats.txt", "w") as fh:
    	fh.write(filecontents)

save_stats()
