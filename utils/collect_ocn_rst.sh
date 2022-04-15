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

if [ ! -d $ARCH_PATH ]; then
    mkdir $ARCH_PATH
fi

#cp $RUNDIR/njord_rst_d01.nc.org $ARCH_PATH
cp $RUNDIR/*.hot-* $ARCH_PATH

