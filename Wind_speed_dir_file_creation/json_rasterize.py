import os
import glob
import pandas as pd
import json
import rasterio

def process_wind_data(folder_path, csv_path):
    wind_data = pd.read_csv(csv_path, delimiter=';')
    wind_data['rounded_speed'] = wind_data['speed'].round().astype(int)
    wind_data['rounded_dir'] = wind_data['dir'].round().astype(int)
    wind_data['time'] = pd.to_datetime(wind_data['time'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
    wind_data['time_for_filename'] = pd.to_datetime(wind_data['time'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%m-%d-%Y_%H%M')

    output_data = {
        "SPEED": {},
        "ANGLE": {}
    }

    # Поиск файлов .asc, соответствующих округленным значениям speed, dir и времени
    for _, row in wind_data.iterrows():
        time_str = row['time_for_filename']
        print(f"Поиск файлов для времени: {time_str}, скорости: {row['rounded_speed']}, направления: {row['rounded_dir']}")
        vel_files = glob.glob(os.path.join(folder_path, f"*_{row['rounded_dir']}_{row['rounded_speed']}_{time_str}*_vel.asc"))
        ang_files = glob.glob(os.path.join(folder_path, f"*_{row['rounded_dir']}_{row['rounded_speed']}_{time_str}*_ang.asc"))

        print(f"Найдено файлов скорости: {len(vel_files)}, файлов направления: {len(ang_files)}")

        # Если найдены соответствующие файлы, преобразовать их в TIF
        for file_path in vel_files:
            output_file_path = os.path.join(folder_path, os.path.basename(file_path).replace('_vel.asc',  f'_wind_{row["rounded_speed"]}.tif'))
            with rasterio.open(file_path) as src:
                raster = src.read(1)
                meta = src.meta
                crs = src.crs
            meta['crs'] = crs

            with rasterio.open(output_file_path, 'w', **meta) as dst:
                dst.write(raster, 1)
            output_data["SPEED"][row['time']] = os.path.basename(output_file_path)
            print(f"Создан файл скорости: {output_file_path}")

        for file_path in ang_files:
            output_file_path = os.path.join(folder_path, os.path.basename(file_path).replace('_ang.asc', f'_angle_{row["rounded_dir"]}.tif'))
            with rasterio.open(file_path) as src:
                raster = src.read(1)
                meta = src.meta
                crs = src.crs
            meta['crs'] = crs

            with rasterio.open(output_file_path, 'w', **meta) as dst:
                dst.write(raster, 1)
            output_data["ANGLE"][row['time']] = os.path.basename(output_file_path)
            print(f"Создан файл направления: {output_file_path}")

    # Запись результатов в JSON
    json_file_name = f"wind_test_{os.path.basename(folder_path)}.json"
    json_file_path = os.path.join(folder_path, json_file_name)
    with open(json_file_path, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)
    print(f"Создан JSON файл: {json_file_path}")

def main():
    base_folder_path = "C:\\work\\fire_model\\1\\utm"
    csv_folder_path = os.path.join(base_folder_path, "filtered")

    # Найти все папки, начинающиеся с "wind_"
    folders_to_process = [os.path.join(base_folder_path, folder) for folder in os.listdir(base_folder_path) if folder.startswith("wind_")]

    for folder in folders_to_process:
        folder_name = os.path.basename(folder)
        csv_file_name = "wind_" + folder_name.replace('wind_', '') + ".csv"
        csv_file_path = os.path.join(csv_folder_path, csv_file_name)

        if os.path.exists(csv_file_path):
            print(f"Начинаю обработку папки {folder} с файлом {csv_file_path}")
            process_wind_data(folder, csv_file_path)
            print(f"Обработка папки {folder} завершена")
        else:
            print(f"CSV файл {csv_file_path} не найден")

if __name__ == "__main__":
    main()
