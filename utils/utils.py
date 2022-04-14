#/usr/bin/env python
"""Commonly used utilities

    Function    
    ---------------
   
    throw_error(source, msg):
        Throw error with call source and error message

"""
import datetime
import os
import numpy as np
import pandas as pd
from scipy import interpolate
import netCDF4 as nc4
import wrf

import logging, logging.config

def throw_error(source, msg):
    '''
    throw error and exit
    '''
    logging.error(source+msg)
    exit()

def write_log(msg, lvl=20):
    '''
    write logging log to log file
    level code:
        CRITICAL    50
        ERROR   40
        WARNING 30
        INFO    20
        DEBUG   10
        NOTSET  0
    '''

    logging.log(lvl, msg)

def get_wrf_file(tgt_time, wrf_dir, wrf_domain):
    '''
    return aimed wrf file name given tgt_time and wrf_domain
    '''
    dirlst=(os.listdir(wrf_dir))
    wrfout_lst=[itm for itm in dirlst if wrf_domain in itm]
    
    time_stamps=[
            datetime.datetime.strptime(itm[11:],'%Y-%m-%d_%H:%M:%S')
            for itm in wrfout_lst]

    # try if single frame
    wrf_hdl=nc4.Dataset(wrf_dir+wrfout_lst[0])
    wrf_time=wrf.extract_times(
            wrf_hdl,timeidx=wrf.ALL_TIMES, do_xtime=False)
    if len(wrf_time)>1: 
        for itime, ifile in zip(time_stamps, wrfout_lst):
            if tgt_time >=itime:
                return ifile
    else:
        for itime, ifile in zip(time_stamps, wrfout_lst):
            if tgt_time ==itime:
                return ifile


def interp_wrf2swan(wrf_var, swan_lat, swan_lon):
    """ 
    Linearly interpolate var from WRF grid onto SWAN grid 
    """
    
    x_org=wrf_var.XLAT.values.flatten()
    y_org=wrf_var.XLONG.values.flatten()
    
    interp=interpolate.LinearNDInterpolator(list(zip(x_org, y_org)), wrf_var.values.flatten())
    #interp=interpolate.NearestNDInterpolator(list(zip(x_org, y_org)), wrf_var.values.flatten())
    template = interp(swan_lat.values, swan_lon.values)
    return template 


