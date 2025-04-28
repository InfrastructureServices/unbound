#!/usr/bin/python
#
# Simple tool for estimating unbound cache usage

import subprocess
import csv
import sys
import time

def ub_getval(key):
    ubctl = subprocess.run(["unbound-control", "get_option", key], capture_output=True)
    return ubctl.stdout.strip()

def human_units(v, base=3):
    units = ['k', 'M', 'G', 'T', 'P']
    unit = ''
    for u in units:
        if v<base*1024:
            break
        v = v // 1024.0
        unit = u
    return '{0:3.5} {1}'.format(v, unit)

def print_kv(key, val, m):
    print('{0:25}: {1:6.4}%; {2:8} {3}'.format(
        key.decode(),
        float(val)/m * 100.0,
        human_units(float(val)),
        val.decode()))


def get_pid(command):
    cmd = subprocess.run(["pidof", command], capture_output=True)
    return int(cmd.stdout.strip())

def get_mem(pid, values):
    cmd = subprocess.run(["ps", "-o", "vsz=,rss=,%mem=", str(pid)], capture_output=True)
    line = cmd.stdout.strip().split()
    values["vsz"] = int(line[0])
    values["rss"] = int(line[1])
    values["%mem"] = float(line[2])

def process_stats(values = {}):
    stats = subprocess.run(["unbound-control", "stats_noreset"], capture_output=True)

    for line in stats.stdout.splitlines():
        key, val = line.split(b'=', 2)
        key = key.decode()
        if key.startswith("mem.") or key.startswith("num.") or key.startswith("time.") or key.endswith("cache.count") or key.startswith("total."):
            try:
                values[key] = int(val.decode())
            except ValueError:
                values[key] = float(val.decode())
    return values


if len(sys.argv) > 1:
    output = open(sys.argv[1], "w")
else:
    output = sys.stdout

interval = 15

pid = get_pid("unbound")

values = {}
process_stats(values)
get_mem(pid, values)

writer = csv.writer(output, dialect=csv.excel, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(values.keys())
while True:
    get_mem(pid, values)
    writer.writerow(values.values())
    output.flush()
    time.sleep(interval)
