""" Rafal711 """


import random
import types
import otoczenia
import roz_start_korzystne
import rozw_start_los
import wczytywanie_struktur
from struktury import Structures, Solution
from tkinter import IntVar
import funkcja_celu
import numpy as np
from typing import List, Dict, Optional
from itertools import product


# kryterium stopu1 - temperatura minimalna
def stop1(temp, temp_min):
    return temp <= temp_min


# liczba iteracja błedu bezwzględnego
def stop2(R: Solution, Rn: Solution, struct: Structures, eps, no_it, max_it):
    if np.abs(funkcja_celu.calculate(struct, R) - funkcja_celu.calculate(struct, Rn)) < eps:
        no_it[0] += 1
    else:
        no_it[0] = 0

    return no_it[0] >= max_it


# funkcja opróżniające magazyny
def empty_magazines(temp_sol: Solution):
    temp_sol.M_mag_p = np.zeros(shape=(7, 3))
    temp_sol.M_mag_m = np.zeros(shape=(3))
    temp_sol.M_mag_sum = np.zeros(shape=(3))


def find_solution(struct: Structures, act_sol: Solution, ch_surr: Dict[str, List[IntVar]], no_qtr=4):

    acts = ['purchase', 'production', 'sales']
    surrs_funs: Dict[str, List[types.FunctionType]] = otoczenia.surrs_funs

    idx_pur = [i for i, v in enumerate(ch_surr['purchase']) if v.get() == 1]
    idx_prod = [i for i, v in enumerate(ch_surr['production']) if v.get() == 1]
    idx_sls = [i for i, v in enumerate(ch_surr['sales']) if v.get() == 1]

    indices = [idx_pur, idx_prod, idx_sls]
    all_comb = product(*indices)

    best_sol = None

    for comb in all_comb:
        new_sol = act_sol.copy()

        # wywołanie funkcji opróżniającej magazyny
        empty_magazines(new_sol)

        for qtr in range(no_qtr):
            surrs_funs['purchase'][comb[0]](struct, new_sol, qtr)
            surrs_funs['production'][comb[1]](struct, new_sol, qtr)
            surrs_funs['sales'][comb[2]](struct, new_sol, qtr)

        if best_sol is None:
            best_sol = new_sol

        elif funkcja_celu.calculate(struct, new_sol, no_qtr) > funkcja_celu.calculate(struct, best_sol, no_qtr):
            best_sol = new_sol

    return best_sol


# funkcja wybierająca losowe rozwiązanie
def find_solution_rand(struct: Structures, act_sol: Solution, ch_surr: Dict[str, List[IntVar]], no_qtr=4):
    surrs_funs: Dict[str, List[types.FunctionType]] = otoczenia.surrs_funs

    idx_pur = [i for i, v in enumerate(ch_surr['purchase']) if v.get() == 1]
    idx_prod = [i for i, v in enumerate(ch_surr['production']) if v.get() == 1]
    idx_sls = [i for i, v in enumerate(ch_surr['sales']) if v.get() == 1]

    dbl_surrs =[random.choice(tab) for tab in [idx_pur, idx_prod, idx_sls]]

    new_sol = act_sol.copy()

    # wywołanie funkcji opróżniającej magazyny
    empty_magazines(new_sol)

    for qtr in range(no_qtr):
        surrs_funs['purchase'][dbl_surrs[0]](struct, new_sol, qtr)
        surrs_funs['production'][dbl_surrs[1]](struct, new_sol, qtr)
        surrs_funs['sales'][dbl_surrs[2]](struct, new_sol, qtr)

    return new_sol


def SA_algorithm(struct: Structures, R_start: Solution, temp_start, temp_min, nr_of_iter, alpha, eps, ch_surr, max_it, random_sol):
    R = R_start  # Aktualne rozwiązanie
    R_best = R  # Dotychczasowe najlepsze rozwiązanie
    Temp = temp_start  # Aktualna temperatura
    it_wo_ch = [0] # liczba iteracji pod rząd gdy błąd bezwzględny pomiędzy rozwiązaniami < eps
    fc_start = funkcja_celu.calculate(struct, R) # funkcja celu rowiązania startowego
    it_idx = 0  # pomocniczy indeks
    fc_data = [(fc_start, it_idx)]  # lista przebiegu funkcji celu
    fc_best_data = [(fc_start, it_idx)] # lista przebiegu najlepszych wartości funckji celu
    stop2_active = False

    while not stop1(Temp, temp_min) and not stop2_active:
        for j in range(nr_of_iter):
            if random_sol:
                Rn = find_solution_rand(struct, R, ch_surr)
            else:
                Rn = find_solution(struct, R, ch_surr)

            if stop2(R, Rn, struct, eps, it_wo_ch, max_it):
                stop2_active = True
                break

            fc_Rn = funkcja_celu.calculate(struct, Rn)
            fc_R = funkcja_celu.calculate(struct, R)

            it_idx += 1
            fc_data.append((fc_Rn, it_idx))

            delta = fc_Rn - fc_R

            if delta >= 0:
                R = Rn
                fc_R = funkcja_celu.calculate(struct, R)

                if fc_R > funkcja_celu.calculate(struct, R_best):
                    R_best = R.copy()
                    fc_best_data.append((fc_R, it_idx))
            else:
                s = np.random.rand(1)[0]
                if s < np.exp(-delta / Temp):
                    R = Rn
        else:
            Temp = alpha * Temp

    return R_best, fc_data, fc_best_data


def run_algorithm(surrs: Dict[str, List[IntVar]], param: np.ndarray, start_opt: IntVar, surr_opt: IntVar, path, lf_file):

    np.set_printoptions(suppress=True)

    # Przypisanie odpowiednich parametrów
    alpha = float(param[0].get())
    temp_start = float(param[1].get())
    nr_of_iter = int(param[2].get())
    temp_min = float(param[3].get())
    max_it = int(param[4].get())
    eps = 10
    random_sol = True if surr_opt.get() == 0 else False
    random_start = True if start_opt.get() == 0 else False
    random_lf = True if lf_file.get() == 0 else False

    # Utworzenie struktury danych (wczytywanie z pliku bądź losowe)
    if random_lf:
        struct = Structures()
    else:
        struct = wczytywanie_struktur.read_structures(path)

    # Wygenerowanie odpowiedniego rozwiązania startowego
    if random_start:
        sol = rozw_start_los.find_start_sol_random(struct)
    else:
        sol = roz_start_korzystne.find_start_sol(struct)

    # Uruchomienie algorytmu Symulowanego Wyżarzania
    best_sol, fc_data, fc_best_data = SA_algorithm(struct, sol, temp_start, temp_min, nr_of_iter, alpha,
                                                   eps, surrs, max_it, random_sol)

    return best_sol, fc_data, fc_best_data
