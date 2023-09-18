import numpy as np
lat = np.array([[1,2,3],[1,2,3]])
lon = np.array([[1,2,3],[1,3,3]])
lat = lat[:, :, np.newaxis]
    # print lat.shape
lon = lon[:, :, np.newaxis]
    # print lat.shape
grid = np.concatenate([lat, lon], axis=2)
print(grid)
target_lat=2
target_lon = 2
vector = np.array([target_lat, target_lon]).reshape(1, 1, -1)
print(vector)
subtraction = vector - grid
print(subtraction)
 # vector subtraction
dist = np.linalg.norm(subtraction, axis=2) # it takes the norm in each row
print(dist)
    # query where in the 2D matrix is the closest point to your points of interest ?
result =  np.where(dist == dist.min())
print(result)