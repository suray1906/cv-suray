import os
import csv
import pandas as pd
from datetime import datetime

# Функция для фильтрации данных по времени
def filter_time(data, start_dt, end_dt):
    return data[(data['time'] >= start_dt) & (data['time'] <= end_dt)]

# Чтение данных из текстового файла
input_text_file = r"C:\work\fire_model\1\gran\2024.05.11_list.txt"
with open(input_text_file, 'r') as file:
    lines = file.readlines()

# Папка с исходными CSV файлами
csv_dir = r"C:\work\fire_model\1\123"
output_dir = r"C:\work\fire_model\1\123\filtered"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Обработка каждого абзаца в текстовом файле
for line in lines:
    if not line.strip():
        continue

    # Парсинг строки для получения значений fire_id, dt_begin и dt_end
    try:
        parts = line.split(',')
        fire_id = int(parts[0].split(':')[1].strip())
        dt_begin = parts[1].split(':')[1].strip().strip('#')
        dt_end = parts[2].split(':')[1].strip().strip('#')

        start_dt = datetime.fromisoformat(dt_begin)
        end_dt = datetime.fromisoformat(dt_end)

        # Открытие соответствующего CSV файла
        input_csv_file = os.path.join(csv_dir, f"wind_{fire_id}.csv")
        if not os.path.exists(input_csv_file):
            print(f"CSV file for fire_id {fire_id} does not exist.")
            continue

        data = pd.read_csv(input_csv_file, delimiter=';', parse_dates=['time'])

        # Фильтрация данных по времени
        filtered_data = filter_time(data, start_dt, end_dt)

        # Сохранение отфильтрованных данных в новый CSV файл
        output_csv_file = os.path.join(output_dir, f"wind_{fire_id}_{end_dt.strftime('%Y-%m-%d_%H_%M_%S')}.csv")
        filtered_data.to_csv(output_csv_file, index=False, sep=';')
        print(f"Processed fire_id {fire_id}: saved to {output_csv_file}")

    except Exception as e:
        print(f"Error processing line: {line}")
        print(e)

print("Обработка завершена.")
