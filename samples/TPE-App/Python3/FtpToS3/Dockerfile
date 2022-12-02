################################################################################
# QEMU
################################################################################
FROM debian:stretch-slim as qemu
RUN apt update && apt install -y qemu-user-static

################################################################################
# TARGET
################################################################################
FROM arm32v7/python:3.7.11-slim-stretch
COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin/

COPY ./requirements.txt /app/
COPY ./app/* /app/
COPY ./cfg/* /app/default/
COPY ./*.cron /tmp/

WORKDIR /app

RUN apt update && \
    apt install -y cron && \
    rm -rf /var/lib/apt/lists/*

RUN crontab /tmp/*.cron && \
    rm /tmp/*.cron && \
    pip3 install -r requirements.txt && \
    pip3 cache purge && \
    rm /usr/bin/qemu-arm-static

CMD ["./run.sh"]
