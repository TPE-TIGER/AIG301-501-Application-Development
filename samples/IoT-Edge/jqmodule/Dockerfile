#-------------------------------------------------------------------------------------------
# build stage
#-------------------------------------------------------------------------------------------
FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

#-------------------------------------------------------------------------------------------
# target stage
#-------------------------------------------------------------------------------------------
FROM arm32v7/python:3.7.11-slim-stretch
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin

RUN apt update \
    && apt install -y --no-install-recommends python3 python3-pip python3-setuptools flex bison libtool make automake autoconf \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/
COPY ./*.json /app/
COPY ./*.py /app/

WORKDIR /app

RUN pip3 install -r requirements.txt
RUN rm /usr/bin/qemu-arm-static

CMD ["python", "-u", "/app/module.py"]