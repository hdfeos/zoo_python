"""
This example code illustrates how to access and visualize a PO.DAAC SeaWinds
grid file in Python.

If you have any questions, suggestions, or comments on this example, please use
the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to see an
example of any other NASA HDF/HDF-EOS data product that is not listed in the
HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo), feel free to
contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).

Usage:  save this script and run

    python SW_S3E_rep_wind_speed_lvl0.py

The HDF file must either be in your current working directory or in a directory
specified by the environment variable HDFEOS_ZOO_DIR.

The netcdf library must be compiled with HDF4 support in order for this example
code to work.  Please see the README for details.

References
[1] ftp://podaac.jpl.nasa.gov/ocean_wind/seawinds/L3/doc/SWS_L3.pdf
"""

import os

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from netCDF4 import Dataset
import numpy as np

def run(FILE_NAME):

    nc = Dataset(FILE_NAME)

    # Identify the data field.
    DATAFIELD_NAME = 'rep_wind_speed'
    
    # Subset the data to match the size of the swath geolocation fields.
    # Turn off autoscaling, we'll handle that ourselves due to the existance
    # of the valid range attribute.
    var = nc.variables[DATAFIELD_NAME]
    var.set_auto_maskandscale(False)
    data = var[:,:,0]

    # Retrieve the needed attributes.  By inspection, the fill value is 0.
    fillvalue = 0
    scale = var.scale_factor
    offset = var.add_offset
    valid_range = var.valid_range

    invalid = np.logical_or(data < valid_range[0], data > valid_range[1])
    invalid = np.logical_or(invalid, data == fillvalue)
    data = data * scale + offset
    data[invalid] = np.nan
    datam = np.ma.masked_array(data, np.isnan(data))


    # Calculate lat and lon according to [1]
    latdim, londim = data.shape
    latinc = 180 / latdim
    loninc = 360 / londim
    y = np.linspace(-90 + latinc/2, 90 - latinc/2, latdim)
    x = np.linspace(0 + loninc/2, 360 - loninc/2, londim)
    longitude, latitude = np.meshgrid(x, y)
    
    # Draw a southern polar stereographic projection using the low resolution
    # coastline database.
    m = Basemap(projection='cyl', resolution='l',
                llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180)
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90, 91, 45))
    m.drawmeridians(np.arange(-180, 180, 45), labels=[True,False,False,True])
    m.pcolormesh(longitude, latitude, datam, latlon=True)
    m.colorbar()
    plt.title('{0} ({1})\n'.format(DATAFIELD_NAME, var.units))
    
    fig = plt.gcf()
    plt.show()
    
    basename = os.path.splitext(os.path.basename(FILE_NAME))[0]
    pngfile = basename + ".png"
    fig.savefig(pngfile)
    
if __name__ == "__main__":

    # If a certain environment variable is set, look there for the input
    # file, otherwise look in the current directory.
    hdffile = 'SW_S3E_2003100.20053531923.hdf'
    try:
        fname = os.path.join(os.environ['HDFEOS_ZOO_DIR'], hdffile)
    except KeyError:
        fname = hdffile

    run(fname)