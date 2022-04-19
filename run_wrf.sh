#!/bin/sh

source ~/njord/bashrc_njord

CAL_DIR=/home/pathop/njord/workspace/calypso_pipeline/

# clean zombies
cd $CAL_DIR
sh ./utils/kill_zombie.sh
sleep 30

cd $CAL_DIR/wrf-top-driver
python3 top_driver.py
