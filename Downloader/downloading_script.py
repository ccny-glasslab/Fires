#!/sharedData2/nshakoor/.conda/envs/wildfireenv3/bin/python

# -*- coding: utf-8 -*-
import datetime
import os
import xarray as xr
import metpy
import cartopy.crs as ccrs
from pyresample import geometry, grid
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import json
import re
import sys
import time
import subprocess
from subprocess import Popen, PIPE
from time import sleep

pc = ccrs.PlateCarree()
pc_extents = [-124.25, -114.25, 32.25, 42.25]
pc_params = pc.proj4_params
target_extents = [pc_extents[0],
                    pc_extents[2],
                    pc_extents[1],
                    pc_extents[3]]
target_rows = 500
target_cols = 500
shape = [target_rows, target_cols]

def main():
#     params = json.load('params.json')
    shape = [target_rows, target_cols]
    dates = [317, 330] #317-323 324-330
    day = dates[0]
    while day <= dates[1]:
        download_and_convert_files(day, day, '2018', '13')
        print(day)
        day += 1
        sleep(10)

def download_and_convert_files(jday_0, jday_f, year, band):
    for jday in range(jday_0, jday_f+1):
        for hour in range(24):
            if hour < 10:
                download_files(year, str(jday), '0' + str(hour), band)
            else:
                download_files(year, str(jday), str(hour), band)
            p1 = Popen(['cat', '../../GOES_Files/GCPurls.txt'], stdout=PIPE)
            p2 = Popen(['gsutil', '-m', 'cp', '-I', '../../GOES_Files/nc_files'], stdin=p1.stdout, stdout=PIPE)
            poll = p2.poll()
            p1.stdout.close()
            p2.communicate()
            if poll is None:
                sleep(5)
            convert_files()

def download_files(year, jday, utchr, band):
    """
    appends to file for using cat ../GCPurls.txt | gsutil cp -I ./
    downloads all files in a given hour
    band should be two digits
    all inputs are strings
    """
    open("../../GOES_Files/GCPurls.txt", "w").close()
    urls = open("../../GOES_Files/GCPurls.txt", "a")
    time_log = open("../../GOES_Files/time_log.txt", "a")
    prefix = 'gs://gcp-public-data-goes-17/ABI-L1b-RadC/'
    code = year + jday + utchr 
    urls.write(prefix + year + '/' + jday + '/' + utchr + '/' + 'OR_ABI-L1b-RadC-M*C' + band + '_G17_s' + code + '*.nc' + '\n')
    date = datetime.datetime.strptime(year[2:] + jday, '%y%j').date()
    date = date.strftime('%m/%d/%Y')
    time_log.write('\n' + date + ' UTC ' + utchr + ' band ' + band)
    urls.close()
    time_log.close()

def convert_files():
    convert_log = open("../../GOES_Files/convert_log.txt", "w")
    fail_log = open("../../GOES_Files/fail_log.txt", "w")
    for file in os.listdir('../../GOES_Files/nc_files/'):
        try:
            data = xr.open_dataset('../../GOES_Files/nc_files/' + file)
            dat = data.metpy.parse_cf('Rad')
            geos = dat.metpy.cartopy_crs
            rad = dat.data

            fk1 = float(data.metpy.parse_cf('planck_fk1'))
            fk2 = float(data.metpy.parse_cf('planck_fk2'))
            bc1 = float(data.metpy.parse_cf('planck_bc1'))
            bc2 = float(data.metpy.parse_cf('planck_bc2'))
            bt = (fk2/(xr.ufuncs.log(fk1/rad + 1)) - bc1)/bc2
            bt = np.asarray(bt)

            goes_params = geos.proj4_params

            source_area = geometry.AreaDefinition.from_cf(data)
            target_area = geometry.AreaDefinition.from_extent('CA', pc_params, shape, target_extents)

            result = grid.get_resampled_image(target_area, source_area, bt)
            np.save('../../GOES_Files/npy_files/' + file[:-3], result)
            data.close()
            os.remove('../../GOES_Files/nc_files/' + file)
            convert_log.write('\n' + file)

        except:
            fail_log.write('\n' + file)
    convert_log.close()
    fail_log.close()

if __name__ == '__main__':
    main()
