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
[INPUT]
# In hours
cmip_frq=6

[OUTPUT]
output_prefix=CMIP6 
``` 
* `[INPUT]['input_root']` is the root directory of the CMIP6 data, here it points to the `./sample/` folder.

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

### run_serial.py
`run_serial.py` is the main script to run the SWAN integration in single serial. It takes in `conf/config.ini` to control the process.

### utils/gfs_wave_down_fcst_subdomain.sh
`gfs_wave_down_fcst_subdomain.sh` is a bash script to download the GFS wave forecast data using grib filter.

### utils/mk_domain.py
`mk_domain.py` is a utility script to generate the domain file for SWAN. You need to set the corresponding paras in the script for your usage.


**Any question, please contact Zhenning LI (zhenningli91@gmail.com)**

