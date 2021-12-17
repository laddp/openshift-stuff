FROM registry.access.redhat.com/ubi8/php-74:latest
COPY show_host_info.php /opt/app-root/src/index.php
COPY myapp.conf /opt/app-root/etc/conf.d/myapp.conf
EXPOSE 8080
CMD ["/usr/sbin/httpd", "-DFOREGROUND"]