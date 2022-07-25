#!/usr/bin/python
from asyncio.subprocess import PIPE
from email.mime import base
import sys
import os
import subprocess
import base64
import json
import pprint
import argparse

# Assumes environment is set up properly with ETCDCTL_ENDPOINTS, ETCDCTL_CERT, ETCDCTL_CACERT, ETCDCTL_KEY
parser = argparse.ArgumentParser(description="Inventory an etcd instance and report count and size of all key/value pairs")
parser.add_argument('--depth', type=int, help="Maximum depth of results to report")
parser.add_argument('--prefix', help="Report only on matching prefixes")
parser.add_argument('--filter', help="Report only on keys containing filter")
parser.add_argument('input_file', type=argparse.FileType('r'), nargs="?", help="Use JSON formmated input file instead of querying etcd")

arguments = parser.parse_args()

if arguments.input_file is None:
    etcd = subprocess.run(['etcdctl', 'get', '--prefix', '/', '--write-out=json', '--dial-timeout=5m', '--command-timeout=5m'],
                      check=True, stdout=PIPE)
    etcd_out = etcd.stdout.decode()
else:
    etcd_file = open(sys.argv[1], "r")
    etcd_out = etcd_file.read()
    etcd_file.close()
etcd_keys = json.loads(etcd_out)

totals = {}

for entry in etcd_keys['kvs']:
    key = base64.b64decode(entry['key']).decode()
    size = len(base64.b64decode(entry['value']))
    split_key = key.split('/')
    key_so_far = ""
    depth = -1
    for nesting in split_key:
        depth += 1
        key_so_far += nesting
        if depth < len(split_key):
            key_so_far += "/"
        if key_so_far not in totals.keys():
            totals[key_so_far] = {}
            totals[key_so_far]['count'] = 0
            totals[key_so_far]['size']  = 0
            totals[key_so_far]['depth'] = depth
        totals[key_so_far]['count'] += 1
        totals[key_so_far]['size']  += size

if arguments.depth is not None:
    totals = { key:attribs for (key,attribs) in totals.items() if attribs['depth'] <= arguments.depth }

if arguments.prefix is not None:
    totals = { key:attribs for (key,attribs) in totals.items() if key.startswith(arguments.prefix)  }

if arguments.filter is not None:
    totals = { key:attribs for (key,attribs) in totals.items() if arguments.filter in key }

pprint.pprint(totals)
