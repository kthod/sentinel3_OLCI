# -*- coding: utf-8 -*-
import os
from netCDF4 import Dataset
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import sys

#pass_folder = sys.argv[1]

def retr(p, n, target_lat, target_lon):
    ''' return the needed values '''
 
    # split the file name and get the cycle and the trajectory of the specific image
    elements = n.split('_')
    cycle = elements[11]
    tr = elements[12]
    
    # Store the core variables
    nc_coord = Dataset(p + '/geo_coordinates.nc', 'r')
    nc_time = Dataset(p + '/time_coordinates.nc', 'r')
    nc_iwv = Dataset(p + '/iwv.nc', 'r')
    # read the bands with the flags
    nc_lqsf = Dataset(p + '/lqsf.nc', 'r')

    lat = nc_coord.variables['latitude'][:]
    # Python buffer object pointing to the start of the array’s data
    lat = lat.data
    lon = nc_coord.variables['longitude'][:]
    lon = lon.data
    time = nc_time.variables['time_stamp'][:] # time_stamp array contains just rows
    time = time.data

    # IWV band
    iwv_var = 'IWV'
    iwv_band = nc_iwv.variables[iwv_var][:]

    # IWV_error band
    iwv_err_var = 'IWV_err'
    if iwv_err_var in nc_iwv.variables.keys():
        iwv_err_band = nc_iwv.variables[iwv_err_var][:]

    # LQSF flags. Land flag is encoding with the number 4
    # Land and cloud flags
    lqsf_var = nc_lqsf.variables['LQSF']

    # lat and lon are x,y matrices, we will add another dimension z in order to stack them
    lat = lat[:, :, np.newaxis]
    # print lat.shape
    lon = lon[:, :, np.newaxis]
    # print lat.shape
    grid = np.concatenate([lat, lon], axis=2)
    vector = np.array([target_lat, target_lon]).reshape(1, 1, -1)
    subtraction = vector - grid

    # vector subtraction
    dist = np.linalg.norm(subtraction, axis=2) # it takes the norm in each row

    # query where in the 2D matrix is the closest point to your points of interest ?
    result =  np.where(dist == dist.min())

    # this is your lat/lon geo point translaated to a x, y position in the image matrix
    target_x_y = result[0][0], result[1][0]

    # Create a list which contain a neighbour of pixels values around the center pixel
    # which covers an area of 9 Km (300m x 30 pixel = 9000 m) 
    pixels = []
    excluded_pixels = 0

    for i in range(-15, 16):
        for j in range(-15, 16):
            # Check if the current pixel in in Land clear sky value
            if(lqsf_var[(result[0][0] + i, result[1][0] + j)] == 4):
                # store a clean land IWV value to the pixels list
                pixels.append(iwv_band[(result[0][0] + i, result[1][0] + j)])
            else:
                excluded_pixels += 1
    # find the average
    if len(pixels) > 0:
        iwv_avg = sum(pixels)/len(pixels) # avoid zeroDivisionError
    else:
        iwv_avg = '--'
    #  Percentage of excluded layers
    perc_excluded = (100 * excluded_pixels) / 961
    #print('Excluded: %d' % excluded_pixels) 
    print(perc_excluded)
    print(iwv_avg)
    # query your raw image band DataFrame using the matrix position instead of the geo position
    iwv_value = iwv_band[target_x_y]
    print(iwv_value)
    if iwv_err_var in nc_iwv.variables.keys():
        iwv_err_value = iwv_err_band[target_x_y]
    else:
        iwv_err_value = '--'
    # detect the time for that specific row and convert from microseconds (10^(-6) sec) to date / time
    time_stamp = time[target_x_y[0] - 1]  # because python array index start from 0 while sentinel rows from 1
    date = dt(2000, 1, 1, 0, 0 ,0) + timedelta(seconds=time_stamp/1e6)
    
    return(n + ', ' + elements[11] + ', ' + elements[12] + ', ' + str(date) + ', ' + str(target_x_y) + ', ' + str(target_lon) + ', ' + str(target_lat) + ', '  + str(iwv_value) + ', ' + str(iwv_avg) + ', ' + str(perc_excluded) + ', ' + str(iwv_err_value)) 

# Create the csv file
f = open("C:/Users/thodoris/Documents/Python_Scripts/s3/s3/s3A_values_orbit.csv" , "w")
f.write("File, Cycle, Orbit, Date and Time, image x_cord, image y-cord, Longitude, Latitude, IWV, IWV_average, Excluded_pixels (%), IWV error   \n")

for root, dirs, files in os.walk('C:/Users/thodoris/Documents/Python_Scripts/s3/s3/data'):
    for name in dirs:
        # In this step we are in an netcdf image folder
        print(name)
        path = os.path.join(root, name)
        with open(r"C:\Users\thodoris\Documents\Python_Scripts\s3\s3\locations2.txt", 'r') as f_loc:
            lines = f_loc.readlines()
            # split each line in pieces in order to store the coordinate values
            for i in lines:
                x = i.split()
                print(x)
                lat_deg = float(x[0])
                lat_m = float(x[1])
                lat_s = float(x[2])
                lon_deg = float(x[4])
                lon_m = float(x[5])
                lon_s = float(x[6])
                # calculate the decimal values
                lat =  float(lat_deg) + float(lat_m) / 60.0 + float(lat_s) / 3600.0
                lon =  float(lon_deg) + float(lon_m) / 60.0 + float(lon_s) / 3600.0
                # call the core function
                f.write(retr(path, name, lat, lon) + '\n')

f.close()
