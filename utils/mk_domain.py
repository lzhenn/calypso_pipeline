#/usr/bin/env python3
"""
    Build domain utility
    Only for unnested grid, d01 domain
    ---------------
   
 """
import os, sys
import re
import numpy as np
import xarray as xr
from scipy import interpolate


# -----------Below for user specificed domain settings------------------------
template_name='test_dom'
#latS, latN, lonW, lonE = 21.483, 22.9848, 112.475, 114.977
#latS, latN, lonW, lonE = 21.7, 41.2, 116.4, 129.7
#latS, latN, lonW, lonE = 18.0, 28, 115, 123
latS, latN, lonW, lonE = 15.0, 35, 100.0, 120
# grid spatial resolution (roughly) in km
# landsea mask in 1km, thus >=1km is recommended
dx=10
# -----------Below for user specificed domain settings------------------------

# -----CONSTANTS------
CWD=sys.path[0]
# 1 deg distance (km) on equator
DEG_DIS=111.32
# lat lon margins from Gebco
MARGIN=dx/DEG_DIS+0.1


def interp2swan(var, swan_lat, swan_lon):
    """ 
    Linearly interpolate var from WRF grid onto SWAN grid 
    """
    print('Interpolate to SWAN grid...')

    res_var=var.lon[1]-var.lon[0]
    samp_spac=max(int(dx/(res_var*DEG_DIS))-1,1)
    # subset of GEBCO data
    var=var.isel(
        lon=slice(0, -1, samp_spac), 
        lat=slice(0, -1, samp_spac))
    
    lon2d_swan, lat2d_swan=np.meshgrid(swan_lon, swan_lat)
    lon2d_var, lat2d_var=np.meshgrid(var.lon, var.lat)
    var_swan=interpolate.griddata((
        lon2d_var.flatten(), lat2d_var.flatten()), 
        var.values.flatten(), 
        (lon2d_swan, lat2d_swan), method='nearest')
    var_swan=xr.DataArray(
        var_swan, 
        coords={'lon': swan_lon, 'lat': swan_lat}, dims=['lat', 'lon'])
    lat2d_swan=xr.DataArray(lat2d_swan, dims=['lat','lon'])
    lon2d_swan=xr.DataArray(lon2d_swan, dims=['lat','lon'])
    return var_swan, lat2d_swan, lon2d_swan
def main_run():
    '''
        read gebco bathy and interpolate
    '''
    print('Read Gebco bathy...')
    ds_bathy=xr.open_dataset(CWD+'/../domaindb/gebco.nc4')
    gebco_ele=ds_bathy['elevation'].sel(
        lat=slice(latS-MARGIN, latN+MARGIN), 
        lon=slice(lonW-MARGIN, lonE+MARGIN))
    
    print('Read USGS landmask...')
    ds_landmask=xr.open_dataset(CWD+'/../domaindb/usgs.nc4')
    usgs_mask=ds_landmask['mask'].sel(
        lat=slice(latS-MARGIN, latN+MARGIN), 
        lon=slice(lonW-MARGIN, lonE+MARGIN))

    # interpolate to SWAN grid
    ngrdx, ngrdy=int((lonE-lonW)/(dx/DEG_DIS)), int((latN-latS)/(dx/DEG_DIS))
    swan_lon=xr.DataArray(np.linspace(lonW, lonE, ngrdx), dims=['lon'])
    swan_lat=xr.DataArray(np.linspace(latS, latN, ngrdy), dims=['lat'])
    swan_ele, lat2d, lon2d=interp2swan(gebco_ele, swan_lat, swan_lon)
    swan_mask, lat2d, lon2d=interp2swan(usgs_mask, swan_lat, swan_lon)
    
    # match SWAN pos/neg
    swan_ele=-swan_ele
    swan_mask=1-swan_mask
    # minimum depth: 1-m
    swan_ele=xr.where(swan_ele<=0, 1, swan_ele)
    ds_swan=xr.Dataset(
        {
            'h': swan_ele, 
            'lat_rho': lat2d, 
            'lon_rho': lon2d,
            'mask_rho': swan_mask
        })
    
    # output
    domdb_path=CWD+'/../domaindb/'+template_name 
    if not(os.path.exists(domdb_path)):
        os.mkdir(domdb_path)

    # netcdf
    ds_swan.to_netcdf(domdb_path+'/swan_d01.nc')
    
    # cordinate file
    with open(domdb_path+'/swan_coord_d01.grd', 'w') as f:
        np.savetxt(f, lon2d.values, fmt='%12.6f', delimiter='\n')
        np.savetxt(f, lat2d.values, fmt='%12.6f', delimiter='\n')
    # bathy file
    swan_ele=xr.where(swan_mask==0, 9999.0, swan_ele)
    with open(domdb_path+'/swan_bathy_d01.bot', 'w') as f:
        np.savetxt(f, swan_ele.values, fmt='%13.8f', delimiter=' ')

    # db file
    db_path=CWD+'/../db/'+template_name
    
    if not(os.path.exists(db_path)):
        os.mkdir(db_path)

    with open(CWD+'/../db/swan_d01.in.tmp', 'r') as sources:
        lines = sources.readlines()
    
    with open(db_path+'/swan_d01.in', 'w') as sources:
        for line in lines:
            # regexp pipeline
            line=re.sub('@NAME', template_name, line)
            line=re.sub('@NWEGRDS', str(ngrdx-1), line)
            line=re.sub('@NSNGRDS', str(ngrdy-1), line)
            sources.write(line)

if __name__=='__main__':
    main_run()