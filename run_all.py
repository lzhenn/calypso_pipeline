#/usr/bin/env python3
'''
Date: Jun 11, 2022

Control the run_serial.py script to run in seperated integrations
prescribed by restart_frq in conf/config.runall.ini

Revision:
May 26, 2021 --- Initial
Oct 25, 2021 --- Fit S2S usage
Nov  1, 2021 --- build dispatcher
Feb 19, 2022 --- build for operational calypso 
Apr 19, 2022 --- build for ltm simulation
Jun 11, 2022 --- build for ltm simulation with seperated simulations
Jul 24, 2022 --- modified for packaging
Zhenning LI
'''
import os, sys, logging.config
from re import I
import datetime, time

import lib 
from utils import utils

CWD=sys.path[0]


def deal_ustwrf(strt_time, end_time, cfg):
    '''Deal with ust WRF path'''
    # spin-up hours for ust wrf
    MIN_SPIN_HR=24
    # maximum extraction hours for single serial ust wrf
    MAX_EPOCH=48
    
    if not(os.path.exists(CWD+'/wrflink')):
        os.mkdir(CWD+'/wrflink')
    else:
        os.system('rm -f '+CWD+'/wrflink/*')
    
    if not(os.path.exists(CWD+'/wrf_fc')):
        utils.throw_error('No wrf_fc folder found! Please use setup.py properly.')
        exit()
    # find initial run serial
    spinup_hours=MIN_SPIN_HR
    # try until find a proper initial serial
    while spinup_hours<=MAX_EPOCH:
        init_time=strt_time+datetime.timedelta(hours=-spinup_hours)
        ymdh=init_time.strftime('%Y%m%d%H')
        test_path=CWD+'/wrf_fc/%s/%s/%s' % (ymdh[0:4], ymdh[0:6] , ymdh)
        if os.path.exists(test_path):
            utils.write_log('Run all find nearest init path:'+test_path)
            link_path=test_path
            break
        spinup_hours+=6
    
    link_time=strt_time
    while link_time<=end_time:
        fn=link_path+'/wrfout_d0?_'+link_time.strftime('%Y-%m-%d_%H:00:00')
        os.system('ln -sf '+fn+' '+CWD+'/wrflink/')
        link_time+=datetime.timedelta(hours=1)
        # next init serial
        if (link_time-init_time).total_seconds()==(spinup_hours+MAX_EPOCH)*3600:
            init_time=link_time+datetime.timedelta(hours=-spinup_hours)
            ymdh=init_time.strftime('%Y%m%d%H')
            link_path=CWD+'/wrf_fc/%s/%s/%s' % (ymdh[0:4], ymdh[0:6] , ymdh)
            utils.write_log('update init path:'+link_path)
def main_run():     
    # logging manager
    logging.config.fileConfig('./conf/logging_config.ini')
    
    utils.write_log('Read Config...')
    
    # controller config handler
    cfg=lib.cfgparser.read_cfg('./conf/config.allrun.ini')

    # make boundary condition file
    if cfg['BOUNDARY'].getboolean('gen_bdy') == True:
        os.system('python3 '+CWD+'/mk_bdy.py')   
    
    full_strt_time=datetime.datetime.strptime(cfg['INPUT']['start_time'],'%Y%m%d%H')
    full_end_time=datetime.datetime.strptime(cfg['INPUT']['end_time'],'%Y%m%d%H')

    # link ust wrfout
    if cfg['WIND']['wrfout_path']=='@PATH':
        deal_ustwrf(full_strt_time, full_end_time, cfg) 
    # in hours
    restart_frq=int(cfg['CORE']['restart_frq'])
    if restart_frq>=(full_end_time-full_strt_time).total_seconds()/3600:
        restart_frq=(full_end_time-full_strt_time).total_seconds()/3600
    curr_time=full_strt_time
    while (curr_time<full_end_time):
        sep_start_time=curr_time
        sep_end_time=curr_time+datetime.timedelta(hours=restart_frq)
        utils.write_log('Run Calypso from %s to %s with segrun from %s to %s' 
            % (
                full_strt_time.strftime('%Y%m%d%H'), full_end_time.strftime('%Y%m%d%H'), 
                sep_start_time.strftime('%Y%m%d%H'), sep_end_time.strftime('%Y%m%d%H')))
    
        cfg['INPUT']['start_time']=sep_start_time.strftime('%Y%m%d%H')
        cfg['INPUT']['end_time']=sep_end_time.strftime('%Y%m%d%H')
        if (curr_time>full_strt_time):
            cfg['CORE']['init_run']='0'

        lib.cfgparser.write_cfg(cfg, './conf/config.ini')
        os.system('python3 '+CWD+'/run_serial.py ')
        curr_time=sep_end_time


# ---------------------END OF MAIN---------------------



if __name__=='__main__':
    main_run()
