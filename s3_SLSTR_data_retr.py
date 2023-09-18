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
    nc_coord = Dataset(p + '/geodetic_in.nc', 'r')
    nc_time = Dataset(p + '/time_in.nc', 'r')
    nc_tcwv = Dataset(p + '/LST_ancillary_ds.nc', 'r')
    # read the bands with the flags
    nc_lqsf = Dataset(p + '/flags_in.nc', 'r')
    nc_indices = Dataset(p + '/indices_in.nc', 'r')
    # print(nc_coord)
    # print("+++++++++++++++++++++++++++++++++++++++++")
    print(nc_time)
    # print("+++++++++++++++++++++++++++++++++++++++++")
    print(nc_indices)
    # print("+++++++++++++++++++++++++++++++++++++++++")
    # print(nc_lqsf)
    lat = nc_coord.variables['latitude_in'][:]
    # Python buffer object pointing to the start of the array’s data
    lat = lat.data
    lon = nc_coord.variables['longitude_in'][:]
    lon = lon.data
    time = nc_time.variables['time_stamp_i'][:] # time_stamp array contains just rows
    NADIR_FIRST_PIXEL = nc_time.variables['NADIR_FIRST_PIXEL_i'][:].data # time_stamp array contains just rows
    Nadir_first_scan_i = nc_time.variables['Nadir_First_scan_i'][:].data # time_stamp array contains just rows
    Nadir_Minimal_ts_i = nc_time.variables['Nadir_Minimal_ts_i'][:].data # time_stamp array contains just rows
    PIXSYNC_i = nc_time.variables['PIXSYNC_i'][:].data # time_stamp array contains just rowsc
    SCANSYNC_i = nc_time.variables['SCANSYNC'][:].data # time_stamp array contains just rowsc

    time = time.data

    pixel_in = nc_indices.variables['pixel_in'][:].data # time_stamp array contains just rowsc
    scan_in = nc_indices.variables['scan_in'][:].data # time_stamp array contains just rowsc
    # IWV band
    tcwv_var = 'TCWV'
    tcwv_band = nc_tcwv.variables[tcwv_var][:]
    # tcwv_orphan_var = 'TCWV_orphan'
    # tcwv_orphan_band = nc_tcwv.variables[tcwv_orphan_var][:]
    # # IWV_error band
    # iwv_err_var = 'IWV_err'
    # if iwv_err_var in nc_iwv.variables.keys():
    #     iwv_err_band = nc_iwv.variables[iwv_err_var][:]

    # # LQSF flags. Land flag is encoding with the number 4
    # # Land and cloud flags
    #lqsf_var = nc_lqsf.variables['LQSF']
    print(nc_lqsf.variables['bayes_in'])
    print(nc_lqsf.variables['cloud_in'])
    flags = nc_lqsf.variables['confidence_in']
    print(flags)
    print(nc_lqsf.variables['pointing_in'])
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
    print(f"lat {lat[target_x_y]}")
    print(f"lon {lon[target_x_y]}")
    # Create a list which contain a neighbour of pixels values around the center pixel
    # which covers an area of 9 Km (300m x 30 pixel = 9000 m) 
    pixels = []
    orphan_pixels =[]
    excluded_pixels = 0
    rows= len(flags)
    cols=len(flags[0])

    right = min(np.abs(cols-result[1][0]),16)
    left = min(result[0][0],15)
    up = min(result[1][0],15)
    down = min(np.abs(rows- result[0][0]),16)
    print(f'right {right}, left {left}, up {up}, down {down}')
    print(f"rows {rows}")
    print(f"x {result[0][0]}")
    print(f"cols {cols}")
    print(f"y {result[1][0]}")
    for i in range(-1*left, right):
        for j in range(-1*up, down):
            # Check if the current pixel in in Land clear sky value
            #print(flags[(result[0][0] + i, result[1][0] + j)])
            #if(flags[(result[0][0] + i, result[1][0] + j)] == 8):
            # print(f"{flags[(result[0][0] + j, result[1][0] + i)]} ", end='')
            # print(f"{tcwv_band[(result[0][0] + j, result[1][0] + i)]} ", end='')
            if (tcwv_band[(result[0][0] + j, result[1][0] + i)]!='--'):
                # store a clean land IWV value to the pixels list
                pixels.append(tcwv_band[(result[0][0] + j, result[1][0] + i)])
            else:
                excluded_pixels += 1
            # if (tcwv_orphan_band[(result[0][0] + j, result[1][0] + i)]!='--'):
            #     # store a clean land IWV value to the pixels list
            #     orphan_pixels.append(tcwv_orphan_band[(result[0][0] + j, result[1][0] + i)])
            # else:
            #     excluded_orphan_pixels += 1
        print('\n')
    # find the average
    print(len(pixels))
    
    if len(pixels) > 0:
        print(sum(pixels))
        iwv_avg = sum(pixels)/len(pixels) # avoid zeroDivisionError
    else:
        iwv_avg = '--'

    # if len(orphan_pixels) > 0:
    #     #print(sum(pixels))
    #     orphan_iwv_avg = sum(orphan_pixels)/len(orphan_pixels) # avoid zeroDivisionError
    # else:
    #     orphan_ivw_avg = '--'
    #  Percentage of excluded layers
    perc_excluded = (100 * excluded_pixels) / 961
    #print('Excluded: %d' % excluded_pixels) 
    print(perc_excluded)
    print(iwv_avg)
    # query your raw image band DataFrame using the matrix position instead of the geo position
    iwv_value = tcwv_band[target_x_y]
    # orphan_ivw_value =tcwv_orphan_band[target_x_y]
    print(iwv_value)
    # if iwv_err_var in nc_iwv.variables.keys():
    #     iwv_err_value = iwv_err_band[target_x_y]
    # else:
    #     iwv_err_value = '--'
    # detect the time for that specific row and convert from microseconds (10^(-6) sec) to date / time
    #time_stamp = time[target_x_y[0] - 1]  # because python array index start from 0 while sentinel rows from 1
    print(SCANSYNC_i)
    print(NADIR_FIRST_PIXEL)
    print(PIXSYNC_i[0])
    time_stamp=Nadir_Minimal_ts_i[target_x_y[0] - 1] + (scan_in[target_x_y] - Nadir_first_scan_i[target_x_y[0] - 1])*SCANSYNC_i[0] +(pixel_in[target_x_y] - NADIR_FIRST_PIXEL[0])*PIXSYNC_i[0]
    print(time_stamp)
    date = dt(2000, 1, 1, 0, 0 ,0) + timedelta(seconds=time_stamp/1e6)
    
    return(n + ', ' + elements[11] + ', ' + elements[12] + ', ' + str(date) + ', ' + str(target_x_y[0]) + ', '+ str(target_x_y[1]) + ', ' + str(target_lon) + ', ' + str(target_lat) + ', '  + str(iwv_value) + ', ' + str(iwv_avg)  +', '+str(perc_excluded)+','+ str(bin(flags[(result[0][0] , result[1][0] )])) ) 

# Create the csv file
f = open("C:/Users/thodoris/Documents/Python_Scripts/s3/s3/s3A_SLSTR_values_CDN_test_test.csv" , "a")
f.write("File, Cycle, Orbit, Date and Time, image x_cord, image y-cord, Longitude, Latitude, TCWV, TCWV_average, Excluded_pixels (%), target flag   \n")

for root, dirs, files in os.walk('C:/Users/thodoris/Documents/Python_Scripts/s3/s3/data1'):
    for name in dirs:
        # In this step we are in an netcdf image folder
        print(name)
        path = os.path.join(root, name)
        with open(r"C:\Users\thodoris\Documents\Python_Scripts\s3\s3\CDN1.txt", 'r') as f_loc:
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
