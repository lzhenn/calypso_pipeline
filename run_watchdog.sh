#!/bin/sh
source ~/njord/bashrc_njord
cd /home/pathop/njord/workspace/calypso_pipeline/

# spin-up run if needed
python3 ./calypso_wrf_watchdog.py
