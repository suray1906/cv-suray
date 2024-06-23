import datetime
import os
import json
import csv
from math import sqrt


# Функция для извлечения данных о ветре из файла
def extract_wind_by_time(filename):
    res = {}
    with open(filename) as f:
        data = json.load(f)
        main_array = data["value0"]["value0"]

        for i in main_array:
            i_time = i["value0"]
            i_dt = datetime.datetime.utcfromtimestamp(i_time)



            direction = (i["value4"] + 180) % 360
            speed = i["value5"]

            res[i_dt] = (speed, direction)

    return res


# Функция для фильтрации данных по времени
def filter_time(data_by_time, start_dt, end_dt):
    return {k: v for k, v in data_by_time.items() if start_dt <= k <= end_dt}


# Функция для нахождения ближайшего и последнего по времени изменения кэш-файла
def find_best_cache_file(lat, lon, cache_dir):
    closest_file = None
    min_distance = float('inf')
    latest_mtime = 0

    for f in os.listdir(cache_dir):
        try:
            i_split = f.split("_")
            i_lat = float(i_split[4])
            i_lon = float(i_split[5])
            distance = sqrt((i_lat - lat) ** 2 + (i_lon - lon) ** 2)
            mtime = os.path.getmtime(os.path.join(cache_dir, f))

            if distance < min_distance or (distance == min_distance and mtime > latest_mtime):
                min_distance = distance
                latest_mtime = mtime
                closest_file = f
        except (IndexError, ValueError):
            continue

    return closest_file


# Чтение данных о пожарах из CSV файла
fire_csv_file = r"C:\fire\cache.csv"
fires = []
with open(fire_csv_file, newline='') as csvfile:
    fire_reader = csv.DictReader(csvfile, delimiter=';')
    for row in fire_reader:
        row['x_min'] = float(row['x_min'])
        row['x_max'] = float(row['x_max'])
        row['y_min'] = float(row['y_min'])
        row['y_max'] = float(row['y_max'])
        row['fire_id'] = int(row['fire_id'])
        fires.append(row)

# Директория с кэш-файлами
cache_dir = r"C:\work\fire_model\model\cache"

# Обработка каждой строки в исходных данных
for fire in fires:
    fire_id = fire['fire_id']
    start_dt = datetime.datetime.fromisoformat(fire['dt_start'])
    end_dt = datetime.datetime.fromisoformat(fire['dt_end'])
    lat = (fire['y_max'] + fire['y_min']) / 2
    lon = (fire['x_max'] + fire['x_min']) / 2
    print(fire_id)
    print(lat)
    print(lon)

    # Поиск ближайшего и последнего по времени изменения кэш-файла
    best_file = find_best_cache_file(lat, lon, cache_dir)
    if best_file is None:
        print(f"No matching cache file found for fire_id {fire_id}")
        continue
    print(f"Using cache file: {best_file}")

    # Создание нового CSV-файла для fire_id
    output_filename = f"C:\\work\\fire_model\\1\\123\\wind_{fire_id}.csv"
    with open(output_filename, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["time", "speed", "dir"])

        # Обработка ближайшего и последнего по времени изменения кэш-файла
        cache_file_path = os.path.join(cache_dir, best_file)
        wind_data = extract_wind_by_time(cache_file_path)
        filtered_data = filter_time(wind_data, start_dt, end_dt)

        # Запись данных в CSV-файл
        for k, v in filtered_data.items():
            writer.writerow([k, v[0], v[1]])

print("Обработка завершена.")
