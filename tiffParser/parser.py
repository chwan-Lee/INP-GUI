import sys
from osgeo import gdal


gdalFile = gdal.Open('.\\input\\ia00000098.TIF')
img = gdalFile.GetRasterBand(1)
arr = img.ReadAsArray()

gt = gdalFile.GetGeoTransform()
print('Image geo-transform = {}'.format(gt))            # 좌표와 해상도 정보, 좌표 시스템에 따라 값의 확인이 필요

LEFT, pxRightUnit, TOP, pxDownUnit = float(gt[0]), int(gt[1]), float(gt[3]), int(gt[5])
print('Left: {0}, X-Step: {1}, Top: {2}, Y-Step: {3}'.format(LEFT, pxRightUnit, TOP, pxDownUnit))

print("Y축 갯수 : {0}, X축 갯수 : {1}".format(len(arr), len(arr[0])))

'''
sys.stdout = open('.\\output\\stdout2.txt','w')
for y in arr:
    for x in y:
        print(x, end=" ")
    print()
sys.stdout.close()
'''