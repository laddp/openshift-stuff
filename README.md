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
