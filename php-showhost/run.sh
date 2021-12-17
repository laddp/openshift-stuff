#!/bin/bash
podman run --name ubi8-php-showhost --rm -p 8123:8080 localhost/ubi8-php-showhost:latest
