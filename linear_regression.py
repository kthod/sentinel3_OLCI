import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression,HuberRegressor,RANSACRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import numpy as np
import csv

# Specify the file path
file_path_slstr = '/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/s3B_values_CDN_BT1.csv'


# Load data
with open(file_path_slstr, mode='r', encoding='utf-8') as file2:
    # Create a CSV reader
    csv_reader2 = csv.reader(file2)
    
    # Specify the index of the column you are interested in
    column_of_interest_index = 1  # e.g., get the second column
    
    x =[]
    y = []
    date_slstr = []
    # Iterate through the rows
    # Iterate through the rows with index
    for index, row in enumerate(csv_reader2):
        # Skip the first row
        print(index)
        if index == 0:
            continue
        if(row[8]==''):
            continue
        if(float(row[8])>90) or (float(row[8])<0):
            continue
        if(float(row[11])<0.97):
            continue
    
        x.append(float(row[8]))
        y.append(float(row[12]))
        
x_np = np.array(x).reshape(-1, 1)
y_np = np.array(y)

# data = pd.read_csv('data.csv')
# x = data.iloc[:, 0].values.reshape(-1, 1)  # Input feature
# y = data.iloc[:, 1].values  # Target variable

# Split data into training and validation sets
x_train, x_val, y_train, y_val = train_test_split(x_np, y_np, test_size=0.99, random_state=42)

# Initialize a linear regression model
model = LinearRegression()

# Train the model using the training data
model.fit(x_train, y_train)


# ransac_coef = model.estimator_.coef_
# ransac_intercept = model.estimator_.intercept_
# print(f"RANSAC Coefficient (Slope): {ransac_coef[0]}")
# print(f"RANSAC Intercept: {ransac_intercept}")

#Get parameters
coefficient = model.coef_[0]
intercept = model.intercept_

print(f'Coefficient (Slope): {coefficient}')
print(f'Intercept (Y-Intercept): {intercept}')

# Predict target variable with validation input data
y_pred = model.predict(x_val)

# Evaluate the model
mse = mean_squared_error(y_val, y_pred)
rmse = mse ** 0.5
print(f'Mean Squared Error: {mse}')
print(f'Root Mean Squared Error: {rmse}')

# Plotting
plt.scatter(x_val, y_val, color='black', label='Actual')
plt.plot(x_val, y_pred, color='blue', linewidth=3, label='Prediction')
plt.xlabel('Input')
plt.ylabel('Target')
plt.title('Linear Regression')
plt.legend()
plt.show()
