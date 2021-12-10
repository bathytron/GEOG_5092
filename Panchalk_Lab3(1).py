#!/usr/bin/env python
# coding: utf-8

# In[4]:


#Lab 3
#panchalk
# modules
import geopandas as gpd
import pandas as pd
import fiona
from shapely.geometry import Point
import glob
import rasterio
from rasterstats import zonal_stats
import random
import numpy as np
from numpy.lib.arraysetops import intersect1d
import rasterio
from rasterio.plot import show

#point to direcotry
file_path = r'C:\Users\Aaron Panchalk\Documents\5092\Lab3\lab3.gpkg'
print(file_path)


huc8 = gpd.read_file(file_path, layer='wdbhuc8')
extent = huc8.bounds
data = fiona.listlayers(file_path)

watershed = []
Density = []
Numpoints = []

huc8 = gpd.read_file(file_path, layer = 'wdbhuc8')
huc12 = gpd.read_file(file_path, layer = 'wdbhuc12')
soil = gpd.read_file(file_path, layer = 'ssurgo_mapunits_lab3')
watershed.append(huc8)
watershed.append(huc12)
HUCid = watershed[6:8]

# build function to solve mean
def sample_mean(sample):
    return sample['aws0150'].mean()
random.seed(0)

#find the extent of both watersheds
for layer in watershed:
    samplepoints = {'point_id':[], 'geometry': []}
    for idx, row in layer.iterrows():
        extent = row['geometry'].bounds
        Density = (row.geometry.area) / 1000000
        rawpoints = (Density * 0.05)
        Numpoints = round(rawpoints)
        z = 0
        
        while z < Numpoints:
            x = random.uniform(extent[0], extent[2])
            y = random.uniform(extent[1], extent[3])
            point = Point(x,y)
            if point.within(row.geometry):
                ID = row[0][:8]
                samplepoints['geometry'].append(point)
                samplepoints['point_id'].append(ID)
                z += 1
                
# create geodatabase
    pointsDf = pd.DataFrame(samplepoints)
    gdf = gpd.GeoDataFrame(pointsDf, crs = huc8.crs)
    huc_points = gpd.overlay(gdf, soil, how = 'intersection')
    grouping = huc_points.groupby(by = 'point_id').mean()

# final
    print(grouping)
    print(sample_mean(grouping))


# In[ ]:




