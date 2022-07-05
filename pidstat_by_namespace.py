#!/usr/bin/python3
import sys,re

def usage():
    print(sys.argv[0] + ": prints out sum of CPU use by namespace")
    print("  usage:\n")
    print("    " + sys.argv[0] + " docker_output_file pidstat_file\n")
    print(" docker_output_file: output of `docker ps -q | xargs docker inspect --format '{{.State.Pid}} {{.Name}} {{.Config.Labels.name}} {{index .Config.Labels \"io.kubernetes.pod.namespace\"}} {{index .Config.Labels \"io.kubernetes.pod.name\"}}")
    print(" pidstat_file: output of pidstat command (only the \"Average:\" section is examined")

if len(sys.argv) != 3:
    usage()
    exit(1)

pid_lookup = {}
with open(sys.argv[1], 'r') as docker:
    docker_lines = docker.readlines()
    docker_re = re.compile(r'^(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
    for line in docker_lines:
        parse = docker_re.search(line)
        if parse:
            pid, docker_name, image_name, namespace, pod_name = parse.groups()
            pid_lookup[pid] = [docker_name, image_name, namespace, pod_name]

namespace_totals = {}
with open(sys.argv[2], 'r') as pidstat:
    pidstat_lines = pidstat.readlines()
    pidstat_re = re.compile(r'^Average:\s+\d+\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+-\s+(\S+)')
    averages = False
    for line in pidstat_lines:
        if line[0:8] == "Average:":
            averages = True
        if averages:
            if line[0:8] != "Average:":
                break
            parse = pidstat_re.search(line)
            if parse:
                pid, usr_pct, sys_pct, guest_pct, cpu, command = parse.groups()
                if pid in pid_lookup:
                    namespace = pid_lookup[pid][2]
                else:
                    namespace = command + " (PID " + pid + ")"
                if namespace in namespace_totals:
                    namespace_totals[namespace] += float(cpu)
                else:
                    namespace_totals[namespace] = float(cpu)

for namespace in sorted(namespace_totals, key=namespace_totals.get, reverse=True):
    print(namespace, "\t", namespace_totals[namespace])