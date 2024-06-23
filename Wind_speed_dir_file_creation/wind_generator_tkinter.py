import tkinter as tk
from tkinter import filedialog, scrolledtext, font, messagebox
import os
import datetime
import json
import csv
import pandas as pd
from math import sqrt
from datetime import datetime as dt
import rasterio
from osgeo import gdal
import threading
import glob
import subprocess
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pyproj import CRS

# Common functions
def log_message(log_text, message, error=False):
    log_text.insert(tk.END, f"{'ERROR: ' if error else ''}{message}\n")
    log_text.see(tk.END)
    log_text.update()

# Stop event
stop_event = threading.Event()

# Stage 1: Обрезка и перепроекция изображения ASTGTM2
def process_stage1():
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

        output_file = os.path.join(output_path, os.path.splitext(os.path.basename(cntr_file))[0] + ".tif")
        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)
        return output_file

    def get_utm_zone(lon, lat):
        utm_zone = int((lon + 180) / 6) + 1
        if lat >= 0:
            utm_crs = CRS.from_epsg(32600 + utm_zone)
        else:
            utm_crs = CRS.from_epsg(32700 + utm_zone)
        return utm_crs

    def reproject_to_utm(input_path, log_text):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if stop_event.is_set():
                    log_message(log_text, "Process stopped by user")
                    return
                if file.endswith('.tif'):
                    input_file_path = os.path.join(root, file)
                    with rasterio.open(input_file_path) as src:
                        lon_center = (src.bounds.left + src.bounds.right) / 2
                        lat_center = (src.bounds.top + src.bounds.bottom) / 2
                        utm_crs = get_utm_zone(lon_center, lat_center)

                        try:
                            transform, width, height = calculate_default_transform(
                                src.crs, utm_crs, src.width, src.height, *src.bounds)
                        except Exception as e:
                            log_message(log_text, f"Ошибка при вычислении параметров перепроецирования для файла {input_file_path}: {e}")
                            continue

                        kwargs = src.meta.copy()
                        kwargs.update({
                            'crs': utm_crs,
                            'transform': transform,
                            'width': width,
                            'height': height
                        })

                        output_file_path = os.path.join(root, f"{os.path.splitext(file)[0]}_utm.tif")

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
                            log_message(log_text, f"Файл {input_file_path} перепроецирован и сохранен как {output_file_path}")
                        except Exception as e:
                            log_message(log_text, f"Ошибка при перепроецировании файла {input_file_path}: {e}")

    def process_files(log_text):
        cntr_path = cntr_entry.get()
        aster_path = aster_entry.get()
        output_path = output_entry.get()

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for root, dirs, files in os.walk(cntr_path):
            if stop_event.is_set():
                log_message(log_text, "Process stopped by user")
                return
            for file in files:
                if stop_event.is_set():
                    log_message(log_text, "Process stopped by user")
                    return
                if file.endswith('.img') or file.endswith('.tif'):
                    cntr_file_path = os.path.join(root, file)
                    cntr_bounds = get_raster_bounds(cntr_file_path)
                    aster_files = find_aster_files(cntr_bounds, aster_path)
                    if aster_files:
                        mosaic, out_trans, meta = merge_aster_files(aster_files)
                        out_image, out_transform = cut_cntr_area(cntr_file_path, mosaic, out_trans, meta)
                        saved_file = save_raster(output_path, cntr_file_path, out_image, out_transform, meta)
                        log_message(log_text, f"Файл {saved_file} обработан и сохранен в {output_path}")

        reproject_to_utm(output_path, log_text)
        log_message(log_text, "Обработка завершена!")

    def select_cntr_path():
        path = filedialog.askdirectory()
        cntr_entry.delete(0, tk.END)
        cntr_entry.insert(0, path)

    def select_aster_path():
        path = filedialog.askdirectory()
        aster_entry.delete(0, tk.END)
        aster_entry.insert(0, path)

    def select_output_path():
        path = filedialog.askdirectory()
        output_entry.delete(0, tk.END)
        output_entry.insert(0, path)

    def start_processing():
        stop_event.clear()
        threading.Thread(target=process_files, args=(log_text,)).start()

    def stop_processing():
        stop_event.set()

    stage1_window = tk.Toplevel(root)
    stage1_window.title("Обрезка и перепроекция изображения ASTGTM2")

    tk.Label(stage1_window, text="Путь к изображениям:").grid(row=0, column=0, sticky=tk.W)
    cntr_entry = tk.Entry(stage1_window, width=50)
    cntr_entry.grid(row=0, column=1, padx=10, pady=5)
    cntr_button = tk.Button(stage1_window, text="Выбрать", command=select_cntr_path)
    cntr_button.grid(row=0, column=2, padx=10, pady=5)

    tk.Label(stage1_window, text="Путь к папке aster:").grid(row=1, column=0, sticky=tk.W)
    aster_entry = tk.Entry(stage1_window, width=50)
    aster_entry.grid(row=1, column=1, padx=10, pady=5)
    aster_button = tk.Button(stage1_window, text="Выбрать", command=select_aster_path)
    aster_button.grid(row=1, column=2, padx=10, pady=5)

    tk.Label(stage1_window, text="Путь к выходной папке:").grid(row=2, column=0, sticky=tk.W)
    output_entry = tk.Entry(stage1_window, width=50)
    output_entry.grid(row=2, column=1, padx=10, pady=5)
    output_button = tk.Button(stage1_window, text="Выбрать", command=select_output_path)
    output_button.grid(row=2, column=2, padx=10, pady=5)

    process_button = tk.Button(stage1_window, text="Пуск", command=start_processing)
    process_button.grid(row=3, column=1, pady=20)
    stop_button = tk.Button(stage1_window, text="Стоп", command=stop_processing)
    stop_button.grid(row=3, column=2, pady=20)

    global log_text
    log_text = scrolledtext.ScrolledText(stage1_window, width=80, height=20)
    log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

