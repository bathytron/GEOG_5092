#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#panchalk lab5

import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import scipy
import glob

from rasterio.plot import show
from matplotlib import pyplot

from scipy.ndimage.measurements import standard_deviation
from lab5functions import reclassAspect, reclassByHisto, slopeAspect


files = glob.glob(r'C:\Users\Aaron\Documents\data\*.tif')
rast_files = sorted(files)

fire = glob.glob(r'C:\Users\Aaron\Documents\data\L5_big_elk\*.tif')
Fire_files = sorted(fire)

Elk = rasterio.open(rast_files[0])
bigelk = Elk.read(1)

slope, aspect = slopeAspect(bigelk,30)
reclass_aspect = reclassAspect(aspect)
reclass_slope = reclassByHisto(slope,10)

band3 = glob.glob(r'C:\Users\Aaron\Documents\data\L5_big_elk\*B3.tif')
B3 = sorted(band3)
band4 = glob.glob(r'C:\Users\Aaron\Documents\data\L5_big_elk\*B4.tif')
B4 = sorted(band4)

# reclassify fire perimeter raster as an array of 1 and 0

with rasterio.open(rast_files[1]) as raster:
    no_data = raster.nodata
    prim = raster.read(1)
    healthy = np.where(prim == 2,1,np.nan)
    fire = np.where(prim == 1,1,np.nan)
    

rr_list = []

# calculate ndvi

for x,y in zip(B3,B4):
    red = rasterio.open(x,'r').read(1)
    nir = rasterio.open(y,'r').read(1)
    NDVI = ((nir - red)/(nir + red))
    HealthNDVI = healthy * NDVI
    BurnNDVI = fire * NDVI
    mean_healthNDVI = np.nanmean(HealthNDVI)
    rr = BurnNDVI/ mean_healthNDVI
    rr_list.append(rr)
    meanrr = rr.mean()

# year array

year_list=[]

for year in range (2002, 2012):
    empty_array = np.zeros_like(rr_list[0])
    year_array = np.where (empty_array == 0, year, year)
    year_list.append(year_array)

master_year = np.vstack(year_list)
master_rr =np.vstack(rr_list)
master_rr[np.isnan(master_rr)] = 0

for rr in rr_list:
    rr[np.isnan(rr)]=0

master_year = master_year.flatten()
master_rr = master_rr.flatten()
trend_line =np.polyfit(master_year, master_rr, 1)
CoR = trend_line[0]

yr=2002

for rr in rr_list:
    print(f'Recovery Ratio for the year {yr}:', round(rr.mean(),3))
    yr += 1
print("---------------------------------------------------------------")
print(f'Coefficent of Recovery:', round(CoR,3))


# In[ ]:


# create function

def zonestatfun (valueras, zonerast, csv_name):
    uniquezones = np.unique(zonerast)
    dic = {'zones':[], 'mean':[], 'max':[], 'min':[], 'sd':[], 'count':[]}
    x = 1
    for zone in list(uniquezones):
        dic['zones'].append(x)
        boras = np.where(zonerast == x,1,np.nan)
        dic['mean'].append(np.nanmean(boras * valueras))
        dic['max'].append(np.nanmax(boras * valueras))
        dic['min'].append(np.nanmin(boras * valueras))
        dic['sd'].append(np.nanstd(boras * valueras))
        dic['count'].append(np.nansum(boras))
        x = x + 1 
                
    df = pd.DataFrame(dic)
    df.to_csv(csv_name)


# In[ ]:


ZoneSlope = zonestatfun(rr,reclass_slope,'zoneslope.csv')
ZoneAspect = zonestatfun(rr,reclass_aspect, 'zoneaspect.csv')


# In[ ]:


# create geotiff

with rasterio.open(r'C:\Users\Aaron\Documents\data\fire_perimeter.tif') as dataset:
    with rasterio.open (f'Recovery_Coefficent.tif','w',
            driver = 'Gtiff',
            height = rr.shape[0],
            width = rr.shape[1],
            count = 1,
            dtype = 'int8',
            crs = dataset.crs,
            transfrom = dataset.transform,
            nodata = 0
        )as out_raster:
        out_raster.write(rr,1)


# In[ ]:


# final print statement
print('When calculating zonal statistics for slope and aspect, as slope increases, recovery ratio decreases. Also, with a south-facing vantage point, there is a higher recovery ratio than when looking to the north.')


# In[ ]:




