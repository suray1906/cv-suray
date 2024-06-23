import os
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd

os.environ['PROJ_LIB'] = r'C:\Users\Su_Us\anaconda3\envs\myenv\Library\share\proj'
# Путь к папкам
cntr_path = "D:\\FIRE\\rezka"
aster_path = "D:\\FIRE\\study\\ASTER"
output_path = "D:\\FIRE\\gran"

# Создаем папку для сохранения результатов, если ее нет
if not os.path.exists(output_path):
    os.makedirs(output_path)

def get_raster_bounds(raster_path):
    with rasterio.open(raster_path) as src:
        bounds = src.bounds
    return bounds

def find_aster_files(bounds, aster_path):
    aster_files = []
    for root, dirs, files in os.walk(aster_path):
        for file in files:
            if file.endswith('.tif'):
                aster_file_path = os.path.join(root, file)
                aster_bounds = get_raster_bounds(aster_file_path)
                if box(*bounds).intersects(box(*aster_bounds)):
                    aster_files.append(aster_file_path)
    return aster_files

def merge_aster_files(aster_files):
    src_files_to_mosaic = []
    for fp in aster_files:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)
    mosaic, out_trans = merge(src_files_to_mosaic)
    meta = src_files_to_mosaic[0].meta.copy()
    meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "count": mosaic.shape[0]
    })
    return mosaic, out_trans, meta

def cut_cntr_area(cntr_file, mosaic, out_trans, meta):
    with rasterio.open(cntr_file) as cntr_src:
        cntr_bounds = cntr_src.bounds
        cntr_geom = box(*cntr_bounds)
        cntr_geo_df = gpd.GeoDataFrame({'geometry': [cntr_geom]}, crs=cntr_src.crs)

    with rasterio.io.MemoryFile() as memfile:
        with memfile.open(**meta) as dataset:
            dataset.write(mosaic)
            out_image, out_transform = mask(dataset=dataset, shapes=cntr_geo_df.geometry, crop=True)
    return out_image, out_transform

def save_raster(output_path, cntr_file, out_image, out_transform, meta):
    out_meta = meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": out_image.shape[1],
                     "width": out_image.shape[2],
                     "transform": out_transform})

    output_file = os.path.join(output_path, os.path.basename(cntr_file))
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(out_image)

# Основной цикл обработки файлов
for root, dirs, files in os.walk(cntr_path):
    for file in files:
        if file.endswith('.img') or file.endswith('.tif'):
            cntr_file_path = os.path.join(root, file)
            cntr_bounds = get_raster_bounds(cntr_file_path)
            aster_files = find_aster_files(cntr_bounds, aster_path)
            if aster_files:
                mosaic, out_trans, meta = merge_aster_files(aster_files)
                out_image, out_transform = cut_cntr_area(cntr_file_path, mosaic, out_trans, meta)
                save_raster(output_path, cntr_file_path, out_image, out_transform, meta)

print("Обработка завершена!")
