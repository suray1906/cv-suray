import os
import json

# Путь к корневой папке
root_path = r"C:\work\fire_model\1\wind_wsg"


def process_json_files(root_path):
    # Проходим по всем папкам в корневой папке
    for folder_name in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder_name)
        if os.path.isdir(folder_path):
            # Ищем JSON-файл в текущей папке
            for file_name in os.listdir(folder_path):
                if file_name.endswith('.json'):
                    json_file_path = os.path.join(folder_path, file_name)
                    print(f"Processing {json_file_path}")
                    # Загружаем содержимое JSON-файла
                    with open(json_file_path, 'r', encoding='utf-8') as json_file:
                        data = json.load(json_file)

                    # Изменяем пути к изображениям в JSON
                    for key in data:
                        for timestamp in data[key]:
                            original_tif = data[key][timestamp]
                            new_tif_path = f"wind_test/{folder_name}/{original_tif}"
                            data[key][timestamp] = new_tif_path

                    # Сохраняем измененный JSON-файл
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(data, json_file, indent=4, ensure_ascii=False)
                    print(f"Updated {json_file_path}")


# Выполняем обработку
process_json_files(root_path)
