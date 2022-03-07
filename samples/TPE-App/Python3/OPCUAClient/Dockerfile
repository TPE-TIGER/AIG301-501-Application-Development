#----
FROM debian:stretch-slim as qemu
RUN apt-get update && apt-get install -y qemu-user-static

################################################################################
# ROOTFS
################################################################################
FROM arm32v7/debian:stretch-slim as rootfs
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip python3-setuptools python3-lxml \
    && rm -rf /var/lib/apt/lists/*

###############################################################################
# Server
##############################################################################
ENV APP opc_ua_client_sample
COPY ./app/ /${APP}/app/
COPY ./cfg /${APP}/cfg/
COPY ./requirements.txt /${APP}/
WORKDIR /${APP}
RUN pip3 install -r requirements.txt
RUN rm /usr/bin/qemu-arm-static ./requirements.txt

CMD ["./app/run.sh" ]
