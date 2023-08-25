import os
import glob
from osgeo import gdal, ogr, osr
!pip install geopandas
import geopandas as gpd

# Путь к каталогу с растровыми файлами
input_directory = '/content/'
output_directory = r"down"

# Проверка на существование выходного каталога, если его нет - создаем
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Список файлов .img во входной директории
raster_files = glob.glob(os.path.join(input_directory, "*.img"))

for raster_file in raster_files:
    # Открытие растра
    raster_dataset = gdal.Open(raster_file, gdal.GA_ReadOnly)
    raster_band = raster_dataset.GetRasterBand(1)

    # Создание бинарной маски
    binary_mask = (raster_band.ReadAsArray() > -2).astype(int)

    # Сохранение бинарной маски в новый растровый файл
    output_raster_file = os.path.join(output_directory, os.path.basename(raster_file))
    driver = gdal.GetDriverByName('GTiff')
    output_raster = driver.Create(output_raster_file, raster_dataset.RasterXSize, raster_dataset.RasterYSize, 1,
                                  gdal.GDT_Int32)
    output_raster.SetGeoTransform(raster_dataset.GetGeoTransform())
    output_raster.SetProjection(raster_dataset.GetProjectionRef())
    output_raster.GetRasterBand(1).WriteArray(binary_mask)
    output_raster.FlushCache()
    output_raster = None # Закрываем файл

    # Открываем бинарный растр для полигонизации
    binary_raster = gdal.Open(output_raster_file, gdal.GA_ReadOnly)
    binary_band = binary_raster.GetRasterBand(1)

    # Преобразование растра в вектор
    output_vector_file = os.path.splitext(output_raster_file)[0] + '.shp'
    source_srs = osr.SpatialReference()
    source_srs.ImportFromWkt(raster_dataset.GetProjectionRef())
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source_srs, target_srs)

    driver = ogr.GetDriverByName('ESRI Shapefile')
    output_vector = driver.CreateDataSource(output_vector_file)
    output_layer = output_vector.CreateLayer('polygonized', srs=target_srs)
    new_field = ogr.FieldDefn('DN', ogr.OFTInteger)
    output_layer.CreateField(new_field)

    gdal.Polygonize(binary_band, None, output_layer, 0, [], callback=None)
    output_vector.FlushCache()

    # Удаление полигонов с нулевыми значениями
    gdf = gpd.read_file(output_vector_file)
    gdf = gdf[gdf['DN'] != 0]
    gdf.to_file(output_vector_file)

    print(f'Processed {raster_file}')