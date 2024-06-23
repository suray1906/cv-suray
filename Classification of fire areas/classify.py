import rasterio
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from rasterio.plot import show
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Устанавливаем переменную среды с путем к proj.db
os.environ['PROJ_LIB'] = r"C:\ProgramData\Anaconda3\envs\fireproj\Library\share\proj"


class FireClassificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик изображений классификации пожара")
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=1)

        canvas = tk.Canvas(main_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        tk.Label(frame, text="Путь к RGB изображению:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_rgb = tk.Entry(frame, width=50)
        self.entry_rgb.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(frame, text="Обзор", command=lambda: self.entry_rgb.insert(0, self.select_file())).grid(row=0,
                                                                                                          column=2,
                                                                                                          padx=5,
                                                                                                          pady=5)

        tk.Label(frame, text="Путь к NBR изображению:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nbr = tk.Entry(frame, width=50)
        self.entry_nbr.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame, text="Обзор", command=lambda: self.entry_nbr.insert(0, self.select_file())).grid(row=1,
                                                                                                          column=2,
                                                                                                          padx=5,
                                                                                                          pady=5)

        tk.Label(frame, text="Путь к выходному изображению:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_output = tk.Entry(frame, width=50)
        self.entry_output.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(frame, text="Обзор", command=lambda: self.entry_output.insert(0, self.select_output_file())).grid(
            row=2, column=2, padx=5, pady=5)

        tk.Label(frame, text="Путь к изображению предыдущей классификации пожара (опционально):").grid(row=3, column=0,
                                                                                                       padx=5, pady=5)
        self.entry_prev = tk.Entry(frame, width=50)
        self.entry_prev.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(frame, text="Обзор", command=lambda: self.entry_prev.insert(0, self.select_file())).grid(row=3,
                                                                                                           column=2,
                                                                                                           padx=5,
                                                                                                           pady=5)

        tk.Label(frame, text="Пороговые значения для pre_fire_mask:").grid(row=4, column=0, padx=5, pady=5)
        self.entry_pre_fire_mask = scrolledtext.ScrolledText(frame, width=50, height=1)
        self.entry_pre_fire_mask.insert(tk.INSERT,
                                        "(red_channel >= 500) & (red_channel <= 1000) & (elev_channel >= 600) & (elev_channel <= 1300)")
        self.entry_pre_fire_mask.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(frame, text="Пороговые значения для non_fuel_mask:").grid(row=5, column=0, padx=5, pady=5)
        self.entry_non_fuel_mask = scrolledtext.ScrolledText(frame, width=50, height=1)
        self.entry_non_fuel_mask.insert(tk.INSERT, "(nbr_data >= -1) & (nbr_data <= -0.65)")
        self.entry_non_fuel_mask.grid(row=5, column=1, padx=5, pady=5)

        tk.Label(frame, text="Пороговые значения для опциональной классификации:").grid(row=6, column=0, padx=5, pady=5)
        self.entry_optional_mask = scrolledtext.ScrolledText(frame, width=50, height=1)
        self.entry_optional_mask.insert(tk.INSERT, "(nbr_data >= 0.5) & (nbr_data <= 0.6)")
        self.entry_optional_mask.grid(row=6, column=1, padx=5, pady=5)

        tk.Button(frame, text="Запуск", command=self.run_script).grid(row=7, column=0, columnspan=3, pady=10)

        self.fig, self.ax = plt.subplots(1, 1, figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=3)

        self.min_max_text = tk.Text(frame, width=100, height=6)
        self.min_max_text.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

    def select_file(self):
        return filedialog.askopenfilename()

    def select_output_file(self):
        return filedialog.asksaveasfilename(defaultextension=".tif")

    def run_script(self):
        rgb_image_path = self.entry_rgb.get()
        nbr_image_path = self.entry_nbr.get()
        output_image_path = self.entry_output.get()
        prev_image_path = self.entry_prev.get()

        pre_fire_mask_expr = self.entry_pre_fire_mask.get("1.0", tk.END).strip()
        non_fuel_mask_expr = self.entry_non_fuel_mask.get("1.0", tk.END).strip()
        optional_mask_expr = self.entry_optional_mask.get("1.0", tk.END).strip()

        if not rgb_image_path or not nbr_image_path or not output_image_path:
            print("Пожалуйста, выберите все необходимые пути к файлам.")
            return

        if prev_image_path:
            self.process_images(rgb_image_path, nbr_image_path, output_image_path, pre_fire_mask_expr,
                                non_fuel_mask_expr, optional_mask_expr, prev_image_path)
        else:
            self.process_images(rgb_image_path, nbr_image_path, output_image_path, pre_fire_mask_expr,
                                non_fuel_mask_expr, optional_mask_expr)

    def process_images(self, rgb_image_path, nbr_image_path, output_image_path, pre_fire_mask_expr, non_fuel_mask_expr,
                       optional_mask_expr, prev_image_path=None):
        # Открываем RGB изображение и извлекаем каналы
        with rasterio.open(rgb_image_path) as rgb_src:
            red_channel = rgb_src.read(1)
            elev_channel = rgb_src.read(2)
            print("RGB изображение успешно прочитано.")
            min_red = np.min(red_channel[red_channel != rgb_src.nodata])
            max_red = np.max(red_channel[red_channel != rgb_src.nodata])
            min_elev = np.min(elev_channel[elev_channel != rgb_src.nodata])
            max_elev = np.max(elev_channel[elev_channel != rgb_src.nodata])

        # Открываем NBR изображение
        with rasterio.open(nbr_image_path) as nbr_src:
            nbr_data = nbr_src.read(1)
            print("NBR изображение успешно прочитано.")
            min_nbr = np.min(nbr_data[nbr_data != nbr_src.nodata])
            max_nbr = np.max(nbr_data[nbr_data != nbr_src.nodata])

            # Подготавливаем выходное изображение на основе свойств NBR изображения
            meta = nbr_src.meta.copy()
            meta.update(dtype=rasterio.float64, count=1, crs='EPSG:4326')

            # Инициализируем классификационное изображение значениями 'no data'
            classification_image = np.full(nbr_data.shape, -3, dtype=np.float64)



            pre_fire_mask = eval(pre_fire_mask_expr)
            classification_image[pre_fire_mask] = -1
            print("Область до пожара классифицирована.")

            if optional_mask_expr:
                optional_mask = eval(optional_mask_expr)
                classification_image[optional_mask] = -1
                print("Дополнительная классификация выполнена.")

            active_fire_mask = nbr_data > 0
            classification_image[active_fire_mask] = 0
            print("Активная область пожара классифицирована.")

            non_fuel_mask = eval(non_fuel_mask_expr)
            classification_image[non_fuel_mask] = -3
            print("Не горючая область классифицирована.")

            if prev_image_path:
                with rasterio.open(prev_image_path) as prev_src:
                    prev_channel = prev_src.read(1)
                    print("Изображение предыдущей классификации пожара успешно прочитано.")
                    prev_fire_mask = prev_channel == -1
                    classification_image[prev_fire_mask] = -1
                    print("Область предыдущего пожара классифицирована.")            

            classification_image[red_channel == rgb_src.nodata] = -3
            classification_image[nbr_data == nbr_src.nodata] = -3
            print("Области с 'no data' обработаны.")

        self.update_min_max_text(min_red, max_red, min_elev, max_elev, min_nbr, max_nbr)
        self.update_plot(classification_image, nbr_src.transform, nbr_src.width, nbr_src.height)

        # Только сохраняем, если результат удовлетворителен
        if messagebox.askyesno("Сохранение", "Сохранить результат?"):
            with rasterio.open(output_image_path, 'w', **meta) as out_dst:
                out_dst.write(classification_image, 1)
            print(f"Выходное изображение сохранено в {output_image_path}")

    def update_min_max_text(self, min_red, max_red, min_elev, max_elev, min_nbr, max_nbr):
        self.min_max_text.delete("1.0", tk.END)
        self.min_max_text.insert(tk.END, f"Красный канал: min={min_red}, max={max_red}\n")
        self.min_max_text.insert(tk.END, f"SWIR1 канал (11): min={min_elev}, max={max_elev}\n")
        self.min_max_text.insert(tk.END, f"NBR данные: min={min_nbr}, max={max_nbr}\n")

    def update_plot(self, classification_image, transform, width, height):
        self.ax.clear()
        extent = [
            transform[2],
            transform[2] + transform[0] * width,
            transform[5] + transform[4] * height,
            transform[5]
        ]
        self.ax.imshow(classification_image, cmap='viridis', extent=extent)
        self.ax.set_title("Классификационное изображение")
        self.ax.set_xlabel("Долгота")
        self.ax.set_ylabel("Широта")
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = FireClassificationApp(root)
    root.mainloop()
