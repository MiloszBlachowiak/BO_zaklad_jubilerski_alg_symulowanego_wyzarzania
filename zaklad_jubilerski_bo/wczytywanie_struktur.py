""" Rafal711 """


import pandas as pd
import numpy as np
from struktury import Structures
from typing import List


# funkcja która separuje od siebie dane znajdujące się w komórkach
# wybranych kolumn i tworzy z nich macierz 3d
def get_data(ch_cols: List[str], df: pd.DataFrame):
    tab_to_3d = []
    for name in ch_cols:
        df_col = df[name]
        df_col.dropna(inplace=True)
        tab2d = []
        size = df_col.shape[0]
        for i in range(size):
            mod_col = df_col.values[i].replace(' ', '')
            mod_col = map(float, mod_col.split(','))
            tab2d.append(list(mod_col))

        tab_to_3d.append(np.array(tab2d))

    return np.stack(tab_to_3d, axis=1)


def read_structures(path):
    col_names = ['P_z', 'P_s', 'P_p',
                 'M_z', 'M_s', 'M_p',
                 'C_z', 'C_s', 'C_p',
                 'c_mag_z', 'c_mag_s', 'c_mag_p',
                 't_z', 't_s', 't_p',
                 'S_z', 'S_s', 'S_p',
                 'c_zam', 'T', 'step']

    # Wczytanie pliku typu excel z danymi
    data = pd.read_excel(path, header=2, usecols="B:V")
    data.columns = col_names

    # Zapisanie odczytanych danych do struktury
    struct = Structures()
    struct.P = get_data(col_names[0: 3], data)
    struct.M = get_data(col_names[3: 6], data)
    struct.C = get_data(col_names[6: 9], data)[0, :, :]
    struct.c_mag = data[col_names[9: 12]].iloc[0].values
    struct.t = data[col_names[12: 15]].iloc[0].values
    struct.S = data[col_names[15: 18]].iloc[0].values
    others = data[col_names[18: 21]].iloc[0].values
    struct.c_zam = others[0]
    struct.T = others[1]
    struct.step = others[2]

    return struct
