#!/usr/bin/python
import sys
import yaml
import logging
import argparse
import subprocess

##############
# init logging
##############
logging.basicConfig(format="%(levelname).1s: %(message)s")

if hasattr(logging, 'getLevelNamesMapping'):
    levelNames = logging.getLevelNamesMapping().keys()
else:
    levelNames = { 'CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG' }

#################
# parse arguments
#################
parser = argparse.ArgumentParser(description="Check service endpoints to ensure that all IPs are backed by running pods")
parser.add_argument('--logLevel', choices=levelNames)
parser.add_argument('endpoints_file', type=argparse.FileType('r'), nargs="?", help="Use YAML formatted input file instead querying `oc get endpoints --all-namespaces -o yaml`")
parser.add_argument('pods_file', type=argparse.FileType('r'), nargs="?", help="Use YAML formatted input file instead querying `oc get pods --all-namespaces -o yaml`")

arguments = parser.parse_args()

logging.basicConfig(format="%(levelname).1s: %(message)s")
if arguments.logLevel is not None:
    logging.getLogger().setLevel(logging.getLevelNamesMapping()[arguments.logLevel])

################
# read endpoints
################
if arguments.endpoints_file is None:
    if hasattr(subprocess, 'run'):
        endpoints_run = subprocess.run(['oc', 'get', 'endpoints', '--all-namespaces', '-o', 'yaml'],
                                       check=True, capture_output=True)
        endpoints_out = endpoints_run.stdout
    else:
        endpoints_out = subprocess.check_output(['oc', 'get', 'endpoints', '--all-namespaces', '-o', 'yaml'])
else:
    endpoints_out = arguments.endpoints_file.read()
    arguments.endpoints_file.close()

try:
    endpoints = yaml.safe_load(endpoints_out)
except yaml.YAMLError as exc:
    logging.critical(exc)
    exit(1)

###########
# read pods
###########
if arguments.pods_file is None:
    if hasattr(subprocess, 'run'):
        pods_run = subprocess.run(['oc', 'get', 'pods', '--all-namespaces', '-o', 'yaml'],
                          check=True, capture_output=True)
        pods_out = pods_run.stdout
    else:
        pods_out = subprocess.check_output(['oc', 'get', 'pods', '--all-namespaces', '-o', 'yaml'])
else:
    pods_out = arguments.pods_file.read()
    arguments.pods_file.close()

try:
    pods = yaml.safe_load(pods_out)
except yaml.YAMLError as exc:
    logging.critical(exc)
    exit(1)

############################################
# build list of all pod IPs and their states
############################################
if 'items' not in pods:
    logging.error("no pod items found")
    exit(1)

runningPods = {}

logging.info("Building pod list")

for pod in pods['items']:
    if 'kind' not in pod:
        logging.error("item has no 'kind' attribute")
        continue

    if pod['kind'] == "Pod":
        logging.info("processing pod " + pod['status']['podIP'] + " " + pod['status']['phase'] + " " + pod['metadata']['namespace'] + '/' + pod['metadata']['name'])

        if pod['status']['phase'] == "Running":
            if pod['status']['podIP'] in runningPods:
                if pod['status']['podIP'] != pod['status']['hostIP']:
                    logging.warning("duplicate pod IP" + pod['status']['podIP'])
                else:
                    runningPods[pod['status']['podIP']]['hasHostIP'] = True
                runningPods[pod['status']['podIP']] = { 
                    'namespace': pod['metadata']['namespace'],
                    'name': pod['metadata']['name'],
                    'previousPod': runningPods[pod['status']['podIP']],
                    'podCount': runningPods[pod['status']['podIP']]['podCount'] + 1 }
            else:
                runningPods[pod['status']['podIP']] = {
                    'namespace': pod['metadata']['namespace'],
                    'name': pod['metadata']['name'],
                    'podCount': 1 }
        else:
            logging.warning("Skipping pod in status other than 'Running'" + pod['status']['phase']+
                             " IP: " + pod['status']['podIP'] +  + ""
                             " Namespace/name: " + pod['metadata']['namespace'] + '/' + pod['metadata']['name'])
    else:
        logging.error("unknown item type \"" + item['kind'] + "\"")

print("Processed " + str(len(pods['items'])) + " pods - " + str(len(runningPods)) + " unique IPs running")

#### test
# del runningPods['10.0.91.48']
# del runningPods['10.130.2.2']

#############################################################
# iterate through all endpoints, check that pod IPs are found
#############################################################
if 'items' not in endpoints:
    logging.error("no endpoint items found")
    exit(1)

errorCount = 0
for service in endpoints['items']:
    if 'kind' not in service:
        logging.error("item has no 'kind' attribute")
        continue

    if service['kind'] == "Endpoints":
        logging.info("checking service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])

        if 'subsets' not in service:
            logging.warning("  skipping - no subsets - service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])
            continue

        for subset in service['subsets']:
            for address in subset['addresses']:
                if 'targetRef' in address:
                    target = address['targetRef']
                else:
                    target = { "kind": "None" }

                logging.info("  check IP " + address['ip'])
                if target['kind'] not in { 'Pod', 'Node', 'None' }:
                    logging.warning("  unknown target type " + target['kind'] + " in service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])

                if address['ip'] not in runningPods:
                    errorCount += 1
                    logging.error("  INVALID SERVICE IP found: Pod IP " + address['ip'] + " from service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])
                else:
                    logging.info("    Found Pod IP " + address['ip'] + " from service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])
    else:
        logging.warning("skiping unknown item type \"", service['kind'], "\"")

print("Checked " + str(len(endpoints['items'])) + " services - " + str(errorCount) + " missing IPs found")