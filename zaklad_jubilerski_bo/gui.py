""" Rafal711 """


import tkinter as tk
import numpy as np
from tkinter import Tk, Label, Button, ttk, IntVar, Checkbutton, Radiobutton, Entry, Toplevel, END, filedialog, messagebox, Text
import pathlib
import pandas as pd
from struktury import mat3d_to_2d
from algorytm_SA import run_algorithm
import matplotlib.pyplot as plt
import matplotlib
from prettytable import PrettyTable


class App:
    def __init__(self, master: Tk):
        self.master = master

        # main window
        w, h = 800, 600
        ws = master.winfo_screenwidth()
        hs = master.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        master.title('Zakład Jubilerski "Złote a skromne"')

        font0 = "Helvetica 15 bold"
        space = Label(master, text='\nProblem optymalizacji procesu produkcyjnego\nAlgorytm SA \n\n', font=font0)
        space.grid(column=2, row=0, columnspan=3)
        font1 = "Helvetica 10 bold"


        # main screen grid
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(2, weight=1)
        master.columnconfigure(3, weight=1)
        master.columnconfigure(4, weight=2)
        master.columnconfigure(5, weight=1)


        # environment: checkbuttons titles
        env_label0 = Label(master, text="Otoczenie Kupna", font=font1)
        env_label0.grid(column=1, row=1, columnspan=1, padx=1, pady=1, sticky=tk.W)

        env_label1 = Label(master, text="Otoczenie Produkcji", font=font1)
        env_label1.grid(column=2, row=1, columnspan=1, padx=1, pady=1, sticky=tk.W)

        env_label2 = Label(master, text="Otoczenie Sprzedaży", font=font1)
        env_label2.grid(column=3, row=1, columnspan=1, padx=1, pady=1, sticky=tk.W)


        # environment: Check buttons
        env_size = (3, 3)
        env = np.zeros(env_size, dtype=object)
        CheckVarLab = ['purchase', 'production', 'sales']

        self.CheckVarEnv = {CheckVarLab[0]: [IntVar() for _ in range(env_size[0])],
                            CheckVarLab[1]: [IntVar() for _ in range(env_size[0])],
                            CheckVarLab[2]: [IntVar() for _ in range(env_size[0])]}

        for i in range(env_size[1]):
            for j in range(env_size[0]):
                env[j, i] = Checkbutton(master, text=f"Otoczenie {j+1}", variable=self.CheckVarEnv[CheckVarLab[i]][j],
                                onvalue=1, offvalue=0, height=2, width=8)
                env[j, i].grid(column=i+1, row=j+2, padx=1, pady=1, sticky=tk.W)


        # Start solution:
        space = Label(master, text='\n\n')
        space.grid(column=1, row=6, padx=1, pady=1)

        st_sol_lab = Label(master, text="Rozwiązanie startowe", font=font1)
        st_sol_lab.grid(column=1, row=7, padx=1, pady=1, sticky=tk.W)

        # Start solution: Radio buttons
        st_sol_size = (2, 1)
        st_sol = np.zeros(env_size, dtype=object)
        st_opt_str = ['losowe', 'najlepsze kwartały']

        self.RadVarStSol = IntVar()

        for i in range(st_sol_size[1]):
            for j in range(st_sol_size[0]):
                st_sol = Radiobutton(master, text=st_opt_str[j], variable=self.RadVarStSol, value=j)
                st_sol.grid(column=i+1, row=j+8, padx=1, pady=1, sticky=tk.W)


        # Surrounding method
        st_sol_lab = Label(master, text="Wybór otoczenia", font=font1)
        st_sol_lab.grid(column=2, row=7, padx=1, pady=1, sticky=tk.W)

        surr_opt_size = (2, 1)
        surr_opt = np.zeros(surr_opt_size, dtype=object)
        surr_opt_str = ['losowy', 'najlepszy']

        self.RadVarSurr = IntVar()

        for i in range(surr_opt_size[1]):
            for j in range(surr_opt_size[0]):
                surr_opt = Radiobutton(master, text=surr_opt_str[j], variable=self.RadVarSurr, value=j)
                surr_opt.grid(column=i+2, row=j+8, padx=1, pady=1, sticky=tk.W)


        # Start - Structure method
        lf_lab = Label(master, text="Struktury", font=font1)
        lf_lab.grid(column=3, row=7, padx=1, pady=1, sticky=tk.W)

        lf_size = (2, 1)
        lf = np.zeros(surr_opt_size, dtype=object)
        lf_str = ['losowe', 'z pliku']

        self.RadVarStruct = IntVar()

        for i in range(lf_size[1]):
            for j in range(lf_size[0]):
                lf = Radiobutton(master, text=lf_str[j], variable=self.RadVarStruct, value=j)
                lf.grid(column=i+3, row=j+8, padx=1, pady=1, sticky=tk.W)


        # Parameters
        parm_size = (5, 1)
        self.Parameters = np.zeros(parm_size[0], dtype=object)
        parm_title = Label(master, text='Parametry', font=font1)
        parm_title.grid(column=5, row=4, padx=1, pady=1)

        # Parameters: labels and entries
        parm_lab = np.zeros(parm_size[0], dtype=object)
        parm_lab[0] = Label(master, text='alfa')
        parm_lab[1] = Label(master, text='temp. startowa')
        parm_lab[2] = Label(master, text='liczba it. w jednej temp.')
        parm_lab[3] = Label(master, text='kryterium stopu 1:')
        parm_lab[4] = Label(master, text='kryterium stopu 2:')
        default_val = [0.9, 1000, 10, 10, 15]

        for i in range(parm_size[0]):
            parm_lab[i].grid(column=4, row=i+5, padx=1, pady=1, sticky=tk.E)
            self.Parameters[i] = Entry(master, bd=5)
            self.Parameters[i].insert(END, default_val[i])
            self.Parameters[i].grid(column=5, row=i+5, padx=1, pady=1, sticky=tk.W)

        self.File_name = r'dane_struktur.xlsx'

        # Button hits
        def button1_hit():
            # sprawdzenie czy otoczenia są wypełnione
            for name in CheckVarLab:
                is_empty = [True if v.get() == 0 else False for v in self.CheckVarEnv[name]]
                if np.all(is_empty):
                    messagebox.showerror("Informacja", "Wybierz wszędzie przynajmniej jedno otoczenie")
                    return None

            # uruchomienie algorytmu
            try:
                best_sol, fc_data, fc_best_data = run_algorithm(self.CheckVarEnv, self.Parameters, self.RadVarStSol,
                                                                self.RadVarSurr, self.File_name, self.RadVarStruct)
            except ValueError:
                messagebox.showerror("Informacja", "Rozwiązanie startowe nie spełnia ograniczeń!\nSpróbuj ponownie")
                return None

            # Wypisanie rozwiązania
            print_sol(best_sol)

            # wykres przebiegu funkcji celu
            fig, ax = plt.subplots(figsize=(8, 5.6))
            backend = matplotlib.get_backend()
            if backend == 'TkAgg':
                fig.canvas.manager.window.wm_geometry("+%d+%d" % (x+400, y))
            elif backend == 'WXAgg':
                fig.canvas.manager.window.SetPosition("+%d+%d" % (x+400, y))
            else:
                fig.canvas.manager.window.move("+%d+%d" % (x+400, y))

            fc_best = list(map(list, list(zip(*fc_best_data))))
            fc = list(zip(*fc_data))
            fc_best[0].append(fc_best[0][-1])
            fc_best[1].append(fc[1][-1])

            ax.plot(fc[1], fc[0], label='fc')
            ax.plot(fc_best[1], fc_best[0], label='fc_best')
            ax.set_title("Przebieg funkcji celu, najlepszy wynik fc={:.3f}".format(fc_best[0][-1]))
            ax.set_xlabel("Numer iteracji")
            ax.set_ylabel("Zysk")
            ax.legend()
            ax.grid()
            plt.show()


        # print solution
        def print_sol(sol):
            top = Toplevel()
            top.geometry('%dx%d+%d+%d' % (w + 160, h + 80, x-400, y-40))
            top.pack_propagate(False)
            #top.resizable(False, False)

            top.columnconfigure(0, weight=1)
            top.columnconfigure(1, weight=1)
            top.columnconfigure(2, weight=1)

            font2 = "Helvetica 12 bold"
            font3 = "Helvetica 13"
            sol_lab = ['Złoto', 'Srebro', 'Platyna']
            mat_lab = ['Macierz kupna', 'Macierz produkcji', 'Macierz sprzedaży']

            temp_col = 0
            temp_row = 0

            string = Label(top, text=mat_lab[0], font=font2)
            string.grid(column=1, row=temp_row, columnspan=1, padx=1, pady=1)
            temp_row += 1

            for i in range(3):
                string = Text(top, height=7)
                string.tag_configure("center", justify='center')
                string.insert(END, print_table_1x4(sol.M_pur[i], sol_lab[i]))
                string.tag_add("center", "1.0", "end")
                string.grid(column=temp_col, row=temp_row, columnspan=1, padx=1, pady=1)
                temp_col += 1

            temp_col = 0
            temp_row += 1

            for idx, mat in enumerate([sol.M_pr, sol.M_sls], start=1):
                M_2d = mat3d_to_2d(mat)
                string = Label(top, text=mat_lab[idx], font=font2)
                string.grid(column=1, row=temp_row, columnspan=1, padx=1, pady=1)
                temp_row += 1

                for i in range(0, M_2d.shape[1], int(M_2d.shape[1] / 3)):
                    string = Text(top, height=13)
                    string.tag_configure("center", justify='center')
                    string.insert(END, print_table_7x4(M_2d[:, i: i + int(M_2d.shape[1] / 3)], sol_lab[temp_col]))
                    string.tag_add("center", "1.0", "end")
                    string.grid(column=temp_col, row=temp_row, columnspan=1, padx=1, pady=1)
                    temp_col += 1

                temp_row += 1
                temp_col = 0


        # Search and load data from excel file
        def button2_hit():
            top = Toplevel()
            top.geometry('%dx%d+%d+%d' % (w, h, x, y))
            top.pack_propagate(False)
            top.resizable(False, False)

            # treeview
            frame = tk.LabelFrame(top, text="Dane z pliku")
            frame.place(height=380, width=800)

            # frame open/load file dialog
            file_frame = tk.LabelFrame(top, text="Załadowany plik")
            file_frame.place(height=200, width=800, rely=0.65, relx=0)

            t_b1 = Button(file_frame, text="Wyszukaj", command=lambda: file_dialog())
            t_b1.place(rely=0.65, relx=0.5)

            t_b2 = Button(file_frame, text="Wczytaj", command=lambda: load_excel())
            t_b2.place(rely=0.65, relx=0.3)

            t_lab = ttk.Label(file_frame, text="Nie załadowano żadnego pliku")
            t_lab.place(rely=0, relx=0)

            # treeview widget
            t_tv1 = ttk.Treeview(frame)
            t_tv1.place(relheight=1, relwidth=1)
            # treeview scrolls
            t_ts_x = tk.Scrollbar(frame, orient="horizontal", command=t_tv1.xview)
            t_ts_y = tk.Scrollbar(frame, orient="vertical", command=t_tv1.yview)

            t_tv1.configure(xscrollcommand=t_ts_x.set, yscrollcommand=t_ts_y.set)
            t_ts_x.pack(side="bottom", fill="x")
            t_ts_y.pack(side="right", fill="y")

            # functions to laod file
            def file_dialog():
                init_dir = pathlib.Path().resolve()
                file_name = filedialog.askopenfilename(initialdir=init_dir, title="Wybierz jakiś plik",
                                                       filetypes=(("xlsx files", "*.xlsx"), ("All files", "*.*")))
                top.lift(master)
                t_lab["text"] = file_name
                return None


            def load_excel():
                file_path = t_lab["text"]
                try:
                    excel_file_name = r"{}".format(file_path)
                    self.File_name = excel_file_name
                    df = pd.read_excel(excel_file_name, header=2, usecols="B:V")

                    col_names = ['Popyt złota', 'Popyt srebra', 'Popyt platyny',
                                 'Marża złota', 'Marża srebra', 'Marża platyny',
                                 'Cena złota', 'Cena srebra', 'Cena platyny',
                                 'Cena magazynowania złota', 'Cena magazynowania srebra', 'Cena magazynowania platyny',
                                 'czas przetwarzania złota', 'czas przetwarzania srebra', 'czas przetwarzania platyny',
                                 'koszt produkcji złota', 'koszt produkcji srebra', 'koszt produkcji platyny',
                                 'cena zamiany sprzętu', 'całkowity czas podczas kwartału', 'krok']

                    df.fillna("", inplace=True)
                    df.columns = col_names

                except ValueError:
                    messagebox.showerror("Informacja", "Plik jest nieprawidłowy")
                    return None

                except FileNotFoundError:
                    messagebox.showerror("Informacja", f"Nie ma takiego pliku jak: {file_path}")
                    top.lift(master)
                    return None

                clear_win()

                t_tv1["column"] = list(df.columns)
                t_tv1["show"] = "headings"

                for column in t_tv1["columns"]:
                    t_tv1.heading(column, text=column)

                df_rows = df.to_numpy().tolist()

                for row in df_rows:
                    t_tv1.insert("", "end", values=row)

                return None


            def clear_win():
                t_tv1.delete(*t_tv1.get_children())


        # Buttons: positions

        b2 = Button(master, text='Wczytaj dane', command=button2_hit, font=font1)
        b2.grid(column=5, row=1, rowspan=1, padx=1, pady=1, sticky='news')

        b1 = Button(master, text='Start', command=button1_hit, font=font1)
        b1.grid(column=5, row=2, rowspan=1, padx=1, pady=1, sticky='news')


def print_table_7x4(tab2d, metal):
    assay = np.array([['8', '9', '12', '14', '18', '22', '24']])
    col_names = ['k', 'qtr_1', 'qtr_2', 'qtr_3', 'qtr_4']
    np.set_printoptions(suppress=True)
    tab2d_int = tab2d.astype(int)

    table = PrettyTable()
    table.title = metal
    table.field_names = col_names
    comp_table = np.concatenate((assay.T, tab2d_int), axis=1)

    for row in comp_table:
        table.add_row(row)

    return table.get_string()


def print_table_1x4(tab2d, metal):
    col_names = ['qtr_1', 'qtr_2', 'qtr_3', 'qtr_4']
    np.set_printoptions(suppress=True)
    tab2d_int = tab2d.astype(int)

    table = PrettyTable()
    table.title = metal
    table.field_names = col_names

    table.add_row(tab2d_int)

    return table.get_string()