# Stage 2: Создание файла с метеоданными
def process_stage2():
    def extract_wind_by_time(filename):
        res = {}
        with open(filename) as f:
            data = json.load(f)
            main_array = data["value0"]["value0"]
            for i in main_array:
                if stop_event.is_set():
                    log_message(log_text, "Process stopped by user")
                    return res
                i_time = i["value0"]
                i_dt = datetime.datetime.utcfromtimestamp(i_time)
                direction = (i["value4"] + 180) % 360
                speed = i["value5"]
                res[i_dt] = (speed, direction)
        return res

    def filter_time(data_by_time, start_dt, end_dt):
        return {k: v for k, v in data_by_time.items() if start_dt <= k <= end_dt}

    def find_best_cache_file(lat, lon, cache_dir):
        closest_file = None
        min_distance = float('inf')
        latest_mtime = 0
        for f in os.listdir(cache_dir):
            if stop_event.is_set():
                log_message(log_text, "Process stopped by user")
                return closest_file
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

    def process_fire_data(fire_csv_file, cache_dir, output_filename):
        fires = []
        with open(fire_csv_file, newline='') as csvfile:
            fire_reader = csv.DictReader(csvfile, delimiter=';')
            for row in fire_reader:
                if stop_event.is_set():
                    log_message(log_text, "Process stopped by user")
                    return
                row['x_min'] = float(row['x_min'])
                row['x_max'] = float(row['x_max'])
                row['y_min'] = float(row['y_min'])
                row['y_max'] = float(row['y_max'])
                row['fire_id'] = int(row['fire_id'])
                fires.append(row)

        if not os.path.exists(output_filename):
            os.makedirs(output_filename)

        for fire in fires:
            if stop_event.is_set():
                log_message(log_text, "Process stopped by user")
                return
            fire_id = fire['fire_id']
            start_dt = datetime.datetime.fromisoformat(fire['dt_start'])
            end_dt = datetime.datetime.fromisoformat(fire['dt_end'])
            lat = (fire['y_max'] + fire['y_min']) / 2
            lon = (fire['x_max'] + fire['x_min']) / 2
            log_message(log_text, f"Обработка fire ID: {fire_id}, lat: {lat}, lon: {lon}")
            best_file = find_best_cache_file(lat, lon, cache_dir)
            if best_file is None:
                log_message(log_text, f"No matching cache file found for fire_id {fire_id}")
                continue
            log_message(log_text, f"Using cache file: {best_file}")
            output_file = os.path.join(output_filename, f"wind_{fire_id}.csv")
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["time", "speed", "dir"])
                cache_file_path = os.path.join(cache_dir, best_file)
                wind_data = extract_wind_by_time(cache_file_path)
                filtered_data = filter_time(wind_data, start_dt, end_dt)
                for k, v in filtered_data.items():
                    if stop_event.is_set():
                        log_message(log_text, "Process stopped by user")
                        return
                    writer.writerow([k, v[0], v[1]])
            log_message(log_text, f"Сохранен и обработан файл с метеоданными для fire_id {fire_id}")

    def filter_bytime(data, start_dt, end_dt):
        return data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]

    def process_wind_data(input_text_file, csv_dir):
        output_dir = os.path.join(csv_dir, "filtered")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_text_file, 'r') as file:
            lines = file.readlines()

        for line in lines:
            if stop_event.is_set():
                log_message(log_text, "Process stopped by user")
                return
            if not line.strip():
                continue
            try:
                parts = line.split(',')
                fire_id = int(parts[0].split(':')[1].strip())
                dt_begin = parts[1].split(':')[1].strip().strip('#')
                dt_end = parts[2].split(':')[1].strip().strip('#')
                start_dt = dt.fromisoformat(dt_begin)
                end_dt = dt.fromisoformat(dt_end)
                input_csv_file = os.path.join(csv_dir, f"wind_{fire_id}.csv")
                if not os.path.exists(input_csv_file):
                    log_message(log_text, f"CSV file for fire_id {fire_id} does not exist.")
                    continue
                data = pd.read_csv(input_csv_file, delimiter=';', parse_dates=['time'])
                filtered_data = filter_bytime(data, start_dt, end_dt)
                output_csv_file = os.path.join(output_dir, f"wind_{fire_id}_{end_dt.strftime('%Y-%m-%d_%H_%M_%S')}.csv")
                filtered_data.to_csv(output_csv_file, index=False, sep=';')
                log_message(log_text, f"Обработка fire_id {fire_id}: сохранен в {output_csv_file}")
            except Exception as e:
                log_message(log_text, f"Error processing line: {line}")
                log_message(log_text, str(e))

    def process_all():
        stop_event.clear()
        fire_csv_file = fire_csv_entry.get()
        cache_dir = cache_dir_entry.get()
        output_filename = output_dir_entry.get()
        input_text_file = input_text_entry.get()

        threading.Thread(target=process_fire_data, args=(fire_csv_file, cache_dir, output_filename)).start()
        threading.Thread(target=process_wind_data, args=(input_text_file, output_filename)).start()

    def select_fire_csv_file():
        file_path = filedialog.askopenfilename()
        fire_csv_entry.delete(0, tk.END)
        fire_csv_entry.insert(0, file_path)

    def select_cache_dir():
        dir_path = filedialog.askdirectory()
        cache_dir_entry.delete(0, tk.END)
        cache_dir_entry.insert(0, dir_path)

    def select_output_dir():
        dir_path = filedialog.askdirectory()
        output_dir_entry.delete(0, tk.END)
        output_dir_entry.insert(0, dir_path)

    def select_input_text_file():
        file_path = filedialog.askopenfilename()
        input_text_entry.delete(0, tk.END)
        input_text_entry.insert(0, file_path)

    def stop_processing():
        stop_event.set()

    stage2_window = tk.Toplevel(root)
    stage2_window.title("Создание файла с метеоданными")

    tk.Label(stage2_window, text="Путь к файлу fire CSV:").grid(row=0, column=0, sticky=tk.W)
    fire_csv_entry = tk.Entry(stage2_window, width=50)
    fire_csv_entry.grid(row=0, column=1, padx=10, pady=5)
    fire_csv_button = tk.Button(stage2_window, text="Выбрать", command=select_fire_csv_file)
    fire_csv_button.grid(row=0, column=2, padx=10, pady=5)

    tk.Label(stage2_window, text="Путь к папке cache:").grid(row=1, column=0, sticky=tk.W)
    cache_dir_entry = tk.Entry(stage2_window, width=50)
    cache_dir_entry.grid(row=1, column=1, padx=10, pady=5)
    cache_dir_button = tk.Button(stage2_window, text="Выбрать", command=select_cache_dir)
    cache_dir_button.grid(row=1, column=2, padx=10, pady=5)

    tk.Label(stage2_window, text="Путь к папке output:").grid(row=2, column=0, sticky=tk.W)
    output_dir_entry = tk.Entry(stage2_window, width=50)
    output_dir_entry.grid(row=2, column=1, padx=10, pady=5)
    output_dir_button = tk.Button(stage2_window, text="Выбрать", command=select_output_dir)
    output_dir_button.grid(row=2, column=2, padx=10, pady=5)

    tk.Label(stage2_window, text="Путь к файлу input text:").grid(row=3, column=0, sticky=tk.W)
    input_text_entry = tk.Entry(stage2_window, width=50)
    input_text_entry.grid(row=3, column=1, padx=10, pady=5)
    input_text_button = tk.Button(stage2_window, text="Выбрать", command=select_input_text_file)
    input_text_button.grid(row=3, column=2, padx=10, pady=5)

    process_button = tk.Button(stage2_window, text="Пуск", command=process_all)
    process_button.grid(row=4, column=1, pady=20)
    stop_button = tk.Button(stage2_window, text="Стоп", command=stop_processing)
    stop_button.grid(row=4, column=2, pady=20)

    global log_text
    log_text = scrolledtext.ScrolledText(stage2_window, width=80, height=20)
    log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)


