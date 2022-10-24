import math
import numpy as np
import matplotlib.pyplot as plt

def plot_all_pts(subset):
    f, (ax1, ax2) = plt.subplots(2, 4, figsize=(20, 10))
    fontsize = 10

    ax1[0].scatter(subset['esrgan_goes_img_039'], subset['landsat_img_039'])
    ax1[0].set_title('esrgan ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax1[1].scatter(subset['laplace_goes_img_039'], subset['landsat_img_039'])
    ax1[1].set_title('laplace ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax1[2].scatter(subset['unsharpmask_goes_img_039'], subset['landsat_img_039'])
    ax1[2].set_title('unsharpmask ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax1[3].scatter(subset['control_goes_img_039'], subset['landsat_img_039'])
    ax1[3].set_title('control ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax2[0].scatter(subset['esrgan_goes_img_103'], subset['landsat_img_103'])
    ax2[0].set_title('esrgan ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax2[1].scatter(subset['laplace_goes_img_103'], subset['landsat_img_103'])
    ax2[1].set_title('laplace ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax2[2].scatter(subset['unsharpmask_goes_img_103'], subset['landsat_img_103'])
    ax2[2].set_title('unsharpmask ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    ax2[3].scatter(subset['control_goes_img_103'], subset['landsat_img_103'])
    ax2[3].set_title('control ' + subset['loc'], fontsize = fontsize, fontweight ='bold')

    for n in range(4):
        ax1[n].set_xlabel('GOES', fontsize = fontsize)
        ax1[n].set_ylabel('Landsat', fontsize = fontsize)
        ax2[n].set_xlabel('GOES', fontsize = fontsize)
        ax2[n].set_ylabel('Landsat', fontsize = fontsize)
        ax1[n].set_xlim(280, 330)
        ax1[n].set_ylim(295, 330)
        ax2[n].set_xlim(280, 330)
        ax2[n].set_ylim(295, 330)
    
    return ax1, ax2

def plot_outer_pts(x_coords, y_coords, subset):
    m = (y_coords[1] - y_coords[0])/(x_coords[1] - x_coords[0])
    b = y_coords[1] - m*x_coords[1]
    
    masked_img_goes = subset['control_goes_img_039'].copy()
    masked_img_landsat = subset['landsat_img_039'].copy()
    
    mask = masked_img_landsat < m*masked_img_goes + b
    
    masked_img_goes[mask] = math.nan
    masked_img_landsat[mask] = math.nan
    
    f, (ax1, ax2) = plt.subplots(2, 2, figsize=(15, 10))
    
    imgs = [masked_img_goes, masked_img_landsat, subset['control_goes_img_039'], subset['landsat_img_039']]
    max_temp, min_temp = img_range(imgs)

    ax1[0].imshow(masked_img_goes, vmin = min_temp, vmax = max_temp)
    ax1[1].imshow(masked_img_landsat, vmin = min_temp, vmax = max_temp)
    ax2[0].imshow(subset['control_goes_img_039'], vmin = min_temp, vmax = max_temp)
    ax2[1].imshow(subset['landsat_img_039'], vmin = min_temp, vmax = max_temp)
    
    ax1[0].set_title('GOES 3.9 microns')
    ax1[1].set_title('Landsat 3.9 microns')
    ax2[0].set_title('GOES 3.9 microns')
    ax2[1].set_title('Landsat 3.9 microns')
    
    for n in range(2):
        ax1[n].axis('off')
        ax2[n].axis('off')

def img_range(imgs):
    maxi = 0
    mini = 1000
    
    for img in imgs:
        if img.max() > maxi:
            maxi = img.max()
        elif img.min() < mini:
            mini = img.min()
            
    return maxi, mini