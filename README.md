# openshift-stuff
Some openshift hacking bits

* pidstat_by_namespace: summarize CPU use by namespace from pidstat output
* sleepy_pod: Pod that sleeps for some time
* sleepy_dc: Deployment config that fails readiness checks on sleepy_pod  
* test_echo_pod: Pod that echos a ton of stuff to stdout - useful for stress testing logging
* etcd_inventory.py
    ```
    usage: etcd_inventory.py [-h] [--depth DEPTH] [--prefix PREFIX] [--filter FILTER] [input_file]

    Inventory an etcd instance and report count and size of all key/value pairs

    positional arguments:
    input_file       Use JSON formmated input file instead of querying etcd

    options:
    -h, --help       show this help message and exit
    --depth DEPTH    Maximum depth of results to report
    --prefix PREFIX  Report only on matching prefixes
    --filter FILTER  Report only on keys containing filter
    ```
* check_service_endpoints.py
    ```
    usage: check_service_endpoints.py [-h] [--logLevel {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}] [endpoints_file] [pods_file]

    Check service endpoints to ensure that all IPs are backed by running pods

    positional arguments:
    endpoints_file        Use YAML formatted input file instead querying `oc get endpoints --all-namespaces -o yaml`
    pods_file             Use YAML formatted input file instead querying `oc get pods --all-namespaces -o yaml`

    options:
    -h, --help            show this help message and exit
    --logLevel {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
    ```