def process_stage3():
    def run_wind_ninja(elevation_file, output_path, wind_speed, wind_direction, timestamp, wind_ninja_path, extra_params):
        year = timestamp.year
        month = timestamp.month
        day = timestamp.day
        hour = timestamp.hour
        minute = timestamp.minute

        elevation_file = os.path.normpath(elevation_file)
        output_path = os.path.normpath(output_path)
        wind_ninja_path = os.path.normpath(wind_ninja_path)

        default_params = [
            wind_ninja_path,
            "--num_threads", "4",
            "--elevation_file", elevation_file,
            "--initialization_method", "domainAverageInitialization",
            "--time_zone", "auto-detect",
            "--input_speed", str(wind_speed),
            "--input_speed_units", "mps",
            "--output_speed_units", "mps",
            "--input_direction", str(wind_direction),
            "--uni_air_temp", "35",
            "--air_temp_units", "C",
            "--input_wind_height", "10",
            "--units_input_wind_height", "m",
            "--output_wind_height", "10",
            "--units_output_wind_height", "m",
            "--mesh_resolution", "30",
            "--units_mesh_resolution", "m",
            "--write_ascii_output", "true",
            "--ascii_out_resolution", "30",
            "--units_ascii_out_resolution", "m",
            "--vegetation", "trees",
            "--diurnal_winds", "true",
            "--year", str(year),
            "--month", str(month),
            "--day", str(day),
            "--hour", str(hour),
            "--minute", str(minute),
            "--uni_cloud_cover", "30",
            "--cloud_cover_units", "percent",
            "--output_path", output_path,
            "--number_of_iterations", "300"
        ]

        if extra_params:
            extra_params_list = [param.strip() for param in extra_params.split(",")]
            command = default_params + extra_params_list
        else:
            command = default_params

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            log_message(log_text, line.strip())
        process.wait()
        if process.returncode != 0:
            log_message(log_text, f"Command failed with return code {process.returncode}", error=True)
            raise subprocess.CalledProcessError(process.returncode, command)

    def process_files(tif_dir, csv_dir, wind_ninja_path, extra_params):
        tif_dir = os.path.normpath(tif_dir)
        csv_dir = os.path.normpath(csv_dir)

        tif_files = [f for f in os.listdir(tif_dir) if f.endswith('_utm.tif')]
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

        for csv_file in csv_files:
            csv_path = os.path.join(csv_dir, csv_file)
            wind_data = pd.read_csv(csv_path, sep=';', parse_dates=['time'])

            identifier = csv_file.split('_')[1]

            matching_tif = None
            for tif_file in tif_files:
                if identifier in tif_file:
                    matching_tif = os.path.join(tif_dir, tif_file)
                    break

            if matching_tif:
                output_subdir = os.path.join(tif_dir, csv_file.replace('.csv', ''))
                os.makedirs(output_subdir, exist_ok=True)

                log_message(log_text, f"Начинаю обработку пары {csv_file} и {matching_tif}")

                for i, row in wind_data.iterrows():
                    timestamp = row['time']
                    wind_speed = row['speed']
                    wind_direction = row['dir']
                    log_message(log_text, f"Скорость {wind_speed} и направление {wind_direction} ")
                    run_wind_ninja(matching_tif, output_subdir, wind_speed, wind_direction, timestamp, wind_ninja_path, extra_params)

                log_message(log_text, f"Обработка пары {csv_file} и {matching_tif} завершена")
            else:
                log_message(log_text, f"No matching TIF file found for {csv_file}")

    def select_tif_dir():
        path = filedialog.askdirectory()
        tif_entry.delete(0, tk.END)
        tif_entry.insert(0, path)

    def select_csv_dir():
        path = filedialog.askdirectory()
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, path)

    def select_wind_ninja_path():
        path = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        wind_ninja_entry.delete(0, tk.END)
        wind_ninja_entry.insert(0, path)

    def start_processing():
        tif_dir = tif_entry.get()
        csv_dir = csv_entry.get()
        wind_ninja_path = wind_ninja_entry.get()
        extra_params = params_entry.get()

        if not all([tif_dir, csv_dir, wind_ninja_path]):
            messagebox.showerror("Error", "Please fill all the fields.")
            return

        log_message(log_text, "Processing started...")
        try:
            threading.Thread(target=process_files, args=(tif_dir, csv_dir, wind_ninja_path, extra_params)).start()
        except Exception as e:
            log_message(log_text, f"An error occurred: {e}", error=True)
            messagebox.showerror("Error", f"An error occurred: {e}")



    stage3_window = tk.Toplevel(root)
    stage3_window.title("WindNinja Batch Processor")

    tk.Label(stage3_window, text="TIF Directory:").grid(row=0, column=0, padx=5, pady=5)
    tif_entry = tk.Entry(stage3_window, width=50)
    tif_entry.grid(row=0, column=1, padx=5, pady=5)
    tk.Button(stage3_window, text="Browse", command=select_tif_dir).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(stage3_window, text="CSV Directory:").grid(row=1, column=0, padx=5, pady=5)
    csv_entry = tk.Entry(stage3_window, width=50)
    csv_entry.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(stage3_window, text="Browse", command=select_csv_dir).grid(row=1, column=2, padx=5, pady=5)

    tk.Label(stage3_window, text="WindNinja Executable:").grid(row=2, column=0, padx=5, pady=5)
    wind_ninja_entry = tk.Entry(stage3_window, width=50)
    wind_ninja_entry.grid(row=2, column=1, padx=5, pady=5)
    tk.Button(stage3_window, text="Browse", command=select_wind_ninja_path).grid(row=2, column=2, padx=5, pady=5)

    tk.Label(stage3_window, text="Additional Parameters:").grid(row=3, column=0, padx=5, pady=5)
    params_entry = tk.Entry(stage3_window, width=50)
    params_entry.grid(row=3, column=1, padx=5, pady=5)

    process_button = tk.Button(stage3_window, text="Run", command=start_processing)
    process_button.grid(row=4, column=0, columnspan=3, pady=10)


    global log_text
    log_text = scrolledtext.ScrolledText(stage3_window, width=70, height=20)
    log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5)



