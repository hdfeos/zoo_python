"""
This example code illustrates how to access and visualize an NSIDC AMSR grid
file in Python.

If you have any questions, suggestions, or comments on this example, please use
the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to see an
example of any other NASA HDF/HDF-EOS data product that is not listed in the
HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo), feel free to
contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).

Usage:  save this script and run

    python AMSR_E_L3_DL_A_TB36_5H_Res_1.py

The HDF file must either be in your current working directory or in a directory
specified by the environment variable HDFEOS_ZOO_DIR.
"""

import os
import re

import gdal
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import mpl_toolkits.basemap.pyproj as pyproj
import numpy as np

def run(FILE_NAME):
    
    # Identify the data field.
    GRID_NAME = 'Ascending_Land_Grid'
    DATAFIELD_NAME = 'A_TB36.5H (Res 1)'
    
    gname = 'HDF4_EOS:EOS_GRID:"{0}":{1}:{2}'.format(FILE_NAME,
                                                     GRID_NAME,
                                                     DATAFIELD_NAME)
    gdset = gdal.Open(gname)
    data = gdset.ReadAsArray().astype(np.float64)

    # Apply the attributes information.
    # Ref:  http://nsidc.org/data/docs/daac/ae_land3_l3_soil_moisture/data.html
    meta = gdset.GetMetadata()
    data[data == float(meta['_FillValue'])] = np.nan
    data *= 0.1
    data = np.ma.masked_array(data, np.isnan(data))

    # Construct the grid.  Reproject out of the global GCTP CEA into lat/lon.
    # Ref:  http://nsidc.org/data/atlas/epsg_3410.html
    meta = gdset.GetMetadata()
    x0, xinc, _, y0, _, yinc = gdset.GetGeoTransform()
    nx, ny = (gdset.RasterXSize, gdset.RasterYSize)
    x = np.linspace(x0, x0 + xinc*nx, nx)
    y = np.linspace(y0, y0 + yinc*ny, ny)
    xv, yv = np.meshgrid(x, y)
    args = ["+proj=cea",
            "+lat_0=0",
            "+lon_0=0",
            "+lat_ts=30",
            "+a=6371228",
            "+units=m"]
    pstereo = pyproj.Proj(' '.join(args))
    wgs84 = pyproj.Proj("+init=EPSG:4326") 
    lon, lat= pyproj.transform(pstereo, wgs84, xv, yv)

    m = Basemap(projection='cyl', resolution='l',
                llcrnrlat=-90, llcrnrlon=-180, urcrnrlat=90, urcrnrlon=180)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(-180, 181, 45), labels=[0, 0, 0, 1])
    m.pcolormesh(lon, lat, data, latlon=True)
    m.colorbar()
    titlestr = '{0} (Kelvin)'.format(DATAFIELD_NAME.replace('_', ' '))
    plt.title(titlestr)

    fig = plt.gcf()
    plt.show()
    
    basename = os.path.splitext(os.path.basename(FILE_NAME))[0]
    dfname = DATAFIELD_NAME.replace(' ','_').replace('(','_').replace(')','_')
    pngfile = "{0}.{1}.png".format(basename, dfname)
    fig.savefig(pngfile)

    del gdset


if __name__ == "__main__":

    # If a certain environment variable is set, look there for the input
    # file, otherwise look in the current directory.
    hdffile = 'AMSR_E_L3_DailyLand_V06_20050118.hdf'
    try:
        hdffile = os.path.join(os.environ['HDFEOS_ZOO_DIR'], hdffile)
    except KeyError:
        pass

    run(hdffile)
    