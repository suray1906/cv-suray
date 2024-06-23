import re
import os

# Path to the wind_test directory
wind_test_directory = r'C:\work\fire_model\model\wind_test'

# Example wind_test folders (this should be replaced with actual OS directory reading)
wind_test_folders = [
    "wind_209908_2019-07-02_23_00_00",
    "wind_210990_2019-06-23_01_00_00",
    "wind_210990_2019-06-28_23_00_00",
    "wind_213288_2019-06-29_04_00_00",
    "wind_213288_2019-07-07_23_00_00",
    "wind_214522_2019-06-30_02_00_00",
    "wind_214522_2019-07-02_23_00_00",
    "wind_216783_2019-07-02_04_00_00",
    "wind_216783_2019-07-14_23_00_00",
    "wind_218735_2019-07-04_03_00_00",
    "wind_218735_2019-07-08_23_00_00",
    "wind_218808_2019-07-05_04_00_00",
    "wind_218808_2019-07-07_23_00_00",
    "wind_219555_2019-07-05_04_00_00",
    "wind_219555_2019-07-07_23_00_00",
    "wind_219757_2019-07-19_04_00_00",
    "wind_219757_2019-07-21_04_00_00",
    "wind_219757_2019-07-31_23_00_00",
    "wind_220983_2019-07-19_04_00_00",
    "wind_220983_2019-08-11_23_00_00",
    "wind_209908_2019-06-30_02_00_00"
]


def update_fire_model_parameters(file_path, wind_test_folders):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []

    for line in lines:
        match = re.search(r'#fire_id#: (\d+),.*#dt_end#: #(\d{4}-\d{2}-\d{2}) ', line)
        if match:
            fire_id = match.group(1)
            dt_end_date = match.group(2)
            wind_folder_name = None

            # Find the corresponding wind_test folder
            for folder in wind_test_folders:
                if fire_id in folder and dt_end_date in folder:
                    wind_folder_name = folder
                    break

            if wind_folder_name:
                wind_raster_filename = f'#wind_raster_filename#:#wind_test/{wind_folder_name}/wind_test_{wind_folder_name}.json#, '
                # Insert the new parameter before #sql_cache_location#
                line = line.replace('#sql_cache_location#', f'{wind_raster_filename}#sql_cache_location#')

        updated_lines.append(line)

    output_file_path = file_path.replace('.txt', '_updated.txt')
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(updated_lines)

    return output_file_path

# Uncomment the following line to run the function
# updated_file = update_fire_model_parameters('/mnt/data/2024.05.11_list.txt', wind_test_folders)
# updated_file
