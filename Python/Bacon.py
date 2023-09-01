from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def open_file():
    filepath = filedialog.askopenfilename()
    if filepath != "":
        with open(filepath, "r") as file:
            data = json.load(file)
            print("Successful file upload!")
    fig = plt.figure(figsize=(8, 4))
    G = nx.Graph()

    for actor in data:
        G.add_node(actor['name'])
    for actor1 in data:
        for actor2 in data:
            if actor1['name'] == actor2['name']:
                continue
            for film1 in actor1['films']:
                for film2 in actor2['films']:
                    if film1['title'] == film2['title']:
                        G.add_edge(actor1['name'], actor2['name'], film=film1['title'])
    name = []
    for names_actors in data:
        name.append(names_actors['name'])
        combo_names = Combobox(root)

        def selected_name(event):
            selection_name = combo_names.get()
            print(selection_name)
            shortest_path = nx.shortest_path(G, selection_name, 'Kevin Bacon')
            lbl_number_bacon.configure(text=f"Число Бейкона: {len(shortest_path) - 1}")

            ONE = 1
            output_lbl11 = Label(root, text="Path from")
            output_lbl12 = Label(root, text=selection_name)
            output_lbl13 = Label(root, text="to Kevin Bacon:")
            output_lbl11.grid(row=4, column=0 + ONE, sticky=W)
            output_lbl12.grid(row=4, column=1 + ONE, sticky=W)
            output_lbl13.grid(row=4, column=2 + ONE, sticky=E)

            for i in range(len(shortest_path) - 1):
                u = shortest_path[i]
                v = shortest_path[i + 1]
                film = G[u][v]['film']
                output_lbl21 = Label(root, text=u)
                output_lbl22 = Label(root, text="was in")
                output_lbl23 = Label(root, text=film)
                output_lbl24 = Label(root, text="with")
                output_lbl25 = Label(root, text=v)
                output_lbl21.grid(row=5 + i, column=0 + ONE, sticky=W)
                output_lbl22.grid(row=5 + i, column=1 + ONE, sticky=W)
                output_lbl23.grid(row=5 + i, column=2 + ONE, sticky=W)
                output_lbl24.grid(row=5 + i, column=3 + ONE, sticky=W)
                output_lbl25.grid(row=5 + i, column=4 + ONE, sticky=E)

                output_lbl31 = Label(root, text=selection_name)
                output_lbl32 = Label(root, text="'s Bacon number is")
                output_lbl33 = Label(root, text=len(shortest_path) - 1)
                output_lbl31.grid(row=6 + i, column=0 + ONE, sticky=W)
                output_lbl32.grid(row=6 + i, column=1 + ONE, sticky=W)
                output_lbl33.grid(row=6 + i, column=2 + ONE, sticky=E)

            prev_shortest_path = []
            for u, v, film in G.edges(data=True):
                if (u in shortest_path) and (v in shortest_path):
                    G[u][v]['edge_color'] = 'red'
                else:
                    G[u][v]['edge_color'] = 'yellow'
            fig.canvas.draw()

            for u, v, film in prev_shortest_path:
                G[u][v]['edge_color'] = 'yellow'

            prev_shortest_path = shortest_path

            nx.draw(G, pos, with_labels=True, node_color="blue",
                    edge_color=[G[u][v]['edge_color'] for u, v in G.edges()], width=2)
            canvas.draw()

    combo_names['values'] = name
    combo_names.current(0)
    combo_names.grid(row=3, column=1, columnspan=2, pady=5)
    actor = combo_names.get()
    print(actor)
    combo_names.bind("<<ComboboxSelected>>", selected_name)

    seed = 1
    pos = nx.spring_layout(G, seed=seed)


    nx.draw(G, pos, with_labels=True, node_color="blue", edge_color="yellow", width=2)
    canvas = FigureCanvasTkAgg(fig, root)
    canvas.get_tk_widget().grid(column=1, row=2, columnspan=16)
    canvas.draw()
    return data


root = Tk()
root.title("Kevin Bacon")
root.geometry("850x550")
load_button = Button(text="Load", command=open_file)
load_button.grid(column=0, row=0, padx=5, pady=5)
lbl_number_bacon = Label(root, font=("Arial Bold", 10))
lbl_number_bacon.grid(column=1, row=1, pady=5)
root.mainloop()