import random
import time
from datetime import datetime
from multiprocessing import Process, Manager, Event
import tkinter as tk
from tkinter import ttk


class Leader:
    def __init__(self, id, sleep_time, event):
        self.id = id
        self.sleep_time = sleep_time
        self.follower = None
        self.event = event

    def run(self, update_ui):
        for _ in range(5):
            update_ui((self.id, None, True))
            time.sleep(self.sleep_time)
            update_ui((self.id, None, False))
            sleep_time_str = datetime.now().strftime("%H:%M.%S")
            m = random.randint(1, self.sleep_time - 1)
            message = f"Leader #{self.id}\n{sleep_time_str} ушел спать на {self.sleep_time} секунды\n{sleep_time_str} проснулся и отправил Follower #{self.id} число {m}"
            update_ui((self.id, message, None))
            self.follower.receive_message(m, update_ui)
            self.event.wait()
            self.event.clear()

    def set_follower(self, follower):
        self.follower = follower


class Follower:
    def __init__(self, id, leader, event):
        self.id = id
        self.leader = leader
        self.event = event

    def receive_message(self, sleep_time, update_ui):
        sleep_time_str = datetime.now().strftime("%H:%M.%S")
        message = f"Follower #{self.id}\n{sleep_time_str} получил сообщение и спит {sleep_time} секунд"
        update_ui((self.id + 3, message, True))  # Измените здесь
        time.sleep(sleep_time)
        update_ui((self.id + 3, None, False))  # И здесь
        self.event.set()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Leader-Follower")

        self.leader_labels = []
        self.follower_labels = []
        self.message_boxes = []

        for i in range(3):
            leader_label = ttk.Label(self, text=f"Leader {i}", background="red")
            leader_label.grid(row=0, column=i)
            self.leader_labels.append(leader_label)

            follower_label = ttk.Label(self, text=f"Follower {i}", background="red")
            follower_label.grid(row=1, column=i)
            self.follower_labels.append(follower_label)

            message_box = tk.Text(self, wrap=tk.WORD, width=30, height=25)
            message_box.grid(row=2, column=i)
            self.message_boxes.append(message_box)

        # Виджет Label для вывода количества завершенных циклов
        self.cycle_count_label = ttk.Label(self, text="0", font=("Arial", 16))
        self.cycle_count_label.grid(row=3, column=1)

    def update_ui(self, id, message=None, sleeping=None):
        if id < 3:
            label = self.leader_labels[id]
        else:
            label = self.follower_labels[id - 3]

        if sleeping is not None:
            label.config(background="green" if not sleeping else "red")

        if message:
            message_box = self.message_boxes[id if id < 3 else id - 3]
            message_box.insert(tk.END, message + "\n\n")
            message_box.see(tk.END)

        self.update()




def main():
    app = Application()

    # Создайте `Event` для каждого лидера и последователя
    events = [Event() for _ in range(3)]

    leaders = [Leader(id=i, sleep_time=random.randint(3, 10), event=event) for i, event in enumerate(events)]
    followers = [Follower(id=i, leader=leader, event=event) for i, (leader, event) in enumerate(zip(leaders, events))]

    for leader, follower in zip(leaders, followers):
        leader.set_follower(follower)

    update_ui_queue = Manager().Queue()

    processes = [Process(target=leader.run, args=((update_ui_queue.put,))) for leader in leaders]

    for process in processes:
        process.daemon = True
        process.start()

    cycle_count = 0

    def process_ui_updates():
        nonlocal cycle_count
        try:
            while True:
                id, message, sleeping = update_ui_queue.get(block=False)
                app.update_ui(id, message, sleeping)

                # Если цикл завершен, увеличиваем счетчик
                if message and "ушел спать" in message:
                    cycle_count += 1
                    app.cycle_count_label.config(text=str(cycle_count))

                time.sleep(0.1)
        except Exception as e:
            app.after(100, process_ui_updates)

    app.after(100, process_ui_updates)
    app.mainloop()

    for process in processes:
        process.join()



if __name__ == "__main__":
    main()
