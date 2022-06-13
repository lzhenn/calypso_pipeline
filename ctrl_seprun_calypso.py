#/usr/bin/env python3
'''
Date: Jun 11, 2022

Control the ctrl_run_calypso.py script to run in seperated integrations.

Revision:
May 26, 2021 --- Initial
Oct 25, 2021 --- Fit S2S usage
Nov  1, 2021 --- build dispatcher
Feb 19, 2022 --- build for operational calypso 
Apr 19, 2022 --- build for ltm simulation
Jun 11, 2022 --- build for ltm simulation with seperated simulations
Zhenning LI
'''
import os, sys, logging.config
import datetime, time

import lib 
from utils import utils

CWD=sys.path[0]

def main_run():
     
    # logging manager
    logging.config.fileConfig('./conf/logging_config.ini')
    
    utils.write_log('Read Config...')
    
    # controller config handler
    cfg=lib.cfgparser.read_cfg('./conf/config.seprun.ini')

    full_strt_time=datetime.datetime.strptime(cfg['INPUT']['start_time'],'%Y%m%d%H')
    full_end_time=datetime.datetime.strptime(cfg['INPUT']['end_time'],'%Y%m%d%H')
    # in hours
    restart_frq=int(cfg['CORE']['restart_frq'])

    curr_time=full_strt_time
    while (curr_time<full_end_time):
        sep_start_time=curr_time
        sep_end_time=curr_time+datetime.timedelta(hours=restart_frq)
        utils.write_log('Run Calypso from %s to %s with segrun from %s to %s' 
            % (full_strt_time, full_end_time, sep_start_time, sep_end_time))
    
        cfg['INPUT']['start_time']=sep_start_time.strftime('%Y%m%d%H')
        cfg['INPUT']['end_time']=sep_end_time.strftime('%Y%m%d%H')
        if (curr_time>full_strt_time):
            cfg['CORE']['init_run']='0'

        lib.cfgparser.write_cfg(cfg, './conf/config.ini')
        os.system('python3 '+CWD+'/ctrl_run_calypso.py ')
        curr_time=sep_end_time


# ---------------------END OF MAIN---------------------



if __name__=='__main__':
    main_run()