# Stage 4: Создание и адаптация растров для использования в модели
def process_stage4():
    def process_wind_data(input_folder_path, output_folder_path, csv_path):
        log_message(log_text, f"Начинаю обработку файлов в {input_folder_path}\n")
        log_text.update()

        wind_data = pd.read_csv(csv_path, delimiter=';')
        wind_data['rounded_speed'] = wind_data['speed'].round().astype(int)
        wind_data['rounded_dir'] = wind_data['dir'].round().astype(int)
        wind_data['time'] = pd.to_datetime(wind_data['time'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
        wind_data['time_for_filename'] = pd.to_datetime(wind_data['time'], format='%Y-%m-%d %H:%M:%S').dt.strftime(
            '%m-%d-%Y_%H%M')

        output_data = {
            "SPEED": {},
            "ANGLE": {}
        }

        for _, row in wind_data.iterrows():
            time_str = row['time_for_filename']
            vel_files = glob.glob(
                os.path.join(input_folder_path, f"*_{row['rounded_dir']}_{row['rounded_speed']}_{time_str}*_vel.asc"))
            ang_files = glob.glob(
                os.path.join(input_folder_path, f"*_{row['rounded_dir']}_{row['rounded_speed']}_{time_str}*_ang.asc"))

            for file_path in vel_files:
                output_file_path = os.path.join(output_folder_path, os.path.basename(file_path).replace('_vel.asc',
                                                                                                        f'_wind_{row["rounded_speed"]}.tif'))
                with rasterio.open(file_path) as src:
                    raster = src.read(1)
                    meta = src.meta
                    crs = src.crs
                meta['crs'] = crs

                with rasterio.open(output_file_path, 'w', **meta) as dst:
                    dst.write(raster, 1)
                output_data["SPEED"][row['time']] = os.path.basename(output_file_path)

            for file_path in ang_files:
                output_file_path = os.path.join(output_folder_path, os.path.basename(file_path).replace('_ang.asc',
                                                                                                        f'_angle_{row["rounded_dir"]}.tif'))
                with rasterio.open(file_path) as src:
                    raster = src.read(1)
                    meta = src.meta
                    crs = src.crs
                meta['crs'] = crs

                with rasterio.open(output_file_path, 'w', **meta) as dst:
                    dst.write(raster, 1)
                output_data["ANGLE"][row['time']] = os.path.basename(output_file_path)

        json_file_name = f"wind_test_{os.path.basename(input_folder_path)}.json"
        json_file_path = os.path.join(output_folder_path, json_file_name)
        with open(json_file_path, 'w') as json_file:
            json.dump(output_data, json_file, indent=4)
        log_message(log_text, f"Создан JSON файл: {json_file_path}\n")
        log_text.update()

    def convert_to_wgs84(directory):
        log_message(log_text, f"Начинаю конвертацию файлов в {directory} в WGS84\n")
        log_text.update()

        for file_name in os.listdir(directory):
            if file_name.endswith('.tif'):
                file_path = os.path.join(directory, file_name)
                src_ds = gdal.Open(file_path)
                if src_ds is None:
                    log_message(log_text, f"Не удалось открыть {file_path}\n")
                    log_text.update()
                    continue

                dst_wkt = 'EPSG:4326'
                temp_file_path = os.path.join(directory, "temp_" + file_name)
                gdal.Warp(temp_file_path, src_ds, dstSRS=dst_wkt)
                src_ds = None

                os.remove(file_path)
                os.rename(temp_file_path, file_path)
                log_message(log_text, f"Конвертирован: {file_path}\n")
                log_text.update()

    def start_process(base_folder_path):
        csv_folder_path = os.path.join(base_folder_path, "filtered")
        output_base_folder_path = os.path.join(base_folder_path, "wind_raster")
        os.makedirs(output_base_folder_path, exist_ok=True)
        folders_to_process = [os.path.join(base_folder_path, folder) for folder in os.listdir(base_folder_path) if
                              folder.startswith("wind_")]

        for folder in folders_to_process:
            folder_name = os.path.basename(folder)
            csv_file_name = "wind_" + folder_name.replace('wind_', '') + ".csv"
            csv_file_path = os.path.join(csv_folder_path, csv_file_name)
            output_folder_path = os.path.join(output_base_folder_path, folder_name)

            if os.path.exists(csv_file_path):
                log_message(log_text, f"Начинаю обработку папки {folder} с файлом {csv_file_path}\n")
                log_text.update()
                os.makedirs(output_folder_path, exist_ok=True)
                process_wind_data(folder, output_folder_path, csv_file_path)
                log_message(log_text, f"Обработка папки {folder} завершена\n")
                log_text.update()

        for folder_name in os.listdir(output_base_folder_path):
            folder_path = os.path.join(output_base_folder_path, folder_name)
            if os.path.isdir(folder_path) and folder_name.startswith("wind_"):
                convert_to_wgs84(folder_path)

        log_message(log_text, "Все процессы завершены.\n")
        log_text.update()

    def run_in_thread(base_folder_path):
        threading.Thread(target=start_process, args=(base_folder_path,)).start()

    def select_folder():
        folder_selected = filedialog.askdirectory()
        entry_base_path.delete(0, tk.END)
        entry_base_path.insert(0, folder_selected)

    def run():
        base_folder_path = entry_base_path.get()
        if not base_folder_path:
            messagebox.showerror("Ошибка", "Выберите путь к папке.")
            return

        log_text.delete(1.0, tk.END)
        run_in_thread(base_folder_path)

    stage4_window = tk.Toplevel(root)
    stage4_window.title("Создание и адаптация растров для использования в модели")

    frame = tk.Frame(stage4_window)
    frame.pack(padx=10, pady=10)

    label_base_path = tk.Label(frame, text="Путь к папке:")
    label_base_path.grid(row=0, column=0, sticky="e")

    entry_base_path = tk.Entry(frame, width=50)
    entry_base_path.grid(row=0, column=1, padx=5)

    button_browse = tk.Button(frame, text="Выбрать", command=select_folder)
    button_browse.grid(row=0, column=2, padx=5)

    button_start = tk.Button(frame, text="Пуск", command=run)
    button_start.grid(row=1, column=0, columnspan=3, pady=10)

    global log_text
    log_text = scrolledtext.ScrolledText(stage4_window, width=80, height=20)
    log_text.pack(padx=10, pady=10)

root = tk.Tk()
root.title("Генерация полей ветра")
root.geometry("600x450")
root.configure(bg="#f0f0f0")

header_font = font.Font(family="Helvetica", size=16, weight="bold")
button_font = font.Font(family="Helvetica", size=12)

header_label = tk.Label(root, text="Выбор этапа:", font=header_font, bg="#f0f0f0")
header_label.pack(pady=20)

button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.pack(pady=10)

stage1_button = tk.Button(button_frame, text="1) Обрезка и перепроекция изображения ASTGTM2", font=button_font, command=process_stage1, wraplength=400, justify="left")
stage1_button.pack(pady=5, fill=tk.X)

stage2_button = tk.Button(button_frame, text="2) Создание файла с метеоданными", font=button_font, command=process_stage2, wraplength=400, justify="left")
stage2_button.pack(pady=5, fill=tk.X)

stage3_button = tk.Button(button_frame, text="3) Генерация модельных полей ветра (Windninja)", font=button_font, command=process_stage3, wraplength=400, justify="left")
stage3_button.pack(pady=5, fill=tk.X)

stage4_button = tk.Button(button_frame, text="4) Создание и адаптация растров для использования в модели", font=button_font, command=process_stage4, wraplength=400, justify="left")
stage4_button.pack(pady=5, fill=tk.X)

root.mainloop()
