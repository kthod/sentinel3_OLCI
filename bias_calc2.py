import csv
import numpy as np
import matplotlib.pyplot as plt
# Specify the file path
file_path_slstr = '/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/s3B_values_CDN_BT.csv'
file_path_olci = '/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/s3B_values_CDN.csv'
from datetime import datetime


date_format = " %Y-%m-%d %H:%M:%S.%f"
reduced_date_format = " %Y-%m-%d %H:%M"

def find_common_dates(date1,date2,wv1,wv2):
    common_dates = set(date1) & set(date2)
    idx_1 = [date1.index(date) for date in common_dates]
    idx_2 = [date2.index(date) for date in common_dates]

    # Extract the corresponding water vapor values for common dates
    common_vapor_1 = [wv1[i] for i in idx_1]
    common_vapor_2 = [wv2[i] for i in idx_2]

    print(type(common_dates))
    bias = np.abs(np.array(common_vapor_1) - np.array(common_vapor_2))
    return bias,list(common_dates)
# Calculating Mean Bias Error


with open(file_path_olci, mode='r', encoding='utf-8') as file1:
    # Create a CSV reader
    csv_reader1 = csv.reader(file1)
    
    # Specify the index of the column you are interested in
    #column_of_interest_index = 1  # e.g., get the second column
    
    iwv =[]
    iwv_avg = []
    date_olci_iwv = []
    date_olci_iwv_avg = []
    # Iterate through the rows
    # Iterate through the rows with index
    for index, row in enumerate(csv_reader1):
        # Skip the first row
        if index == 0:
            continue
        if(row[8]!=' --'):
            iwv.append(float(row[8]))
            formatted_date_str = datetime.strptime(row[3], date_format).strftime(reduced_date_format)
            date_olci_iwv.append(datetime.strptime(formatted_date_str, reduced_date_format))

        if(row[9]!=' --'):
            iwv_avg.append(float(row[9]))
            formatted_date_str = datetime.strptime(row[3], date_format).strftime(reduced_date_format)
            date_olci_iwv_avg.append(datetime.strptime(formatted_date_str, reduced_date_format))
        


# Open the file
with open(file_path_slstr, mode='r', encoding='utf-8') as file2:
    # Create a CSV reader
    csv_reader2 = csv.reader(file2)
    
    # Specify the index of the column you are interested in
    column_of_interest_index = 1  # e.g., get the second column
    
    estimated_wv =[]
    ecmwf_wv = []
    date_slstr = []
    # Iterate through the rows
    # Iterate through the rows with index
    for index, row in enumerate(csv_reader2):
        # Skip the first row
        if index == 0:
            continue
        if(float(row[8])>50):
            continue
        if(float(row[11])<0.97):
            continue
        estimated_wv.append(float(row[8]))
        ecmwf_wv.append(float(row[12]))
        formatted_date_str = datetime.strptime(row[3], date_format).strftime(reduced_date_format)
        date_slstr.append(datetime.strptime(formatted_date_str, reduced_date_format))


# Assuming:
# dates_1 and water_vapor_1 correspond to the first dataset
# dates_2 and water_vapor_2 correspond to the second dataset

# Find common dates and their indices in both datasets


##########################################################
# comparison of iwv by olci with tcwv by slstr
##########################################################

bias,common_dates = find_common_dates(date_olci_iwv,date_slstr,iwv,estimated_wv)
plt.title("comparison of wv by olci with zwd by slstr in kg/m^2")
plt.scatter(common_dates,bias)
plt.show()

print("comparison of wv by olci with wv by slstr in kg/m^2")
print(f"mean abs error {np.mean(bias)}")
print(f"std {np.std(bias)}")

##########################################################
# comparison of iwv_avg by olci with tcwv by slstr
##########################################################

bias,common_dates = find_common_dates(date_olci_iwv_avg,date_slstr,iwv_avg,estimated_wv)
plt.title("comparison of zwd_avg by olci with zwd by slstr in kg/m^2")
plt.scatter(common_dates,bias)
plt.show()
print("comparison of iwv_avg by olci with wv by slstr in kg/m^2")
print(f"mean abs error {np.mean(bias)}")
print(f"std {np.std(bias)}")

##########################################################
# comparison of estimated wv by slstr with ecmwf
##########################################################
bias = np.abs(np.array(estimated_wv) - np.array(ecmwf_wv))
plt.title("comparison of estimated wv by slstr with ecmwf in mm")
plt.scatter(date_slstr,bias)
plt.show()
print("comparison of estimated wv by slstr with ecmwf in kg/m^2")
print(f"mean abs error {np.mean(bias)}")
print(f"std {np.std(bias)}")



plt.title("WV measurments")
plt.xlabel("date")
plt.ylabel("TCWV in kg/m^2") 

plt.scatter(date_slstr,estimated_wv ,label = 'estimated wv (slstr)')
plt.scatter(date_slstr,ecmwf_wv,label= 'ecmwf_wv')
plt.scatter(date_olci_iwv,iwv ,label = 'iwv (olci)')
plt.scatter(date_olci_iwv_avg,iwv_avg,label= 'iwv avg (olci)')
plt.legend()
plt.show()
# plt.scatter(date,bias)
# plt.show()

# print(estimated_wv)
# print(ecmwf_wv)        
# print(date)
