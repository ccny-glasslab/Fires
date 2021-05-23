"""
Downloads GOES-17 .nc files from the California Camp Fire and converts them into 500x500 pixel .npy files
of California brightness temperatures, deleting the originals.
"""

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
    """
    Downloads GOES-17 files during the California Camp Fire from GCS in batches of one day, and converts them
    into .npy files. 
    """
    shape = [target_rows, target_cols]
    dates = [318, 318] #317-323 324-330
    day = dates[0]
#     while day <= dates[1]: CHANGE THIS
    download_and_convert_files(day, day, '2018', '14') #change band here
    day += 1

def download_and_convert_files(jday_0, jday_f, year, band):
    """
    Downloads all the files of the given GOES band from the given start julian day 
    to the end julian day, inclusive, in the given year. 
    
    Parameter jday_0: first julian day to download files from
    Precondition: jday_0 is an int of a valid julian day in the given year, which is never over 366
    
    Parameter jday_f: last julian day to download files from
    Precondition: jday_f is an int of a valid julian day in the given year, which is never over 366
    
    Parameter year: year to download files from
    Precondition: year is an int and a year that the GOES-17 satellite has recieved data from
    
    Parameter band: GOES band to download data from
    Precondition: band is an int between 1 and 16, inclusive
    """
    for jday in range(jday_0, jday_f+1):
#         for hour in range(24): CHANGE THIS
        hour = 0 #CHANGE THIS
        if hour < 10:
            download_files(year, str(jday), '0' + str(hour), band)
        else:
            download_files(year, str(jday), str(hour), band)
        p1 = Popen(['cat', 'test/GCPurls.txt'], stdout=PIPE) #../../GOES_Files/GCPurls.txt
        p2 = Popen(['gsutil', '-m', 'cp', '-I', 'test/nc_files'], stdin=p1.stdout, stdout=PIPE) #../../GOES_Files/nc_files
        poll = p2.poll()
        p1.stdout.close()
        p2.communicate()
        if poll is None:
            sleep(5)
        convert_files()

def download_files(year, jday, utchr, band):
    """
    Appends links for all files in a given hour on a given day in a given year to a text file 
    for using cat ../GCPurls.txt | gsutil cp -I ./ to download.
    
    Parameter year: year to download files from
    Precondition: year is a str and a year that the GOES-17 satellite has recieved data from
    
    Parameter jday: julian day to download files from
    Precondition: jday is a str of a valid julian day in the given year, which is never over 366
    
    Parameter band: GOES band to download data from
    Precondition: band is a two-digit str between 01 and 16, inclusive
    """
    open("test/GCPurls.txt", "w").close() #../../GOES_Files/GCPurls.txt
    urls = open("test/GCPurls.txt", "a") #../../GOES_Files/GCPurls.txt
    time_log = open("test/time_log.txt", "a") #../../GOES_Files/time_log.txt
    prefix = 'gs://gcp-public-data-goes-17/ABI-L1b-RadC/'
    code = year + jday + utchr 
    urls.write(prefix + year + '/' + jday + '/' + utchr + '/' + 'OR_ABI-L1b-RadC-M*C' + band + '_G17_s' + code 
               + '*.nc' + '\n')
    date = datetime.datetime.strptime(year[2:] + jday, '%y%j').date()
    date = date.strftime('%m/%d/%Y')
    time_log.write('\n' + date + ' UTC ' + utchr + ' band ' + band)
    urls.close()
    time_log.close()

def convert_files():
    """
    Converts all files in a directory of .nc files into 500x500 .npy files of California brightness temperatures, 
    and deletes the originals. If the conversion fails, the file name is written to a log.
    """
    convert_log = open("test/convert_log.txt", "w") #../../GOES_Files/convert_log.txt
    fail_log = open("test/fail_log.txt", "w") #../../GOES_Files/fail_log.txt
    for file in os.listdir('test/nc_files/'): #../../GOES_Files/nc_files/
        try:
            data = xr.open_dataset('test/nc_files/' + file) #../../GOES_Files/convert_log.txt
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
            np.save('test/npy_files/' + file[:-3], result) #../../GOES_Files/npy_files/
            data.close()
            os.remove('test/nc_files/' + file) #../../GOES_Files/nc_files/
            convert_log.write('\n' + file)
        except:
            fail_log.write('\n' + file)
    convert_log.close()
    fail_log.close()

if __name__ == '__main__':
    main()
