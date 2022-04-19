#/usr/bin/env python3
'''
This is a watchdog for wrfout files.
The watchdog will wait for the file to be generated.
If wrfout is generated, the watchdog will move the file to the archive folder.

Feb 19, 2022 --- build for operational calypso 
Feb 25, 2022 --- build for operational calypso on sugon 
Zhenning LI
'''
import os, sys, time
import datetime

import lib 
from utils import utils

CWD=sys.path[0]
def main_run():
     
    
    # controller config handler
    cfg_hdl=lib.cfgparser.read_cfg('./conf/fcst.resub.ini')
        
    if (cfg_hdl['INPUT']['model_init_ts']== 'realtime'):
        today = datetime.datetime.today()+datetime.timedelta(days=-1)
        init_ts = today.replace(hour=12)
    else:
        init_ts=datetime.datetime.strptime(
                cfg_hdl['INPUT']['model_init_ts'], '%Y%m%d%H')
    
    arch_path=cfg_hdl['ARCHIVE']['arch_root']+'/'+init_ts.strftime('%Y%m%d%H')
    if not os.path.exists(arch_path):
        os.makedirs(arch_path)

    total_dom=int(cfg_hdl['INPUT']['ndom'])
    dom_lb=['d0'+str(i) for i in range(1,total_dom+1)]
    run_days=int(cfg_hdl['INPUT']['run_days'])

    SLEEP=int(cfg_hdl['CORE']['req_interval'])
    round_nfiles=int(cfg_hdl['CORE']['round_nfiles'])
    move_flag=cfg_hdl['INPUT'].getboolean('move_flag')

    # for pure wrf
    watch_dir=cfg_hdl['INPUT']['watch_path']
    
    curr_ts=init_ts
    swan_strt_ts=init_ts
    file_count=0
    tic=time.time()
    print('WRFOUT Watchdog started at:', datetime.datetime.now())
    while (curr_ts<=init_ts+datetime.timedelta(days=run_days)):
        test_fn='wrfout_'+dom_lb[-1]+'_'+curr_ts.strftime('%Y-%m-%d_%H:00:00')
        if os.path.isfile(watch_dir+'/'+test_fn):
            print('%s found, wait to make sure writing completed...' % (test_fn))
            time.sleep(SLEEP) # wait for the file to be fully generated
            if move_flag:
                for dom in dom_lb:
                    fn='wrfout_'+dom+'_'+curr_ts.strftime('%Y-%m-%d_%H:00:00')
                    os.system('mv '+watch_dir+'/'+fn+' '+arch_path)
                    print('%s moved...' % (fn))
            file_count+=1
            curr_ts=curr_ts+datetime.timedelta(hours=1)
            tic=time.time()
        else:
            print('waiting for %s to be generated, %4ds passed...' % (
                test_fn, time.time()-tic))
            if time.time()-tic > 10800:
                print('maximum waiting time elapsed, exit...')
                exit()
            time.sleep(SLEEP)
            
        # call swan model
        if ((file_count>0) and (file_count % round_nfiles==0)):
            swan_cfg=lib.cfgparser.read_cfg('./conf/config.ini.smp')
            if move_flag:
                print('the %d round(s) wrfout moved to archive, run swan' % (file_count/round_nfiles))
                swan_cfg['INPUT']['wrfout_path']=arch_path
            else:
                print('the %d round(s) wrfout completed, run swan' % (file_count/round_nfiles))
                swan_cfg['INPUT']['wrfout_path']=watch_dir

            swan_cfg['INPUT']['start_time']=swan_strt_ts.strftime('%Y%m%d%H')
            swan_cfg['INPUT']['end_time']=curr_ts.strftime('%Y%m%d%H')
            swan_cfg['ARCHIVE']['arch_path']=arch_path
            if (file_count/round_nfiles==1 and cfg_hdl['CORE']['init_run']=='1'):
                swan_cfg['CORE']['init_run']='1'
            else:
                swan_cfg['CORE']['init_run']='0'
            swan_cfg['CORE']['ntasks']=cfg_hdl['CORE']['ntasks']

            lib.cfgparser.write_cfg(swan_cfg, './conf/config.ini')
            swan_strt_ts=curr_ts

            os.system('python3 '+CWD+'/ctrl_run_calypso.py')
            
    print('-----------------------ALL TASKS DONE!!!-----------------------')        

# ---------------------END OF MAIN---------------------


if __name__=='__main__':
    main_run()
