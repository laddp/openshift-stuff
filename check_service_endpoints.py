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
parser.add_argument('data_file', type=argparse.FileType('r'), nargs="?", help="Use YAML formatted input file instead of querying `oc get endpoints,pods --all-namespaces -o yaml`")

arguments = parser.parse_args()

logging.basicConfig(format="%(levelname).1s: %(message)s")
if arguments.logLevel is not None:
    logging.getLogger().setLevel(logging.getLevelNamesMapping()[arguments.logLevel])

################
# read datafile
################
if arguments.data_file is None:
    print("Gathering endpoint and pod data from oc")
    if hasattr(subprocess, 'run'):
        data_run = subprocess.run(['oc', 'get', 'endpoints,pods', '--all-namespaces', '-o', 'yaml'],
                                  check=True, capture_output=True)
        data_out = data_run.stdout
    else:
        data_out = subprocess.check_output(['oc', 'get', 'endpoints,pods', '--all-namespaces', '-o', 'yaml'])
else:
    print("Loading endpoint and pod data from " + arguments.data_file.name)
    data_out = arguments.data_file.read()
    arguments.data_file.close()

print("Endpoint and pod data loaded, parsing")

try:
    data = yaml.safe_load(data_out)
except yaml.YAMLError as exc:
    logging.critical(exc)
    exit(1)

print("Endpoint and pod data parsed")

############################################
# build list of all pod IPs and their states
############################################
if 'items' not in data:
    logging.error("no pod or endpoint items found")
    exit(1)

runningPods = {}
podCount = 0
runningCount = 0

print("Cataloging pod data")
for item in data['items']:
    if 'kind' not in item:
        logging.error("item has no 'kind' attribute")
        continue

    if item['kind'] == "Pod":
        podCount += 1
        pod = item
        logging.info("processing pod " + 
                     (pod['status']['podIP'] if 'podIP' in pod['status'] else "") + " " +
                     pod['status']['phase'] + " " + pod['metadata']['namespace'] + '/' + pod['metadata']['name'])

        if pod['status']['phase'] == "Running":
            runningCount += 1
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
            logging.info("Skipping pod in status other than 'Running' - " + pod['status']['phase'] +
                         (" IP: " + pod['status']['podIP'] + " ") if 'podIP' in pod['status'] else "" +
                         " Namespace/name: " + pod['metadata']['namespace'] + '/' + pod['metadata']['name'])
    elif item['kind'] == "Endpoints":
        continue
    else:
        logging.error("unknown item type \"" + item['kind'] + "\"")

print("Processed " + str(podCount) + " pods - " +
      str(runningCount) + " running pods with " + 
      str(len(runningPods)) + " unique IPs")

#### test
# del runningPods['10.0.91.48']
# del runningPods['10.130.2.2']

#############################################################
# iterate through all endpoints, check that pod IPs are found
#############################################################
print("Checking service endpoints")
errorCount = 0
serviceCount = 0
endpointCount = 0
for item in data['items']:
    if 'kind' not in item:
        logging.error("item has no 'kind' attribute")
        continue

    if item['kind'] == "Endpoints":
        serviceCount += 1
        service = item
        logging.info("checking service " + service['metadata']['namespace'] + "/" + service['metadata']['name'])

        if 'subsets' not in service:
            logging.info("  skipping - no subsets - service: " + service['metadata']['namespace'] + "/" + service['metadata']['name'])
            continue

        for subset in service['subsets']:
            if 'addresses' not in subset:
                logging.warning("  skipping service with no addresses ready: " + service['metadata']['namespace'] + "/" + service['metadata']['name'])
                continue

            for address in subset['addresses']:
                endpointCount += 1
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

print("Checked " + str(endpointCount) + " endpoints on " + str(serviceCount) + " services - " + str(errorCount) + " missing IPs found")
