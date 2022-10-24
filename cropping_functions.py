import matplotlib.pyplot as plt
import numpy as np
import os
import random
import cartopy.crs as ccrs
from pyresample import geometry, grid
import pyresample
import matplotlib.pyplot as plt
import datetime
import metpy
import datetime
import xarray as xr
from pyresample import geometry, grid
import cartopy.crs as ccrs
from sklearn.metrics import mean_squared_error
import math
from skimage.transform import resize
import tensorflow as tf
import tensorflow_hub as hub
from skimage.filters import laplace
from skimage.filters import unsharp_mask
import math

def shiftPixels(refimg, newimg_full, min_x, min_y, lats=None, lons=None):
    assert refimg.shape[0] <= newimg_full.shape[0]
    assert refimg.shape[1] <= newimg_full.shape[1]
    
    if lats != None or lons != None:
        newimg = newimg_full[lats[0]:lats[1], lons[0]:lons[1]]
    else:
        newimg = newimg_full.copy()
    
    nx = 0
    ny = 0
    
    while refimg.shape != newimg.shape:
        x_add = 0
        y_add = 0
        
        if refimg.shape[0] > newimg.shape[0]:
            x_add += 1
            nx += 1
        elif refimg.shape[0] < newimg.shape[0]:
            x_add -= 1
            nx += 1
        if refimg.shape[1] > newimg.shape[1]:
            y_add += 1
            ny += 1
        elif refimg.shape[1] < newimg.shape[1]:
            y_add -= 1
            ny += 1
        
        if lats != None or lons != None:
            newimg = newimg_full[lats[0]:lats[1] + nx, lons[0]:lons[1] + ny]
        else:
            newimg = newimg_full[:(newimg.shape[0] + x_add), :(newimg.shape[1] + y_add)]
    
    if lats != None or lons != None:
        lats[1] += x_add
        lons[1] += y_add

    if lats != None or lons != None:
        return newimg_full[lats[0]+min_x:lats[1]+min_x+1, lons[0]+min_y:lons[1]+min_y+1]
    return newimg_full[abs(min_x):(newimg.shape[0] + abs(min_x)), abs(min_y):(newimg.shape[1] + abs(min_y))]

def expand(refimg, newimg_full, min_x, min_y, lats, lons):
    newimg = newimg_full[lats[0]:lats[1], lons[0]:lons[1]]
    
    nx = 0
    ny = 0
    
    x_add = 0
    y_add = 0
    
    while refimg.shape != newimg.shape:
        x_add = 0
        y_add = 0
    
        if refimg.shape[0] > newimg.shape[0]:
            x_add += 1
            nx += 1
        elif refimg.shape[0] < newimg.shape[0]:
            x_add -= 1
            nx += 1
        if refimg.shape[1] > newimg.shape[1]:
            y_add += 1
            ny += 1
        elif refimg.shape[1] < newimg.shape[1]:
            y_add -= 1
            ny += 1
        newimg = newimg_full[lats[0]:lats[1] + nx, lons[0]:lons[1] + ny]

    lats[1] += x_add
    lons[1] += y_add
    
    result = newimg_full[lats[0]+min_x-1:lats[1]+min_x+2, lons[0]+min_y-1:lons[1]+min_y+2]
    
    if result.shape[0] % 2 != 0:
        result = result[:-1,:]
    if result.shape[1] % 2 != 0:
        result = result[:,:-1]

    return result