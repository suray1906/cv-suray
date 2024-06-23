import os
import json

# Список каталогов для обработки
root_directory = "C:\\work\\fire_model\\1\\wind_wsg"




def clean_directory(directory):
    # Имя JSON файла
    json_file_name = "wind_test_" + os.path.basename(directory) + ".json"
    json_file_path = os.path.join(directory, json_file_name)

    # Загружаем JSON файл
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # Список нужных файлов .tif и .prj
    relevant_files = set()
    for key in data.keys():
        relevant_files.update(data[key].values())

    # Добавляем соответствующие .prj файлы
    relevant_files.update([f.replace('.tif', '.prj') for f in relevant_files])

    # Список всех файлов в каталоге
    all_files = set(os.listdir(directory))

    # Определяем файлы для удаления
    files_to_delete = all_files - relevant_files - {json_file_name}

    # Удаляем ненужные файлы
    for file_name in files_to_delete:
        file_path = os.path.join(directory, file_name)
        os.remove(file_path)
        print(f"Удалён: {file_path}")


# Обрабатываем каждый каталог
for folder_name in os.listdir(root_directory):
    folder_path = os.path.join(root_directory, folder_name)
    if os.path.isdir(folder_path) and folder_name.startswith("wind_"):
        clean_directory(folder_path)

print("Очистка каталогов завершена.")
