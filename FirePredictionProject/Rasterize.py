from osgeo import gdal
import os
import rasterio

# Устанавливаем переменную окружения
os.environ['PROJ_LIB'] = r'C:\Users\Su_Us\anaconda3\envs\myenv\Library\share\proj'

# Задаем путь к папке
folder_path = 'D:\\Fire_Data\\150\\'

# Создаем список файлов, которые нужно обработать
file_names = {

    '68151_utm_130_3_30m_ang.asc',
    '68151_utm_130_3_30m_vel.asc',
    '68151_utm_143_4_30m_ang.asc',
    '68151_utm_143_4_30m_vel.asc',
    '68151_utm_149_2_30m_ang.asc',
    '68151_utm_149_2_30m_vel.asc',
    '68151_utm_155_3_30m_ang.asc',
    '68151_utm_155_3_30m_vel.asc',
    '68151_utm_162_4_30m_ang.asc',
    '68151_utm_162_4_30m_vel.asc',
    '68151_utm_163_3_30m_ang.asc',
    '68151_utm_163_3_30m_vel.asc',
    '68151_utm_170_4_30m_ang.asc',
    '68151_utm_170_4_30m_vel.asc',
    '68151_utm_176_2_30m_ang.asc',
    '68151_utm_176_2_30m_vel.asc',
    '68151_utm_178_4_30m_ang.asc',
    '68151_utm_178_4_30m_vel.asc',
    '68151_utm_181_3_30m_ang.asc',
    '68151_utm_181_3_30m_vel.asc',
    '68151_utm_189_2_30m_ang.asc',
    '68151_utm_189_2_30m_vel.asc',
    '68151_utm_197_3_30m_ang.asc',
    '68151_utm_197_3_30m_vel.asc',
    '68151_utm_198_3_30m_ang.asc',
    '68151_utm_198_3_30m_vel.asc',
    '68151_utm_215_4_30m_ang.asc',
    '68151_utm_215_4_30m_vel.asc'

}

# Обрабатываем каждый файл
for file_name in file_names:
    # Полный путь к файлу
    file_path = os.path.join(folder_path, file_name)

    # Путь к выходному файлу
    output_file_path = os.path.join(folder_path, file_name.replace('.asc', '.tif'))

    # Обработка файла
    with rasterio.open(file_path) as src:
        raster = src.read(1)
        meta = src.meta

    with rasterio.open(output_file_path, 'w', **meta) as dst:
        dst.write(raster, 1)
