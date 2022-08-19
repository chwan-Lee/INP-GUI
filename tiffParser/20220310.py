from osgeo import gdal
import sys

filename = ['.\\tiff\\CC_RSSI.TIF']

for i in range(0, 1) :
    img = gdal.Open(filename[i])
    metadata = img.GetMetadata()
    gt = img.GetGeoTransform()
    desc = img.GetDescription()
    driver = img.GetDriver()
    proj = img.GetProjection()
    num_bands = img.RasterCount
    xSize = img.RasterXSize
    ySize = img.RasterYSize

    band = img.GetRasterBand(1)
    datatype = band.DataType
    datatype_name = gdal.GetDataTypeName(band.DataType)
    bytes = gdal.GetDataTypeSize(band.DataType)
    band_max, band_min, band_mean, band_stddev = band.GetStatistics(0, 1)

    print(i, filename[i], ":", metadata)
    print(" ", filename[i], ":", "Description = ", desc)                        # 파일 이름 정보
    print(" ", filename[i], ":", "Projection = ", proj)                         # projection(좌표 관련 정보 포함 않됨, htz export 시 적용되지 안음)
    print(" ", filename[i], ":", "X =", xSize, "Y =", ySize)                    # 데이터 픽셀 숫자(해상도에 따른 픽셀 숫자, 좌표와 거리 등 고려)
    print(' ', filename[i], ":", 'Image geo-transform = {gt}'.format(gt=gt))    # 좌표와 해상도 정보, 좌표 시스템에 따라 값의 확인이 필요
    print(" ", filename[i], ":", 'Raster driver: {d}'.format(d=driver.ShortName))
    print(" ", filename[i], ":", "Band No. =", num_bands, band)
    print(" ", filename[i], ":", 'Band datatype: {dt}'.format(dt=band.DataType))
    print(" ", filename[i], ":", 'Band datatype: {dt}'.format(dt=datatype_name))
    print(" ", filename[i], ":", 'Band datatype size: {b} bytes'.format(b=bytes))
    print(" ", filename[i], ":", 'Band range: {minimum} - {maximum}'.format(maximum=band_max, minimum=band_min)) # data range = Received level
    print(" ", filename[i], ":", 'Band mean, stddev: {m}, {s}\n'.format(m=band_mean, s=band_stddev))
