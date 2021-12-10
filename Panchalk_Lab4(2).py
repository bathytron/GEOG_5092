#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import numpy as np
import matplotlib.pyplot as plt
import glob
import rasterio
from rasterio.plot import show, show_hist

files = glob.glob(r'C:\Users\Aaron\OneDrive - The University of Colorado Denver\5092\newlab4\data\*.tif')

#part 1
# organize data and remove suitable sites and slopes
rast_files = sorted(files)
rast_files.pop(1)
rast_files.pop(2)

# create list for raters
factors = []

def mean_window(rasterfiles):
    for raster in rasterfiles: 
        with rasterio.open(raster) as array:
            data = array.read(1)
            earray = np.zeros_like(data)
            for row in range(0, data.shape[0]):
                for col in range(0, data.shape[1]):
                    win = data[row: row + 11, col: col + 9]
                    earray[row, col]= win.sum()/99
            factors.append(earray)

            
# run function
mean_window(rast_files)


# In[2]:


# set criteria for each raster
area = np.where(factors[0] < 0.05,1,0)
slope = np.where(factors[1] < 15,1,0)
urban = np.where(factors[2] == 0,1,0)
water = np.where(factors[3] < 0.02,1,0)
wind = np.where(factors[4] > 8.5,1,0)


# booleans with the rasters
array_group = (area+slope+urban+water+wind)


fivearray = np.where(array_group == 5,1,0)

# part 1 product
fivearray.sum()


# In[3]:


# part 2
# make geotiff

with rasterio.open(r'C:\Users\Aaron\OneDrive - The University of Colorado Denver\5092\newlab4\data\slope.tif') as dataset:
    with rasterio.open (f'suit_areas.tif','w',
                driver = 'GTiff',
                height = fivearray.shape[0],
                width = fivearray.shape[1],
                count = 1,
                dtype = 'int8',
                crs = dataset.crs,
                transform = dataset.transform,
                nodata = 0) as out_raster:
        fivearray = fivearray.astype('int8')
        out_raster.write(fivearray, indexes = 1)


# In[4]:


# get the bounds of the tif and calculate centroid, and append earray and array

with rasterio.open('suit_areas.tif') as blob:
    cell_size = blob.transform[0]
    bounds = blob.bounds
    x_coords = np.arange(bounds[0] + cell_size/2, bounds[2], cell_size)
    y_coords = np.arange(bounds[1] + cell_size/2, bounds[3], cell_size)
    x, y = np.meshgrid(x_coords, y_coords)
    x.flatten().shape, y.flatten().shape
    suit_coords = np.c_[x.flatten(),y.flatten()]
    
# Ravel returns a flattened array of cells that are 0 or 1 and compares that with the xy coords of suit_coords  
    Rave = x.ravel()
    Boo = fivearray.reshape(Rave.shape)

# Multiply my boolean by cells and append any cells with a value of 1 to Boo_coords    
    Boo_coords =[]
    for i, e in zip(suit_coords, Boo):
        x = np.multiply(i[0],e)
        y = np.multiply(i[1],e)
        if x != 0 and y != 0: 
            Boo_coords.append([x,y])


# In[8]:


import pandas as pd
from scipy.spatial import cKDTree


trans_stats = pd.read_csv("transmission_stations.txt")
x_coord = trans_stats['X']
y_coord = trans_stats['Y']
stations = np.column_stack([x_coord, y_coord])

Boo_array = np.array(Boo_coords)
Stat_array = np.array(stations)

dist,indexes = cKDTree(Stat_array).query(Boo_array)


# In[9]:


Stat_array.shape


# In[10]:


# min and max distances
print('Max:', dist.max()/1000,'Min:', dist.min()/1000)


# In[ ]:




