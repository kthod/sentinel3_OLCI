# -*- coding: utf-8 -*-
import os
from netCDF4 import Dataset
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import sys
import statistics
#pass_folder = sys.argv[1]

def locate_target(target_lat, target_lon, lat, lon):
    """
    function to find the coordinates of the target station on the image grid
    """
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

    return target_x_y
def find_weights(target_lat,target_lon,lat,lon,target_x_y,tcwv):


    if np.abs(lon[target_x_y[0]][target_x_y[1]-1]-target_lon) < np.abs(lon[target_x_y[0]][target_x_y[1]+1]-target_lon):
        w1 = np.abs(lon[target_x_y[0]][target_x_y[1]-1]-target_lon)
        w2 = np.abs(lon[target_x_y[0]][target_x_y[1]]-target_lon)
        lon = target_x_y[1]-1
        print("left")
    else:    
        w1 = np.abs(lon[target_x_y[0]][target_x_y[1]+1]-target_lon)
        w2 = np.abs(lon[target_x_y[0]][target_x_y[1]]-target_lon)
        lon = target_x_y[1]+1
    
    
    w1_norm = w1/(w1+w2)
    w2_norm = w2/(w1+w2)
    print(tcwv[target_x_y[0]][lon])
    print(w1)
    print(tcwv[target_x_y[0]][target_x_y[1]])
    print(w2)
    wv = w2_norm*tcwv[target_x_y[0]][lon]+w1_norm*tcwv[target_x_y[0]][target_x_y[1]]

    return wv

def create_templates_around_target(cols,rows,target_x_y,s8_band,s9_band,flags):
    """
    function to create 10x10 template around target station
    """

    T11=[]
    T12=[]

    right = min(np.abs(cols-target_x_y[1]),8)
    left = min(target_x_y[0],8)
    up = min(target_x_y[1],5)
    down = min(np.abs(rows- target_x_y[0]),5)


    # print(f'right {right}, left {left}, up {up}, down {down}')
    # print(f"rows {rows}")
    # print(f"x {result[0][0]}")
    # print(f"cols {cols}")
    # print(f"y {result[1][0]}")
    excluded_pixels =0

    for i in range(-1*left, right):
        for j in range(-1*up, down):
            # Check if the current pixel in in Land clear sky value

            # print(f"{flags[(result[0][0] + j, result[1][0] + i)]} ", end='')
            # print(f"{tcwv_band[(result[0][0] + j, result[1][0] + i)]} ", end='')
            # if (s8_band[(result[0][0] + j, result[1][0] + i)]!='--'):
                # store a clean land IWV value to the pixels list
            binary_flag = int16_to_binary_str(flags[(target_x_y[0] + j, target_x_y[1] + i)])
            # print(binary_flag)
            # print(binary_flag[12])
            # print(binary_flag[1])
            if (binary_flag[12] =='1' and binary_flag[1]=='0'):
                
                T11.append(s8_band[(target_x_y[0] + j, target_x_y[1] + i)])
                T12.append(s9_band[(target_x_y[0] + j, target_x_y[1] + i)])
            else:
                excluded_pixels+=1
    T11_median =calculate_median_BT(T11)
    T12_median =calculate_median_BT(T12)
    #print(f"BISIAS {len(T11)}")

    poped_items=0
    for k in range(len(T11)):
        
            
        if (np.abs(T11[k-poped_items]-T11_median)<np.abs(T12[k-poped_items]-T12_median) or (T11[k-poped_items]-T11_median)*(T12[k-poped_items]-T12_median)<0):
             
            T11.pop(k-poped_items)
            T12.pop(k-poped_items)
            poped_items+=1
            excluded_pixels+=1
    return T11,T12,excluded_pixels

def calculate_median_BT(T):
    """
    function to calculate the mean brightness temperature for each template
    """
    # if len(T11) > 0:
    #     print(sum(T11))
    #     T11_mean = sum(T11)/len(T11) # avoid zeroDivisionError
    # else:
    #     T11_mean = '--'

    # if len(T12) > 0:
    #     print(sum(T12))
    #     T12_mean = sum(T12)/len(T12) # avoid zeroDivisionError
    # else:
    #     T12_mean = '--'
    if len(T)>0:
        T_median = statistics.median(T)
    else:
        T_median = 0
    return T_median

def calculate_product_R(Ti,Tj,Ti_median,Tj_median):
    cov =0
    var = 0
    for  i in range(len(Ti)):
        cov+=(Ti[i] - Ti_median)*(Tj[i] - Tj_median)
        var+=(Ti[i] - Ti_median)**2
    # query your raw image band DataFrame using the matrix position instead of the geo position
    # bt_value = bt_band[target_x_y]
    if(var>0):

        R = cov/var
    else:
        R =0  
    return R

def int16_to_binary_str(n):
    return format(n & 0xFFFF, '016b')  # & 0xFFFF to handle negative numbers

# Test


def retr(p, n, target_lat, target_lon):
    ''' return the needed values '''
 
    # split the file name and get the cycle and the trajectory of the specific image
    elements = n.split('_')
    cycle = elements[11]
    tr = elements[12]
    print(cycle)
     
    # Store the core variables
    nc_coord = Dataset(p + '/geodetic_in.nc', 'r')
    nc_coordtx = Dataset(p + '/geodetic_tx.nc', 'r')
    nc_time = Dataset(p + '/time_in.nc', 'r')
    nc_s8 = Dataset(p + '/S8_BT_in.nc', 'r')
    nc_s9 = Dataset(p + '/S9_BT_in.nc', 'r')
    nc_met = Dataset(p+ '/met_tx.nc', 'r')
    # nc_indicesn = Dataset(p + '/indices_in.nc', 'r')
    # nc_indiceso = Dataset(p + '/indices_io.nc', 'r')
    tcwv_ecmwf= nc_met.variables['total_column_water_vapour_tx'][:]
    # print(nc_s8)
    # print(len(nc_met.variables['total_column_water_vapour_tx'][:][0][0]))
    # nc_flagf = Dataset(p + '/flags_fn.nc', 'r')
    # print(nc_flagf)
    nc_flagi = Dataset(p + '/flags_in.nc', 'r')
    
    # print(nc_flagi)
    # print(nc_flagi.variables['confidence_in'])
    # print(len(nc_coord.variables['latitude_in'][:]))
    # print(len(nc_coord.variables['latitude_in'][:][0]))
    #print(nc_time)
    flags = nc_flagi.variables['confidence_in'][:]
    lat = nc_coord.variables['latitude_in'][:]
    lattx = nc_coordtx.variables['latitude_tx'][:]
    # Python buffer object pointing to the start of the array’s data
    lat = lat.data
    lon = nc_coord.variables['longitude_in'][:]
    lontx = nc_coordtx.variables['longitude_tx'][:]
    lon = lon.data
    time = nc_time.variables['time_stamp_i'][:] # time_stamp array contains just rows
    
    time = time.data
    # NADIR_FIRST_PIXEL = nc_time.variables['NADIR_FIRST_PIXEL_i'][:].data # time_stamp array contains just rows
    # Nadir_first_scan_i = nc_time.variables['Nadir_First_scan_i'][:].data # time_stamp array contains just rows
    # Nadir_Minimal_ts_i = nc_time.variables['Nadir_Minimal_ts_i'][:].data # time_stamp array contains just rows

    # OBLIQUE_FIRST_PIXEL = nc_time.variables['OBLIQUE_FIRST_PIXEL_i'][:].data # time_stamp array contains just rows
    # Oblique_first_scan_i = nc_time.variables['Oblique_First_scan_i'][:].data # time_stamp array contains just rows
    # Oblique_Minimal_ts_i = nc_time.variables['Oblique_Minimal_ts_i'][:].data # time_stamp array contains just rows
    # PIXSYNC_i = nc_time.variables['PIXSYNC_i'][:].data # time_stamp array contains just rowsc
    # SCANSYNC_i = nc_time.variables['SCANSYNC'][:].data # time_stamp array contains just rowsc

    time = time.data

    # pixel_in = nc_indicesn.variables['pixel_in'][:].data # time_stamp array contains just rowsc
    # scan_in = nc_indicesn.variables['scan_in'][:].data # time_stamp array contains just rowsc
    # pixel_io = nc_indiceso.variables['pixel_io'][:].data # time_stamp array contains just rowsc
    # scan_io = nc_indiceso.variables['scan_io'][:].data # time_stamp array contains just rowsc
    # BT band
    s8_band = nc_s8.variables['S8_BT_in'][:]
    s9_band = nc_s9.variables['S9_BT_in'][:]

    target_x_y = locate_target(target_lat,target_lon,lat, lon)
    target_x_ytx = locate_target(target_lat,target_lon,lattx,lontx)
    # Create a list which contain a neighbour of pixels values around the center pixel
   # which covers an area of 9 Km (300m x 30 pixel = 9000 m) 
    print(f"nadir {target_x_y}")
    print(f"tx {target_x_ytx}")
    rows= len(lat)
    cols=len(lat[0])

    T11,T12,excluded_pixels = create_templates_around_target(cols,rows,target_x_y,s8_band,s9_band,flags)
    # find the average
    #print(len(pixels))
    
    
    T11_median =calculate_median_BT(T11)
    T12_median =calculate_median_BT(T12)
    #  Percentage of excluded layers
    # perc_excluded = (100 * excluded_pixels) / 961
    #print('Excluded: %d' % excluded_pixels) 

    Rij = calculate_product_R(T11,T12,T11_median,T12_median)
    Rji = calculate_product_R(T12,T11,T12_median,T11_median)
    
    r2 = Rij*Rji
    if r2>0.97:
        label = 'reliable'
    elif r2<=0.97 and r2>=0.95:
        label = 'uncertain'
    elif r2<0.95:
        label = 'rejected'
    
    wv=10*(13.73-13.662*Rij)
    
    # detect the time for that specific row and convert from microseconds (10^(-6) sec) to date / time
    time_stamp = time[target_x_y[0] - 1]  # because python array index start from 0 while sentinel rows from 1
    #time_stamp=Nadir_Minimal_ts_i[target_x_y[0] - 1] + (scan_in[target_x_y] - Nadir_first_scan_i[target_x_y[0] - 1])*SCANSYNC_i[0] +(pixel_in[target_x_y] - NADIR_FIRST_PIXEL[0])*PIXSYNC_i[0]
    #time_stamp=Oblique_Minimal_ts_i[target_x_y[0] - 1] + (scan_io[target_x_y] - Oblique_first_scan_i[target_x_y[0] - 1])*SCANSYNC_i[0] +(pixel_io[target_x_y] - OBLIQUE_FIRST_PIXEL[0])*PIXSYNC_i[0]
    # print(SCANSYNC_i)
    # print(NADIR_FIRST_PIXEL)
    # print(PIXSYNC_i[0])
    # time_stamp=Nadir_Minimal_ts_i[target_x_y[0] - 1] + (scan_in[target_x_y] - Nadir_first_scan_i[target_x_y[0] - 1])*SCANSYNC_i[0] +(pixel_in[target_x_y] - NADIR_FIRST_PIXEL[0])*PIXSYNC_i[0]
    # print(time_stamp)
    date = dt(2000, 1, 1, 0, 0 ,0) + timedelta(seconds=time_stamp/1e6)
    if cycle =='011':
        print(" ")  

    ecmwf_wv= find_weights(target_lat,target_lon,lattx,lontx,target_x_ytx,tcwv_ecmwf[0])
    return(n + ', ' + elements[11] + ', ' + elements[12] + ', ' + str(date) + ', ' + str(target_x_y[0]) + ', '+ str(target_x_y[1]) + ', ' + str(target_lon) + ', ' + str(target_lat) + ', '  + str(wv) + ', ' + str(excluded_pixels/400*100)  +', '+label+','+ str(r2)+','+str(tcwv_ecmwf[0][target_x_ytx[0]][target_x_ytx[1]])+', '+str(lattx[target_x_ytx[0]][target_x_ytx[1]])+', '+str(lontx[target_x_ytx[0]][target_x_ytx[1]])
            +','+str(tcwv_ecmwf[0][target_x_ytx[0]][target_x_ytx[1]-1])+','+str(tcwv_ecmwf[0][target_x_ytx[0]][target_x_ytx[1]+1])+', '+str(lattx[target_x_ytx[0]][target_x_ytx[1]+1])+', '+str(lontx[target_x_ytx[0]][target_x_ytx[1]+1])+','+str(ecmwf_wv)) 

# Create the csv file
f = open("/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/s3B_values_CDN_BT1.csv" , "w")
f.write("File, Cycle, Orbit, Date and Time, image x_cord, image y-cord, Longitude, Latitude, WV, Excluded_pixels (%), label, r2 , ecmwf,lat,lon  \n")

for root, dirs, files in os.walk('/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/Data1'):
    for name in dirs:
        # In this step we are in an netcdf image folder
        print(name)
        path = os.path.join(root, name)
        with open("/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/CDN1.txt", 'r') as f_loc:
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
