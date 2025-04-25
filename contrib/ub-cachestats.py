#!/usr/bin/python
#
# Simple tool for estimating unbound cache usage

import subprocess


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


stats = subprocess.run(["unbound-control", "stats_noreset"], capture_output=True)

for line in stats.stdout.splitlines():
    key, val = line.split(b'=', 2)
    if key == b'mem.cache.rrset':
        m = float(ub_getval('rrset-cache-size'))
        print_kv(key, val, m)
    elif key == b'mem.cache.message':
        m = float(ub_getval('msg-cache-size'))
        print_kv(key, val, m)
    elif key == b'mem.http.query_buffer':
        m = float(ub_getval('http-query-buffer-size'))
        print_kv(key, val, m)
    elif key == b'mem.http.response_buffer':
        m = float(ub_getval('http-response-buffer-size'))
        print_kv(key, val, m)
    else:
        #print(str(key))
        pass
