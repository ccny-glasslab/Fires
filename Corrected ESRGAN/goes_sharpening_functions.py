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

model = hub.load("https://tfhub.dev/captain-pool/esrgan-tf2/1")
random.seed(42)

maxi = 400
mini = 275

def control_sharpening_img(img):
    height, width = img.shape
    smallimg = resize(img, (round(height/2), round(width/2)))
    control = resize(smallimg, (height, width))
    return control

def laplace_sharpening_img(img):
    height, width = img.shape
    smallimg = resize(img, (round(height/2), round(width/2)))
    blurryimg = resize(smallimg, (height, width))
    laplace_edges = laplace(blurryimg)
    sharpimg = blurryimg + 0.8*laplace_edges
    return sharpimg

def unsharpmask_sharpening_img(img):
    height, width = img.shape
    smallimg = resize(img, (round(height/2), round(width/2)))
    blurryimg = resize(smallimg, (height, width))
    sharpimg = unsharp_mask(blurryimg/blurryimg.max(), radius=1, amount=1)*blurryimg.max()
    return sharpimg

def load_image(array):
    new_array = 255*((array - mini) / (maxi - mini))
    result = np.zeros((array.shape[0], array.shape[1], 3))
    result[:,:,0]= new_array
    result[:,:,1]= new_array
    result[:,:,2]= new_array
    return result

def preprocess_image(array):
    height, width, depth = array.shape
    result = np.zeros((array.shape[0]//2, array.shape[1]//2, 3))
    hr_image = result[:,:,:]
    smallimg = resize(array, (round(height/2), round(width/2), 3))
    hr_image = smallimg
    
    hr_size = tf.convert_to_tensor(hr_image.shape[:-1])
    hr_image = tf.image.crop_to_bounding_box(hr_image, 0, 0, hr_size[0], hr_size[1])
    hr_image = tf.cast(hr_image, tf.float32)
    return tf.expand_dims(hr_image, 0)

def esrgan_sharpening_img(image):
    hr_image = preprocess_image(load_image(image))    
    fake_image = model(hr_image)
    fake_image = tf.squeeze(fake_image)
    fake_image = (np.mean(fake_image, axis=2)/255)*(maxi - mini) + mini 
    return resize(fake_image, (image.shape[0], image.shape[1]))