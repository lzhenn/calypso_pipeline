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
    return 'wrfout_'+wrf_domain+'_'+tgt_time.strftime('%Y-%m-%d_%H:00:00')
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


