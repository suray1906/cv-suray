import subprocess
import pandas as pd
import os
from datetime import datetime


def run_wind_ninja(elevation_file, output_path, wind_speed, wind_direction, timestamp):
    year = timestamp.year
    month = timestamp.month
    day = timestamp.day
    hour = timestamp.hour
    minute = timestamp.minute

    command = [
        r"C:\work\fire_model\WindNinja-3.10.0\bin\WindNinja_cli.exe",
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

    subprocess.run(command, check=True)


# Paths to the directories
tif_dir = "C:\\work\\fire_model\\1\\utm"
csv_dir = "C:\\work\\fire_model\\1\\utm\\filtered"

# Get list of all .tif files and .csv files
tif_files = [f for f in os.listdir(tif_dir) if f.endswith('_utm.tif')]
csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

# Process each CSV file
for csv_file in csv_files:
    csv_path = os.path.join(csv_dir, csv_file)
    wind_data = pd.read_csv(csv_path, sep=';', parse_dates=['time'])

    # Extract identifier to match with tif files
    identifier = csv_file.split('_')[1]

    # Find the matching tif file
    matching_tif = None
    for tif_file in tif_files:
        if identifier in tif_file:
            matching_tif = os.path.join(tif_dir, tif_file)
            break

    if matching_tif:
        # Create output directory with the same name as the CSV file
        output_subdir = os.path.join(tif_dir, csv_file.replace('.csv', ''))
        os.makedirs(output_subdir, exist_ok=True)

        print(f"Начинаю обработку пары {csv_file} и {matching_tif}")

        for i, row in wind_data.iterrows():
            timestamp = row['time']
            wind_speed = row['speed']
            wind_direction = row['dir']
            print(f"Скорость {wind_speed} и направление {wind_direction} ")
            run_wind_ninja(matching_tif, output_subdir, wind_speed, wind_direction, timestamp)

        print(f"Обработка пары {csv_file} и {matching_tif} завершена")
    else:
        print(f"No matching TIF file found for {csv_file}")
