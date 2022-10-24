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

def control_img(img):
    height, width = img.shape
    control = resize(img, (2*height, 2*width))
    return control

def laplace_sharpening_img(img):
    height, width = img.shape
    blurryimg = resize(img, (2*height, 2*width))
    laplace_edges = laplace(blurryimg)
    sharpimg = blurryimg + 0.8*laplace_edges
    return sharpimg

def unsharpmask_sharpening_img(img):
    height, width = img.shape
    blurryimg = resize(img, (2*height, 2*width))
    sharpimg = unsharp_mask(blurryimg/blurryimg.max(), radius=1, amount=1)*blurryimg.max()
    return sharpimg

def load_image(array):
    result = np.zeros((array.shape[0], array.shape[1], 3))
    result[:,:,0]= array
    result[:,:,1]= array
    result[:,:,2]= array
    return result

def preprocess_image(array):
    hr_image = array
    hr_size = (tf.convert_to_tensor(hr_image.shape[:-1]) // 2) * 2
    hr_image = tf.image.crop_to_bounding_box(hr_image, 0, 0, hr_size[0], hr_size[1])
    hr_image = tf.cast(hr_image, tf.float32)
    return tf.expand_dims(hr_image, 0)

def downscale_image(image):
    height, width = image.shape
    result = np.zeros((image.shape[0]//2, image.shape[1]//2, 3))
    smallimg = resize(image, (round(height/2), round(width/2)))
    result[:,:,0] = smallimg
    result[:,:,1] = smallimg
    result[:,:,2] = smallimg
    lr_image = tf.expand_dims(result, 0)
    lr_image = tf.cast(lr_image, tf.float32)
    return lr_image

def esrgan_sharpening_img(image):
    hr_image = preprocess_image(load_image(image))
    lr_image = downscale_image(image)
    
    fake_image = model(lr_image)
    fake_image = tf.squeeze(fake_image)
    
    hr_image = tf.squeeze(hr_image).numpy()
    lr_image = tf.squeeze(lr_image).numpy()
    return np.mean(fake_image, axis=2)