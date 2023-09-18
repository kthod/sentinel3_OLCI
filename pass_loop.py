import os

#passes = ['007', '21', '64', '78', '121', '135', '178', '235', '278',
passes = [ '107','292', '335', '349']

for i in passes:
    print(i)
    os.system('C:/Users/thodoris/Documents/Python_Scripts/s3/s3/download.py %s' % i)
