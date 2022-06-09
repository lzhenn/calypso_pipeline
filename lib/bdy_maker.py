#/usr/bin/env python3
"""
    Build boundary maker to generate boundary file for SWAN 

    Class       
    ---------------
                bdy_maker
"""

import datetime
import sys

import numpy as np
import pandas as pd
import xarray as xr
from utils import utils

print_prefix='lib.bdy_maker>>'

CWD=sys.path[0]

class BdyMaker:

    '''
    Construct bdymaker to generate boundary file for SWAN 

    '''
    
    def __init__(self, cfg_hdl):
        """ construct dispatcher obj """

        utils.write_log(print_prefix+'Construct boundary maker...')
        self.strt_time=datetime.datetime.strptime(cfg_hdl['INPUT']['start_time'],'%Y%m%d%H')
        self.end_time=datetime.datetime.strptime(cfg_hdl['INPUT']['end_time'],'%Y%m%d%H')
        self.max_seglen=int(cfg_hdl['BOUNDARY']['seg_len'])
        self.fprefix=cfg_hdl['BOUNDARY']['bdy_prefix']
        self.bdy_dir=cfg_hdl['BOUNDARY']['bdy_dir']
        self.out_dir=cfg_hdl['CORE']['calypso_path']
        self.bdy_time_delta=cfg_hdl['BOUNDARY']['bdy_time_delta']

        # load domain file
        self.load_domain(cfg_hdl)

        # build segs
        self.build_segs(cfg_hdl)
    
    
    
    def load_domain(self, cfg):
        """ load domain file """
        utils.write_log(print_prefix+'Load domain file...')
        ds_swan=xr.load_dataset(CWD+'/domaindb/'+cfg['INPUT']['nml_temp']+'/roms_d01.nc')
        self.lat2d=ds_swan['lat_rho'].values
        self.lon2d=ds_swan['lon_rho'].values
        self.mask=ds_swan['mask_rho'].values


    def build_segs(self, cfg):
        """ build_segs for SWAN """
        utils.write_log(print_prefix+'build segments...')
        self.segs=[]
        # uid for segs
        self.uid=0
        # 4 boundaries
        self.form_bdy('W', self.mask[:,0],
                      self.lat2d[:,0], self.lon2d[:,0])
        self.form_bdy('S', self.mask[0,1:],
                      self.lat2d[0,1:], self.lon2d[0,1:])

        self.form_bdy('E', self.mask[1:,-1],
                      self.lat2d[1:,-1], self.lon2d[1:,-1])
        self.form_bdy('N', self.mask[-1,1:-2],
                      self.lat2d[-1,1:-2], self.lon2d[-1,1:-2])
        
        for seg in self.segs:
            seg['file']=self.fprefix+'.%s.%03d.txt' % (seg['orient'], seg['id']) 
    
    def form_bdy(self, bdy_type, maskline, latline, lonline):
        """ form boundary accourding to maskline """
        find_flag=False
        uid=self.uid
        for i in range(maskline.shape[0]):
            if maskline[i] == 1:
                if not(find_flag):
                    find_flag=True
                    seg_dict={'id':uid, 'orient':bdy_type, 
                    'lat0':latline[i], 'lon0':lonline[i]}
                    uid=uid+1
                    seg_len=1
                else:
                    seg_len=seg_len+1
                    if seg_len==self.max_seglen:
                        seg_dict=close_seg(seg_dict, 
                            latline[i], lonline[i], seg_len)
                        self.segs.append(seg_dict)
                        seg_dict={}
                        find_flag=False
            # find land point
            else:
                # already in seg
                if find_flag:
                    if seg_len>int(0.25*self.max_seglen):
                        seg_dict=close_seg(seg_dict, 
                            latline[i-1], lonline[i-1], seg_len)
                        self.segs.append(seg_dict)
                        seg_dict={}
                    find_flag=False
            # last position
            if i==maskline.shape[0]-1:
                if find_flag:
                    seg_dict=close_seg(seg_dict,
                        latline[i], lonline[i], seg_len)
                    self.segs.append(seg_dict)
                    seg_dict={}

    def print_seg_cmd(self):
        """ print seg cmd for swan.in 
        """
        utils.write_log(print_prefix+'print seg cmd for swan.in...')
        for seg in self.segs:
            print('BOUNDSPEC SEGMENT XY %8.4f %8.4f %8.4f %8.4f VARIABLE FILE 0 \'%s\''
                % (seg['lat0'], seg['lon0'], seg['lat1'], seg['lon1'], seg['file']))
    
    def parse_seg_waves(self):
        """ parse seg cmd for swan.in 
        """
        utils.write_log(print_prefix+'parse seg waves from bdy files...')
        ts=pd.date_range(
            start=self.strt_time, end=self.end_time, 
            freq=self.bdy_time_delta+'min')

        len_ts=len(ts)

        for seg in self.segs:
            seg['sigh']=5*np.random.rand(len_ts)
            seg['period']=20*np.random.rand(len_ts)
            seg['dir']=5*np.random.rand(len_ts)+90
            seg['spread']=np.repeat(20, len_ts)
            data=np.array([seg['sigh'], seg['period'], seg['dir'], seg['spread']])
            seg['df'] = pd.DataFrame(data.T, index=ts, columns=['sigh', 'period', 'dir', 'spread'])
    
    def gen_seg_files(self):
        """ generate seg files """ 
        utils.write_log(print_prefix+'generate seg files...')
        
        for seg in self.segs:
            seg_file=open(self.out_dir+'/'+seg['file'],'w')
            #seg_file=open('test.csv','w')
            seg_file.write('TPAR\n')
            for tp in seg['df'].itertuples():
                seg_file.write('%s %8.2f %8.2f %8.2f %8.2f\n' 
                % (tp[0].strftime('%Y%m%d.%H%M'), tp[1], tp[2], tp[3], tp[4]))
            seg_file.close()

def close_seg(seg_dict, lat, lon, seg_len):
    """close a segment"""
    seg_dict['lat1']=lat
    seg_dict['lon1']=lon
    seg_dict['latm']=(seg_dict['lat0']+seg_dict['lat1'])/2
    seg_dict['lonm']=(seg_dict['lon0']+seg_dict['lon1'])/2
    seg_dict['len']=seg_len
    return seg_dict

