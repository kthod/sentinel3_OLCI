from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import sys
import os
#orbit = sys.argv[1]
api = SentinelAPI('kthod', 'kala1300', 'https://apihub.copernicus.eu/apihub')
print(api)
footprint = geojson_to_wkt(read_geojson(r"C:\Users\thodoris\Documents\Python_Scripts\s3\s3\map_CDN.geojson"))
print(footprint)
products = api.query(footprint,
                     producttype='OL_2_LRR___',
                     relativeorbitnumber= '7',
                     #cyclenumber = '052',
                     date=('20150225', date(2023, 7, 24)),
                     platformname='Sentinel-3',
                     filename = "S3B_*",
                     instrumentshortname = "OLCI"
                     #platformnumber = 'B'
                     )
#print(products)
api.download_all(products)

