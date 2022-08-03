#/usr/bin/env python3
'''
Date: May 26, 2021

Automatic SWAN controller for consecutive runs.
Convert WRFOUT UV10 to SWAN needed file

Revision:
May 26, 2021 --- Initial
Oct 25, 2021 --- Fit S2S usage
Nov  1, 2021 --- build dispatcher
Feb 19, 2022 --- build for operational calypso 
Apr 19, 2022 --- build for ltm simulation
Jul 24, 2022 --- modified for packaging
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
    cfg_hdl=lib.cfgparser.read_cfg('./conf/config.ini')
        
    # init dispatcher
    ctrler=lib.dispatcher.Dispatcher(cfg_hdl)
    
    # dispatch tasks
    ctrler.dispatch(cfg_hdl)
        
    # end if rewrite wind

    utils.write_log('Run Calypso...')
    
    proj_path=cfg_hdl['CORE']['calypso_path']+'/Projects/'+cfg_hdl['INPUT']['nml_temp']+'/'

    # deal with swan domains 
    dom_match=lib.cfgparser.get_varlist(cfg_hdl['INPUT']['swan_wrf_match'])
    ndom=int(cfg_hdl['INPUT']['swan_ndom'])
    for idom in range(ndom):
        dom_id=dom_match[idom].split(':')[0]
        args=ctrler.strt_time.strftime('%Y%m%d.%H')+' '
        args=args+ctrler.end_time.strftime('%Y%m%d.%H')+' '
        args=args+proj_path+' '
        args=args+cfg_hdl['CORE']['ntasks']+' '
        args=args+cfg_hdl['ARCHIVE']['arch_path']+' '
        args=args+cfg_hdl['INPUT']['nml_temp']+' '
        args=args+cfg_hdl['CORE']['init_run']+' '
        args=args+dom_id+' '
        print(args) 
                
        rst_lead=1
        strt_time=time.time()
        os.system('sh calypso_swan.sh '+ args)
        end_time=time.time()
    
    exit() # exit for analysis run
    while (end_time-strt_time<60):
        print('Runtime error detected, try resub with previous rst files...')
        rst_lead=rst_lead+1
        strt_time=time.time()
        os.system('sh '+CWD+'/calypso_swan.sh '+args+' '+str(rst_lead))
        end_time=time.time()
        
        if (rst_lead>5):
            print('Failed in maximum resub tests, exit...')
            exit()



# ---------------------END OF MAIN---------------------



if __name__=='__main__':
    main_run()
