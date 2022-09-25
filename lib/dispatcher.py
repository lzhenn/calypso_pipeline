#/usr/bin/env python3
"""
    Build dispatcher to control the running flow

    Class       
    ---------------
                dispatcher
"""

import datetime
import os, sys

import netCDF4 as nc4
import wrf
import pandas as pd
import numpy as np
import xarray as xr
import lib.cfgparser
from utils import utils

print_prefix='lib.dispatcher>>'

CWD=sys.path[0]

class Dispatcher:

    '''
    Construct dispatcher to control the running flow

    Attributes
    -----------
    start_t:        datetime obj
        model start time

    end_t:          datetime obj
        model end time
    
    Methods
    -----------

    '''
    
    def __init__(self, cfg_hdl):
        """ construct dispatcher obj """

        utils.write_log(print_prefix+'Construct dispatcher...')
        self.strt_time=datetime.datetime.strptime(cfg_hdl['INPUT']['start_time'],'%Y%m%d%H')
        self.end_time=datetime.datetime.strptime(cfg_hdl['INPUT']['end_time'],'%Y%m%d%H')
        self.wind_time_delta=datetime.timedelta(minutes=60)
        #self.wind_time_delta=datetime.timedelta(minutes=int(cfg_hdl['WIND']['wind_time_delta']))
        self.proj_path=CWD+'/swan_lite/Projects/'+cfg_hdl['INPUT']['nml_temp']

        if not(os.path.exists(self.proj_path)):
            utils.write_log(print_prefix+'Project path does not exists, make it...')
            os.mkdir(self.proj_path)
    def dispatch(self, cfg):
        """ dispatch procedures to ran SWAN """
        utils.write_log(print_prefix+'Dispatch tasks...')
        strt_time=self.strt_time
        end_time=self.end_time

        if cfg['WIND'].getboolean('rewrite_wind'):
            self.interp_wind(strt_time, end_time, cfg)


    def interp_wind(self, wind_start_time, wind_stop_time, cfg):
        """ interpolate wind for SWAN """
        utils.write_log(print_prefix+'Interpolate wind for SWAN...')
        
        # active domains
        ndom=1
        #ndom=int(cfg['INPUT']['swan_ndom'])
        
        # WRF Parameters
        wrf_dir=cfg['WIND']['wrfout_path']
        if wrf_dir=='@PATH':
            wrf_dir=CWD+'/wrflink/'
        else:
            if not os.path.exists(wrf_dir):
                utils.throw_error('WRF output directory does not exist!')
        
        dom_match=lib.cfgparser.get_varlist(cfg['INPUT']['swan_wrf_match'])

        for idom in range(ndom):
            # SWAN domain file
            dom_id, wrf_domain=dom_match[idom].split(':')
            if cfg['INPUT'].getboolean('innermost') and idom ==0:
                continue
            dom_file=CWD+'/domaindb/'+cfg['INPUT']['nml_temp']+'/roms_'+dom_id+'.nc'
            if not(os.path.exists(dom_file)):
                dom_file=CWD+'/domaindb/'+cfg['INPUT']['nml_temp']+'/swan_'+dom_id+'.nc'
            ds_swan=xr.load_dataset(dom_file)

            lat_swan=ds_swan['lat_rho']
            lon_swan=ds_swan['lon_rho']
           
            # IF force file exists
            force_fn='swan_wind_'+dom_id+'.dat'
            #force_fn=cfg['WIND']['wind_prefix']+'_'+dom_id+'.dat'
            force_fn=self.proj_path+'/'+force_fn
            
            if os.path.exists(force_fn):
                utils.write_log('Delete existing wind file...%s' % force_fn, 30)
                os.remove(force_fn)
            
            curr_time=wind_start_time

            # iter timeframes 
            while curr_time < wind_stop_time:
                wrf_file=utils.get_wrf_file(curr_time, wrf_dir, wrf_domain)
                wrf_file=wrf_dir+wrf_file
                utils.write_log('Read '+wrf_file)
                
                utils.write_log(print_prefix+'Read WRFOUT surface wind...')
                wrf_hdl=nc4.Dataset(wrf_file)
                
                wrf_u10 = wrf.getvar(
                        wrf_hdl, 'U10', 
                        timeidx=wrf.ALL_TIMES, method="cat")
                wrf_v10 = wrf.getvar(
                        wrf_hdl, 'V10',
                        timeidx=wrf.ALL_TIMES, method="cat")
                wrf_time=wrf.extract_times(
                        wrf_hdl,timeidx=wrf.ALL_TIMES, do_xtime=False)
                wrf_hdl.close()

                # test if SWAN domain is within the WRF domain
                utils.write_log(
                    print_prefix+'lat_swan min:%7.4f; max:%7.4f' % (
                        lat_swan.values.min(), lat_swan.values.max()))
                utils.write_log(
                    print_prefix+'lat_wrf min:%7.4f; max:%7.4f' % (
                        wrf_u10.XLAT.values.min(), wrf_u10.XLAT.values.max()))
                utils.write_log(
                    print_prefix+'lon_swan min:%7.4f; max:%7.4f' % (
                        lon_swan.values.min(), lon_swan.values.max()))
                utils.write_log(
                    print_prefix+'lon_wrf min:%7.4f; max:%7.4f' % (
                        wrf_u10.XLONG.values.min(), wrf_u10.XLONG.values.max()))

                if not(utils.is_domain_within_wrf(lat_swan, lon_swan, wrf_u10)):
                    utils.throw_error('SWAN domain is not within the WRF domain!')
                
                wrf_time=[pd.to_datetime(itm) for itm in wrf_time]
                
                utils.write_log('Query Wind Timestamp:'+str(curr_time))
                u10_tmp=wrf_u10
                v10_tmp=wrf_v10

                utils.write_log('Interpolate U wind...')
                swan_u = utils.interp_wrf2swan(u10_tmp, lat_swan, lon_swan)
                utils.write_log('Interpolate V wind...')
                swan_v = utils.interp_wrf2swan(v10_tmp, lat_swan, lon_swan)
                
                if 'swan_uv' in locals():# already defined
                    swan_uv=np.concatenate((swan_uv, swan_u, swan_v), axis=0)
                else:
                    swan_uv=np.concatenate((swan_u, swan_v), axis=0)
                
                curr_time=curr_time+self.wind_time_delta
                
            # add one more time stamp to close up the file
            swan_uv=np.concatenate((swan_uv, swan_u, swan_v), axis=0)
                    
            utils.write_log('Output...')
            with open(force_fn, 'a') as f:
                np.savetxt(f, swan_uv, fmt='%7.2f', delimiter=' ')
                f.write('\n')
            del swan_uv 
