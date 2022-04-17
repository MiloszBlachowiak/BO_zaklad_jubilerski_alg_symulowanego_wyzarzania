""" Rafal711 """


import numpy as np
from struktury import Structures, Solution


def calculate(struct: Structures, sol: Solution, no_qtr=4):
    fc = 0
    for i in range(struct.K.shape[0]):
        for j in range(3):
            for h in range(no_qtr):
                fc += struct.M[i, j, h] * struct.K[i] * struct.C[j, h] * sol.M_sls[i, j, h] - \
                      struct.S[j] * sol.M_pr[i, j,  h]

    return fc - (sol.M_mag_sum @ struct.c_mag) - (struct.c_zam * struct.no_ch) - np.sum(np.multiply(sol.M_pur, struct.C))
