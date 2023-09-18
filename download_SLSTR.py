from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import sys
import os
#orbit = sys.argv[1]
api = SentinelAPI('thkalamarakis', 'th0doris6287', 'https://apihub.copernicus.eu/apihub')
print(api)
footprint = geojson_to_wkt(read_geojson(r"C:\Users\thodoris\Documents\Python_Scripts\s3\s3\map_CDN.geojson"))
print(footprint)
products = api.query(footprint,
                     producttype='SL_2_LST___',
                     relativeorbitnumber= '78',
                     #cyclenumber = '052',
                     #date=('20230425', date(2023, 7, 24)),
                     platformname='Sentinel-3',
                     filename = "S3B_*",
                     instrumentshortname = "SLSTR",
                     #platformnumber = 'B'
                     timeliness="Non Time Critical"
                     )
#print(products)
api.download_all(products)

