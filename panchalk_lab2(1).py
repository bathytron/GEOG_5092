#!/usr/bin/env python
# coding: utf-8

# In[26]:


#panchalk lab2
# modules

import geopandas as gpd
import pandas as pd
import fiona
from shapely.geometry import Point, LineString, Polygon
import glob
import rasterio
from rasterstats import zonal_stats


# In[27]:


# query 

Dict = []
Districts = {'num_coords':[], 'districts':[], 'poly':[]}

Main_List = glob.glob('*.txt*')
print(Main_List)

for Q in Main_List:
    H = pd.read_csv(Q, delim_whitespace=True)
    pairs=list(zip(H['X'],H['Y']))
    poly= Polygon(pairs)
    Districts['poly'].append(poly)
    Districts['num_coords'].append(len(pairs))
    Districts['districts'].append(Q[-6:-4])
    
    
print(Main_List)


# In[28]:


Districts['num_coords'][0]


# In[29]:


# part 2
# convert to shapefiles

Df = pd.DataFrame.from_dict(Districts)
Gdf = gpd.GeoDataFrame(Df, geometry='poly')
Gdf = Gdf.set_crs('epsg:4326')
Shapefile = Gdf.to_file('distshapefile.shp')


# In[30]:


AgLand = {'Dist':[1,5,6,1,5,6], 'year':[2004,2004,2004,2009,2009,2009], 'per_coverage':[]}
Ag_List = glob.glob('*.tif')

for Ag in Ag_List:
    Stats = pd.DataFrame(zonal_stats('distshapefile.shp', Ag, stats = ['count', 'sum']))
    Count = list(Stats['count'])
    Sum = list(Stats['sum'])
    AgPer = ([i / j for i, j in zip(Sum, Count)])
    print(AgPer)
    for percentage in AgPer:
        AgLand['per_coverage'].append(percentage*100)


# In[31]:


Df2 = pd.DataFrame.from_dict(AgLand)


# In[32]:


Df2

