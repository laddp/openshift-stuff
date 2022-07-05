FROM registry.access.redhat.com/ubi8/php-74:latest
USER 0
ADD show_host_info.php /tmp/src/index.php
RUN chown -R 1001:0 /tmp/src
USER 1001

# Install the dependencies
RUN /usr/libexec/s2i/assemble

# Set the default command for the resulting image
CMD /usr/libexec/s2i/run