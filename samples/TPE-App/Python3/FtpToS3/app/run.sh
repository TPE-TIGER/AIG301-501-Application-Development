#!/bin/bash

if [ ! -f /app/cfg/config.json ]; then
    cp /app/default/config.json /app/cfg/config.json
fi

cron start
python -u web.py
