# Calypso_pipeline

Calypso_pipeline controls the pipeline actions of the SWAN system.

## Setup

### Installation
Please install python3 using Anaconda3 distribution. [Anaconda3](https://www.anaconda.com/products/individual) with python3.8 and 3.9 has been deeply tested, lower version of python3 may also work (without testing).

If you wish to feed in `grib2` data, Please first install [ecCodes](https://confluence.ecmwf.int/display/ECC/ecCodes+Home).

We recommend to create a new environment in Anaconda and install the `requirements.txt`:

```bash
conda create -n swan python=3.9
conda activate swan
pip install -r requirements.txt
```

After installing dependencies, you need to edit `conf/setup.ini` according to your environment to setup static data and other parameters.

## Usage

### Modify config.ini

When you properly setup the pipeline, first edit the `./conf/config.allrun.ini` file properly.

``` python
# This config file will be fed to the ctrl_seprun_calypso.py
# to rewrite the config.ini and control the ctrl_run_calypso.py

[INPUT]
nml_temp = test_dom 
# dswan:dwrf
swan_wrf_match = d01:d01
start_time = 2021080600
end_time = 2021080603

[WIND]
# flag for rewrite wind forcing file
rewrite_wind = True
# if use PATH system, please setup conf/setup.ini properly, and set wrfout_path=@PATH
wrfout_path = @PATH 

[BOUNDARY]
# flag for rewrite boundary forcing file
gen_bdy = True 
# how long distance for a segment (in deg, basically same as the global model grid spacing)
seg_len = 0.5
# ERA-5 and GFS grib data are supported, if eccodes and its python-binding are well installed.
# Support formatted start time in @ quotes and DOUBLE % such as: 
# @%%Y%%m%%d@,  @%%Y%%m%%d%%H@, etc. 
bdy_dir=/home/metctm1/array_hq86/data/era5_wave
#bdy_dir=/home/metctm1/array/data/gfs_wave/@%%Y%%m%%d%%H@

[CORE]
run_calypso = True
ntasks =16
# in hours
restart_frq = 24 
init_run = 1 

[ARCHIVE]
# yyyymmddhh will be automatically added to the end of the archive path
arch_path = /home/lzhenn/array74/Njord_Calypso/case_study/scs/
``` 


### Execute the pipeline
```bash
cd $CALYPSO_PIPELINE_HOME
python3 run_all.py
```

### run_all.py
By using `conf/conf.allrun.ini`, `run_all.py` will control the `run_serial.py` script to run in seperated SWAN integrations
prescribed by restart_frq in conf/config.allrun.ini

### mk_bdy.py
run_all.py will call `mk_bdy.py` to generate the boundary file for each integration.
**NOTE:** When you first time run the model after generating the specific domain configurations, this script will overwrite the `@BOUNDSPEC` in `./db/${DOMAIN}/swan_d01.in`. 
Occassionaly, you may need to tune the `[BOUNDARY][seg_len]` in `./conf/config.allrun.ini` manually. The default option should be equal to the boundary file resolution, for example, if the boundary file resolution is 0.25, the default option should be 0.25. If you encounter errors in `./Calypso/PRINT01-001` like the following:

```
 BOUNDSPEC SEGMENT XY 120.0000  16.2670 120.0000  16.2670 VARIABLE FILE 0 'swan_bdy.E.002.txt'
 point with location     120.0000     16.2670 is not active
 ** Error            : invalid boundary point
 segment point     120.00     16.27 grid   -99.00  -99.00 -98 -98 
 ** Error            : (  -99  -99) is outside computational grid    
 point with location     120.0000     16.2670 is not active
 ** Error            : invalid boundary point
 segment point     120.00     16.27 grid   -99.00  -99.00 -98 -98 
 ** Error            : (  -99  -99) is outside computational grid    
 ** Warning          : No points on the boundaries found
 ** Warning          : At least two points needed for a segment
 ** Warning          : Length of segment short, boundary values ignored
 segment length=     0.00; [len]=     0.00
```
**Please try a larger segment length.**

### run_serial.py
`run_serial.py` is the main script to run the SWAN integration in single serial. It takes in `conf/config.ini` to control the process.

### utils/gfs_wave_down_fcst_subdomain.sh
`gfs_wave_down_fcst_subdomain.sh` is a bash script to download the GFS wave forecast data using grib filter.

### utils/mk_domain.py
`mk_domain.py` is a utility script to generate the domain file for SWAN. You need to set the corresponding paras in the script for your usage.

**Any question, please contact Zhenning LI (zhenningli91@gmail.com)**

