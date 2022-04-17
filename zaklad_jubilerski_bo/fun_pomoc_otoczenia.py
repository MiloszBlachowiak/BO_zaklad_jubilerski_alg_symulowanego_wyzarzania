""" MiloszBlachowiak """


from struktury import Structures, Solution
import numpy as np


# DO PRODUKCJI

# redukcja niedoboru poprzez odjęcie losowej wartości od ilości produkowanego wyrobu
def reduce_deficiency(struct: Structures, sol: Solution, p_metal: int, chosen_assay: int, qtr: int):
    if int(sol.M_pr[chosen_assay, p_metal, qtr] / 2) > 0:
        to_subtract = np.random.randint(int(sol.M_pr[chosen_assay, p_metal, qtr] / 2))

        sol.M_pr[chosen_assay, p_metal, qtr] -= to_subtract

        # update magazynu  (po odjęciu)
        sol.M_mag_m[p_metal] += to_subtract * struct.K[chosen_assay]
        sol.M_mag_p[chosen_assay, p_metal] -= to_subtract
    return sol


# wyeliminowanie niedoboru metalu
def fix_deficiency(struct: Structures, sol: Solution, p_metal, qtr):

    while sol.M_mag_m[p_metal] < 0:
        chosen_assay = np.random.randint(len(struct.K))

        if sol.M_pr[chosen_assay, p_metal, qtr] > 0:

            if sol.M_pr[chosen_assay, p_metal, qtr] > 1:

                # odejmujemy losową wartość
                to_subtract = np.random.randint(sol.M_pr[chosen_assay, p_metal, qtr])
            else:
                to_subtract = sol.M_pr[chosen_assay, p_metal, qtr]

            sol.M_pr[chosen_assay, p_metal, qtr] -= to_subtract

            # update magazynu  (po odjęciu)
            sol.M_mag_m[p_metal] += to_subtract * struct.K[chosen_assay]
            sol.M_mag_p[chosen_assay, p_metal] -= to_subtract

            if np.all(sol.M_pr[chosen_assay, p_metal, qtr]) == 0:  # przez błędy zaokrągleń przy przemnażaniu czasami
                # jest minimalny niedobór metalu, który nie powinien występować
                sol.M_mag_m[p_metal] = 0
    return sol


# DO SPRZEDAŻY

# funkcja pomocnicza do sprawdzania i ewentualnej eliminacji niedoboru metalu w magazynie
def fix_metal_deficiency(sol: Solution, qtr: int, p_metal: int):

    if any(el < 0 for el in sol.M_mag_p[:, p_metal]):  # sprawdzanie czy nie mamy niedoboru produktu w magazynie

        for i in range(len(sol.M_mag_p[:, p_metal])):

            if sol.M_mag_p[i, p_metal] < 0:  # zerujemy niedobór
                sol.M_sls[i, p_metal, qtr] -= -1 * sol.M_mag_p[i, p_metal]
                sol.M_mag_p[i, p_metal] += -1 * sol.M_mag_p[i, p_metal]

                if sol.M_sls[i, p_metal, qtr] > 0:  # zmniejszamy jeszcze ilość sprzedanego produktu żeby dać nam pole do manipulacji
                    to_subtract = np.random.randint(int(np.ceil(sol.M_sls[i, p_metal, qtr])))

                    sol.M_sls[i, p_metal, qtr] -= to_subtract
                    sol.M_mag_p[i, p_metal] += to_subtract
    return sol
