from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
import sys
import os
#orbit = sys.argv[1]
api = SentinelAPI('thkalamarakis', 'th0doris6287', 'https://apihub.copernicus.eu/apihub')
print(api)
footprint = geojson_to_wkt(read_geojson('/home/thodorisk/Documents/Sentinel3_WV/sentinel3_OLCI/map_CDN.geojson'))
print(footprint)
products = api.query(footprint,
                     producttype='SL_1_RBT___',
                     #relativeorbitnumber= '7',
                     #cyclenumber = '052',
                     date=('20191225', date(2020, 1, 24)),
                     platformname='Sentinel-3',
                     filename = "S3B_*",
                     instrumentshortname = "SLSTR",
                     #platformnumber = 'B'
                     #timeliness="Non Time Critical"
                     )
#print(products)
api.download_all(products)

