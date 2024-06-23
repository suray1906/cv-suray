import os
from osgeo import gdal

# Путь к корневому каталогу
root_directory = "C:\\work\\fire_model\\1\\222\\wind_raster"


def convert_to_wgs84(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith('.tif'):
            file_path = os.path.join(directory, file_name)
            # Открываем исходное изображение
            src_ds = gdal.Open(file_path)
            if src_ds is None:
                print(f"Не удалось открыть {file_path}")
                continue

            # Получаем параметры преобразования
            dst_wkt = 'EPSG:4326'

            # Создаем название временного файла
            temp_file_path = os.path.join(directory, "temp_" + file_name)

            # Преобразуем изображение
            gdal.Warp(temp_file_path, src_ds, dstSRS=dst_wkt)

            # Закрываем исходное изображение
            src_ds = None

            # Заменяем оригинальный файл
            os.remove(file_path)
            os.rename(temp_file_path, file_path)
            print(f"Конвертирован: {file_path}")


# Проходим по всем папкам в корневом каталоге, которые начинаются с "wind_"
for folder_name in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder_name)
    if os.path.isdir(folder_path) and folder_name.startswith("wind_"):
        convert_to_wgs84(folder_path)

print("Конвертация завершена.")
