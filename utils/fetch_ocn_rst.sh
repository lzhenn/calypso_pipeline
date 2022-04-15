#!/bin/sh
# Start time 
STRT_YMDH=$1
#STRT_YMDH=2022033012

# Current time for archive
CURR_YMDH=$2
#CURR_YMDH=2022033112

# RUN dir
RUNDIR=$3
#RUNDIR=/home/pathop/njord/COAWST_Njord_v35

# Archive path root
ARCH_ROOT=$4
#ARCH_ROOT=/home/pathop/njord/data/restart/njord/

ARCH_PATH=${ARCH_ROOT}/I${STRT_YMDH}R${CURR_YMDH}

echo "fetch previous day init" $ARCH_PATH

cp  $ARCH_PATH/* $RUNDIR/spunup_restart/
