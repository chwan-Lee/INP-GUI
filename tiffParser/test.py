import sys
from osgeo import gdal


sys.stdout = open('.\\output\\stdout2.txt','w')

image = gdal.Open('.\\tiff\\sample_2.TIF')
img = image.GetRasterBand(1)
arr = img.ReadAsArray()

for i in arr :
    for j in i:
        print(j, end=" ")
    print()

sys.stdout.close()
