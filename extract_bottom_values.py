##!/Usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Oct 16 15:21:34 2018

@author: ryanheneghan
@author: Matthias Buechner (PIK)
"""

import numpy as np
import xarray as xr
import glob
import re
import os
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description='Extract ocean bottom fields')
parser.add_argument('-g', '--gcm', dest='gcm', action='store', required=True, help='CMIP6 model')
parser.add_argument('-e', '--experiment', dest='experiment', action='store', required=True, help='CMIP6 experiment')
parser.add_argument('-v', '--variable', dest='var', action='store', required=True, help='Variable')

options = parser.parse_args()

gcm = options.gcm
experiment = options.experiment
var = options.var

# base path to files
root = '/p/tmp/buechner/ISIMIP3b_ocean_remap'

all_files=glob.glob(root+'/'+gcm+'/'+experiment+'/'+var+'/*') # Pulls out all matching files
num_files=len(all_files) # How many files there are...

if num_files == 0:
    print('!!!  no files found for processing. exit')
    quit()

print(''   + gcm)
print(' '  + experiment)
print('  ' + var)

## For loop over all zall files with this variable
for i in range(0,num_files):

    curr_file=all_files[i] # Current file name
    print('   <= ' + curr_file)

    # Bits of the new name
    basename = os.path.basename(curr_file).replace(var, var+'-bottom')

    # New name
    out_path = root + '/' + gcm + '/' + experiment + '/' + var + '-bottom'
    new_name = out_path + '/' + basename
    Path(out_path).mkdir(parents=True, exist_ok=True)

    print('   => ' + new_name)

    CURR_NCFILE = xr.open_dataset(curr_file, decode_times=False) # Open current file

    # Extract lat, lon, time dimensions
    num_lat = len(CURR_NCFILE['lat'])
    num_lon = len(CURR_NCFILE['lon'])
    num_time = len(CURR_NCFILE['time'])

    print('    time steps: ', num_time)

    # Initialise storage
    VAR_bot = np.zeros((num_time, num_lat, num_lon))

    # loop over time
    for time in range(0,num_time):
        print('\r    current time step: ' + str(time + 1), end = '')
        VAR = CURR_NCFILE[var][time,:,:,:].values # pull out values for current time slice

        for j in range(0,num_lat): # loop over latitude
            for k in range(0,num_lon): # loop over longitude
                VAR_SPEC = VAR[:,j,k] # pull out lat, lon slice
                VAR_UNMASK = VAR_SPEC[~np.isnan(VAR_SPEC)] # pull out only unmasked values
                if len(VAR_UNMASK) == 0: # if there are no unmasked values
                    VAR_bot[time,j,k] = np.NAN # there are no values in this cell, so bottom is 'nan'
                    if len(VAR_UNMASK) > 0: # if there are unmasked values
                        VAR_bot[time,j,k] = VAR_UNMASK[len(VAR_UNMASK)-1] # the last one is the bottom

    print('')

    ##### Now, we want to construct the netcdf which will carry the bottom variable
    # Create temporary dataset 'ds', with time, long and lats from original netcdf we're working from
    ds = xr.Dataset({'time': CURR_NCFILE['time'], 'lon': CURR_NCFILE['lon'],'lat':CURR_NCFILE['lat']})
    # Put the bottom values in a dataarray 'da' with corresponding dimensions to 'ds'
    da = xr.DataArray(VAR_bot, dims = ['time','lat','lon'])
    # Put da in ds, under current var
    ds[var]=da

    # Fill in attributes of the variable, using info from the current netcdf we're using
    ds[var].attrs['long_name'] = CURR_NCFILE[var].long_name + ' on Bottom (z_b)'
    ds[var].attrs['standard_name'] = CURR_NCFILE[var].standard_name
    ds[var].attrs['units'] = CURR_NCFILE[var].units
    ds[var].attrs['comment'] = CURR_NCFILE[var].comment
    # backward rotated velocities (uo and vo) got an additional comment in variable meta data
    try:
        ds[var].attrs['comment_isimip'] = CURR_NCFILE[var].comment_isimip
    except:
        pass

    ## Fill in attributes of time, using info from the current netcdf we're using
    ds['time'].attrs['long_name'] = CURR_NCFILE['time'].long_name
    ds['time'].attrs['standard_name'] = CURR_NCFILE['time'].standard_name
    ds['time'].attrs['units'] = CURR_NCFILE['time'].units
    ds['time'].attrs['bounds'] = CURR_NCFILE['time'].bounds
    ds['time'].attrs['calendar'] = CURR_NCFILE['time'].calendar

    ## Fill in attributes of lat, using info from the current netcdf we're using
    ds['lat'].attrs['long_name'] = CURR_NCFILE['lat'].long_name
    ds['lat'].attrs['standard_name'] = CURR_NCFILE['lat'].standard_name
    ds['lat'].attrs['units'] = CURR_NCFILE['lat'].units
    ds['lat'].attrs['axis'] = CURR_NCFILE['lat'].axis

    ## Fill in attributes of lon, using info from the current netcdf we're using
    ds['lon'].attrs['long_name'] = CURR_NCFILE['lon'].long_name
    ds['lon'].attrs['standard_name'] = CURR_NCFILE['lon'].standard_name
    ds['lon'].attrs['units'] = CURR_NCFILE['lon'].units
    ds['lon'].attrs['axis'] = CURR_NCFILE['lon'].axis

    # Save ds to netcdf, with new name
    print('    write output...')
    ds.to_netcdf(new_name, format='NETCDF4_CLASSIC',encoding={var: {'dtype': 'float32', 'zlib': True, '_FillValue': 1e+20}})
