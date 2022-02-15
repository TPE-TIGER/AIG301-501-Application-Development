#----
FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

################################################################################
# ROOTFS
################################################################################
FROM arm32v7/python:3.7.11-slim-stretch as rootfs
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/
RUN apt update \
    && apt install -y --no-install-recommends python3 python3-pip python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

###############################################################################
# Server
##############################################################################
ENV APP hello-app
COPY . /${APP}
WORKDIR /${APP}
RUN pip3 install -r requirements.txt
RUN rm /usr/bin/qemu-arm-static
WORKDIR /${APP}/app
CMD ["/bin/bash", "./run.sh" ]