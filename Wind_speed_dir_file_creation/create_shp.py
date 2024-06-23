import os
import rasterio
import numpy as np
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import geopandas as gpd
from rasterio.features import shapes


def process_images(input_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.img') or filename.endswith('.tif'):
            img_path = os.path.join(input_folder, filename)
            process_image(img_path)

def process_image(img_path):
    with rasterio.open(img_path) as src:
        data = src.read(1)  # Чтение первого канала

        # Приведение типа данных к float32
        data = data.astype(np.float32)

        mask = data != -3  # Создание маски для значений, отличных от -3
        print(f"Обрабатываем {img_path}")
        # Преобразование маски в геометрии
        results = (
            {'properties': {'raster_val': v}, 'geometry': s}
            for i, (s, v) in enumerate(
            shapes(data, mask=mask, transform=src.transform))
        )

        # Создание GeoDataFrame из геометрий
        geoms = list(results)
        if geoms:
            gdf = gpd.GeoDataFrame.from_features(geoms)

            # Объединение всех полигонов в один и упрощение
            union = unary_union(gdf.geometry)
            simplified_union = union.buffer(0.0001).simplify(0.0001)

            # Создание нового GeoDataFrame для упрощенной геометрии
            simplified_gdf = gpd.GeoDataFrame(geometry=[simplified_union], crs=src.crs)

            # Создание имени для shp файла
            shp_path = os.path.splitext(img_path)[0] + '_shape.shp'

            # Сохранение в shp файл
            simplified_gdf.to_file(shp_path)
            print(f"сохранили {shp_path}")

if __name__ == "__main__":
    input_folder = r"C:\work\fire_model\1\stary_pozar\Новая папка"
    process_images(input_folder)
