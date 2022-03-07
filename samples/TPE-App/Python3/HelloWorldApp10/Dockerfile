#----
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
ENV APP hello-app
COPY . /${APP}
WORKDIR /${APP}
RUN pip3 install -r requirements.txt
RUN rm /usr/bin/qemu-arm-static

CMD ["python3", "-u" , "./app/run.py" ]



