#!/usr/bin/env python
import subprocess

def get_iptables():
    output, _ = subprocess.Popen(
        [
            '/sbin/iptables',
            '-L', 'INPUT', '-v', '-n', '-x'
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()
    return output.split("\n")

def create_metrics():
    values = []
    names = ['bbb_fw_udp', 'bbb_fw_http', 'bbb_fw_https']
    for item in get_iptables():
        if "bigbluebutton" in item:
            values.append(int(item.strip().split()[0]))
    return dict(zip(names, values))

def save_stats():
    filecontents = ""
    for metric, value in create_metrics().iteritems():
        filecontents += "{} {}\n".format(metric, value)
    with open("/var/tmp/metrics/bbb_fw_stats.prom", "w") as fh:
    	fh.write(filecontents+"\n")

if __name__ == "__main__":
    save_stats()
