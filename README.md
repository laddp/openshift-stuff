# openshift-stuff
Some openshift hacking bits

* **pidstat_by_namespace**: summarize CPU use by namespace from pidstat output
* **sleepy_pod**: Pod that sleeps for some time
* **sleepy_dc**: Deployment config that fails readiness checks on sleepy_pod  
* **test_echo_pod**: Pod that echos a ton of stuff to stdout - useful for stress testing logging
* **etcd_inventory.py**

    Examine the contents of your etcd database.  For OCP, recommended size is no more that 1GB -
    if your database approaches or exceeds that size, this tool will help locate
    large keys and high key counts.

    Runtime query mode assumes your environment is properly set up with
    `ETCDCTL_ENDPOINTS`, `ETCDCTL_CERT`, `ETCDCTL_CACERT`, `ETCDCTL_KEY` needed to
    run `etcdctl`.
    See https://access.redhat.com/articles/2542841 for details on how to set
    these for OCP.

    ```
    usage: etcd_inventory.py [-h] [--depth DEPTH] [--prefix PREFIX] [--filter FILTER] [input_file]

    Inventory an etcd instance and report count and size of all key/value pairs

    positional arguments:
    input_file       Use JSON formmated input file instead of querying etcd with
                     'etcdctl get --prefix '/' --write-out=json --dial-timeout=5m --command-timeout=5m`

    options:
    -h, --help       show this help message and exit
    --depth DEPTH    Maximum depth of results to report
    --prefix PREFIX  Report only on matching prefixes
    --filter FILTER  Report only on keys containing filter
    ```

    Sample output:

    ```
    # etcd_inventory.py etcd_contents.json
    {'/': {'count': 9110, 'depth': 0, 'size': 73174511},
     '/kubernetes.io/': {'count': 8534, 'depth': 1, 'size': 68968941},
     '/kubernetes.io/apiextensions.k8s.io/': {'count': 189,
                                              'depth': 2,
                                              'size': 4453545},
     '/kubernetes.io/apiextensions.k8s.io/customresourcedefinitions/': {'count': 189,
                                                                        'depth': 3,
                                                                        'size': 4453545},
     '/kubernetes.io/apiextensions.k8s.io/customresourcedefinitions/activemqartemisaddresses.broker.amq.io/': {'count': 1,
                                                                                                               'depth': 4,
                                                                                                               'size': 12333},
     '/kubernetes.io/apiextensions.k8s.io/customresourcedefinitions/activemqartemises.broker.amq.io/': {'count': 1,
                                                                                                       'depth': 4,
                                                                                                       'size': 99352},
    
    ...

     '/openshift.io/useridentities/': {'count': 1, 'depth': 2, 'size': 355},
     '/openshift.io/useridentities/quicklab_htpasswd:quicklab/': {'count': 1,
                                                                 'depth': 3,
                                                                 'size': 355},
     '/openshift.io/users/': {'count': 1, 'depth': 2, 'size': 236}}
    ```


* **check_service_endpoints.py**

    Search tool to check all OCP service backend IPs for pods that are not running.  This should not
    normally happen, but in some scenarios a unknown bug may cause this to happen.

    ```
    usage: check_service_endpoints.py [-h]
                    [--logLevel {INFO,CRITICAL,WARN,WARNING,ERROR,DEBUG,FATAL}]
                    [endpoints_file] [pods_file]

    Check service endpoints to ensure that all IPs are backed by running pods

    positional arguments:
    endpoints_file        Use YAML formatted input file instead of querying
                          `oc getendpoints --all-namespaces -o yaml`
    pods_file             Use YAML formatted input file instead of querying
                          `oc get pods --all-namespaces -o yaml`

    optional arguments:
    -h, --help            show this help message and exit
    --logLevel {INFO,CRITICAL,WARN,WARNING,ERROR,DEBUG,FATAL}
    ```

    Sample output:

    ```
    ./check_service_endpoints.py
    Gathering subprocess data
    Gathering pod data
    Processed 290 pods - 132 unique IPs running
    W:   skipping - no subsets - service cert-manager-operator/cert-manager-operator-controller-manager-metrics-service
    W:   skipping - no subsets - service openshift-machine-api/machine-api-controllers
    W:   skipping - no subsets - service openshift-machine-api/machine-api-operator-webhook
    Checked 93 services - 0 missing IPs found

    # check_service_endpoints.py endpoints.yaml pods.yaml
    Processed 81 pods - 39 unique IPs running
    E:   INVALID SERVICE IP found: Pod IP 10.130.2.2 from service default/docker-registry
    W:   skipping - no subsets - service glusterfs/gluster.org-glusterblock-glusterfs
    E:   INVALID SERVICE IP found: Pod IP 10.0.91.48 from service kube-system/kubelet
    E:   INVALID SERVICE IP found: Pod IP 10.0.91.48 from service openshift-monitoring/node-exporter
    Checked 24 services - 3 missing IPs found
    ```
