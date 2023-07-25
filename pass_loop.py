import os

passes = ['007', '21', '64', '78', '121', '135', '178', '235', '278', '292', '335', '349']

for i in passes:
    print(i)
    os.system('python s3_retrieve_V3.py %s' % i)
