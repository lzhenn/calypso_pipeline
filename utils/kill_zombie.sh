#!/bin/bash
INTERVAL=10
ps -u pathop | grep mpirun | awk '{print $1}' | xargs kill -9
sleep $INTERVAL;
ps -u pathop | grep python | awk '{print $1}' | xargs kill -9
sleep $INTERVAL;
