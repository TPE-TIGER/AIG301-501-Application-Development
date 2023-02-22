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

COPY ./requirements.txt /app/
COPY ./*.py /app/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y build-essential libssl-dev libffi-dev cargo \
    && pip3 install --upgrade pip --no-cache-dir \
    && pip3 install -r requirements.txt --no-cache-dir \
    && apt-get remove -y build-essential libssl-dev libffi-dev cargo \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "-u", "/app/module.py"]
