#!/bin/bash

if [ ! -f /app/cfg/config.json ]; then
    mkdir -p /app/cfg
    cp ./cfg/config.json /app/cfg
fi
python3 -u ./app/run.py