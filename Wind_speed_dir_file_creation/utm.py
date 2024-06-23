import os
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import CRS

# Путь к папке с исходными изображениями
input_path = "D:\\FIRE\\gran"


# Функция для определения зоны UTM на основе координат
def get_utm_zone(lon, lat):
    utm_zone = int((lon + 180) / 6) + 1
    if lat >= 0:
        utm_crs = CRS.from_epsg(32600 + utm_zone)
    else:
        utm_crs = CRS.from_epsg(32700 + utm_zone)
    return utm_crs


# Основной цикл обработки файлов
for root, dirs, files in os.walk(input_path):
    for file in files:
        if file.endswith('.tif'):
            input_file_path = os.path.join(root, file)

            # Открываем исходный файл
            with rasterio.open(input_file_path) as src:
                # Определяем координаты центра изображения
                lon_center = (src.bounds.left + src.bounds.right) / 2
                lat_center = (src.bounds.top + src.bounds.bottom) / 2

                # Определяем соответствующую зону UTM
                utm_crs = get_utm_zone(lon_center, lat_center)

                # Вычисляем параметры для перепроецирования
                try:
                    transform, width, height = calculate_default_transform(
                        src.crs, utm_crs, src.width, src.height, *src.bounds)
                except Exception as e:
                    print(f"Ошибка при вычислении параметров перепроецирования для файла {input_file_path}: {e}")
                    continue

                # Обновляем метаданные
                kwargs = src.meta.copy()
                kwargs.update({
                    'crs': utm_crs,
                    'transform': transform,
                    'width': width,
                    'height': height
                })

                # Формируем имя выходного файла
                output_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}_utm.tif")

                # Перепроецируем и сохраняем изображение
                try:
                    with rasterio.open(output_file_path, 'w', **kwargs) as dst:
                        for i in range(1, src.count + 1):
                            reproject(
                                source=rasterio.band(src, i),
                                destination=rasterio.band(dst, i),
                                src_transform=src.transform,
                                src_crs=src.crs,
                                dst_transform=transform,
                                dst_crs=utm_crs,
                                resampling=Resampling.nearest)
                    print(f"Файл {input_file_path} перепроецирован и сохранен как {output_file_path}")
                except Exception as e:
                    print(f"Ошибка при перепроецировании файла {input_file_path}: {e}")

print("Обработка завершена!")
