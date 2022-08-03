#!/usr/bin/env python3

import os, sys
import lib

CWD=sys.path[0]

# controller config handler
cfg=lib.cfgparser.read_cfg(CWD+'/conf/setup.ini')
 
SWAN_ROOT= cfg['CONST']['swan_root']
DMDB_ROOT = cfg['CONST']['domdb_root']

# set DOMDB_PATH below to link the geo_em data
WRFFC_PATH=cfg['CONST']['ust_wrffc_root']
for itm in ['domaindb','Calypso','wrf_fc']:
    try:
        os.remove(CWD+'/'+itm)
    except OSError:
        pass

os.system('ln -sf '+SWAN_ROOT+' ./Calypso')
os.system('ln -sf '+DMDB_ROOT+' ./domaindb')

if WRFFC_PATH.strip() != '':
    os.system('ln -sf '+WRFFC_PATH+' ./wrf_fc')

