FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

################################################################################
# ROOTFS
################################################################################
FROM arm32v7/python:3.7.11-slim-stretch as rootfs
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/

###############################################################################
# Server
##############################################################################
ENV APP /aic

COPY . /${APP}
WORKDIR /${APP}

RUN pip3 install -r requirements.txt
RUN rm /usr/bin/qemu-arm-static
WORKDIR /${APP}/src
CMD ["/bin/bash", "./run.sh" ]
