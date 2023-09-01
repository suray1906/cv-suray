import os
import uuid
import numpy as np
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import shutil

input_file_path = "input_file.bin"
output_file_path = "sorted_output_file.bin"
tmp_dir = "tmp/"

if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

def sort(input_file, start, end):
    print(f"Sorting chunk starting at {start} and ending at {end}")
    with open(input_file, 'rb') as f:
        f.seek(start)
        chunk = np.frombuffer(f.read(end - start), dtype=np.int32)
        if len(chunk) > 0:
            sorted_chunk = np.sort(chunk)
            chunk_name = tmp_dir + uuid.uuid4().hex + ".bin"
            with open(chunk_name, "wb+") as wf:
                wf.write(sorted_chunk.tobytes())
            return chunk_name

def merge(first_file, second_file):
    print("Merging files")

    with open(first_file, "rb") as f1:
        with open(second_file, "rb") as f2:
            l1 = np.frombuffer(f1.read(), dtype=np.int32)
            l2 = np.frombuffer(f2.read(), dtype=np.int32)

            result = np.concatenate((l1, l2))
            result.sort()

            file_name = tmp_dir + uuid.uuid4().hex + ".bin"
            with open(file_name, "wb+") as wf:
                wf.write(result.tobytes())

    os.remove(first_file)
    os.remove(second_file)

    return file_name

def merge_files(sorted_files):
    while len(sorted_files) > 1:
        with ProcessPoolExecutor() as executor:
            merged_files = list(executor.map(merge, sorted_files[0::2], sorted_files[1::2]))
        sorted_files = merged_files

    return sorted_files[0]

if __name__ == '__main__':
    try:
        max_memory = 256 * 1024 * 1024  # 256 MB
        file_size = os.path.getsize(input_file_path)
        chunk_size = min(128 * 1024 * 1024, file_size // (file_size // (128 * 1024 * 1024)))

        chunks = [(i, min(i + chunk_size, file_size)) for i in range(0, file_size, chunk_size)]

        with ProcessPoolExecutor() as executor:
            sorted_files = list(executor.map(sort, [input_file_path] * len(chunks), [chunk[0] for chunk in chunks], [chunk[1] for chunk in chunks]))

        while len(sorted_files) > 1:
            first_file = sorted_files.pop(0)
            second_file = sorted_files.pop(0)
            sorted_files.append(merge(first_file, second_file))

        final_file_name = sorted_files[0]
        shutil.move(final_file_name, output_file_path)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Чистка
        try:
            shutil.rmtree(tmp_dir)
        except OSError as e:
            print(f"Error removing temporary directory: {e}")
