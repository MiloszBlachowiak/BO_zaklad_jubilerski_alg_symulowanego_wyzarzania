""" ....... """


from struktury import Structures, Solution
import numpy as np


def check_time(struct: Structures, sol: Solution, qtr: int):
    p_metal = struct.ch_prod[qtr]
    if struct.t[p_metal] * np.sum(sol.M_pr[:, p_metal, qtr]) > struct.T:
        return False

    return True


# sprawdzenie warunków dotyczących ilości metalu wykorzystanych w produkcji
def check_masses(struct: Structures, matrix_sol, qtr: int, mag_sur):
    p_metal = struct.ch_prod[qtr]
    if struct.K @ matrix_sol[:, p_metal, qtr] > mag_sur[p_metal, qtr]:
        return False

    return True


# sprawdzenie czy nie sprzedaliśmy więcej niż jest w magazynie w danym kwartale
def check_storehouse_sell(matrix_sell, qtr, p_metal, mag_p):
    if np.all(mag_p[:, p_metal, qtr] >= matrix_sell[:, p_metal, qtr]):
        return True

    return False


# sprawdzenie warunków popytu dla sprzedaży w jednym kwartale
def check_demand_sls(struct: Structures, matrix_sell, qtr, metal):
    if np.all(matrix_sell[:, metal, qtr] <= struct.P[:, metal, qtr]):
        return True

    return False


# sprawdzenie warunków popytu dla sprzedaży w jednym kwartale
def check_popyt_prod(struct: Structures, matrix_prod, qtr, metal):
    if np.all(matrix_prod[:, int(metal), qtr] <= struct.P[:, int(metal), qtr]):
        return True

    return False


# sprawdzenie w korzystnym
def check_time_prod(struct: Structures, matrix_prod_opt, qtr: int):
    p_metal = int(struct.ch_prod[qtr])
    if struct.t[p_metal] * np.sum(matrix_prod_opt[:, p_metal, qtr]) > struct.T:
        return False

    return True


# obliczanie zapasu metalu który możemy jeszcze dokupić aby pozostać w granicach wartości popytu
def calc_demand_reserve_pur(struct: Structures, sol: Solution, p_metal: int):
    return struct.P[:, p_metal, :].sum(axis=1) @ struct.K - np.sum(sol.M_pur[p_metal, :])


# obliczanie zapasu produktu, o który możemy maksymalnie zwiększyć produkcję aby pozostać jeszcze w granicach wartości popytu
def calc_demand_reserve_prod(struct: Structures, sol: Solution, assay: int, p_metal: int):
    return np.sum(struct.P[assay, p_metal, :]) - np.sum(sol.M_pr[assay, p_metal, :])


# obliczanie zapasu produktu, o który możemy maksymalnie zwiększyć produkcję aby pozostać jeszcze w granicach wartości popytu
def calc_demand_reserve_sls(struct: Structures, sol: Solution, assay: int, p_metal: int, qtr: int):
    return struct.P[assay, p_metal, qtr] - sol.M_sls[assay, p_metal, qtr]


# obliczanie zapasu czasu
def calc_time_reserve_prod(struct: Structures, sol: Solution, p_metal: int, qtr: int):
    return struct.T - struct.t[p_metal] * np.sum(sol.M_pr[:, p_metal, qtr])


# obliczenie zapasu masy produktu jaką możemy dodać względem zapasu metalu w magazynie
def calc_mag_reserve(struct: Structures, sol: Solution, assay: int, p_metal: int):
    return sol.M_mag_m[p_metal]/struct.K[assay]

