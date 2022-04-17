""" MiloszBlachowiak """


from struktury import Structures, Solution
import numpy as np
import random
import ograniczenia
from fun_pomoc_otoczenia import fix_metal_deficiency

#SPRZEDAŻ

# Otoczenie 1 - sprzedaż - losowe wybieranie określonej liczby prób dla każdego metalu i zwiększenie wartości w odpowiadających
# im komórkach o losową wartość z dopuszczalnego zakresu lub ewentualne odjęcie w przypadku niedoboru materiału w magazynie
def sls_surr_1(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 3):

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_p = sol.M_mag_p - sol.M_sls[:, :, qtr]


    for p_metal in set(struct.ch_prod):

        # lista prób
        metal_assays = [i for i in range(len(struct.K))]

        fix_metal_deficiency(sol, qtr, p_metal)

        for _ in range(min(nr_of_changes, len(struct.K))):
            # losowy wybór próby (nie można wybrać 2 razy tej samej)
            chosen_assay = metal_assays.pop(np.random.randint(len(metal_assays)))

            # zapas popytu
            demand_reserve = ograniczenia.calc_demand_reserve_sls(struct, sol, chosen_assay, p_metal, qtr)

            # limit ile możemy zwiększyć
            limit = min(sol.M_mag_p[chosen_assay, p_metal], demand_reserve)

            # losowy wybór masy do dodania (maksymalnie możemy dodać tyle ile jeszcze mamy w magazynie)
            if limit == 0:
                to_add = 0
            else:
                to_add = np.random.randint(int(np.ceil(limit)))

            # dodanie wartości
            sol.M_sls[chosen_assay, p_metal, qtr] += to_add

            # update magazynu  (po zmianie)
            sol.M_mag_p[chosen_assay, p_metal] -= to_add

    return sol

###################################################################################################

#Otoczenie 2 - sprzedaż - losowy wybór jak w otoczeniu 1, odjęcie lub dodanie stałej wartości lub gdy to niemożliwe to,
# maksymalnej możliwej
def sls_surr_2(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 3, value=10):

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_p = sol.M_mag_p - sol.M_sls[:, :, qtr]

    for p_metal in set(struct.ch_prod):

        # lista prób
        metal_assays = [i for i in range(len(struct.K))]

        fix_metal_deficiency(sol, qtr, p_metal)

        for _ in range(min(nr_of_changes, len(struct.K))):
            # losowy wybór próby (nie można wybrać 2 razy tej samej)
            chosen_assay = metal_assays.pop(np.random.randint(len(metal_assays)))

            if np.random.randint(3) != 0:  # można losować z większej puli i manipulować prawdopodobieństwem dodawania i odejmowania
                # DODAJEMY WARTOŚĆ DO KOMÓRKI

                # zapas popytu
                demand_reserve = ograniczenia.calc_demand_reserve_sls(struct, sol, chosen_assay, p_metal, qtr)

                # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
                to_add = min(value, sol.M_mag_p[chosen_assay, p_metal], demand_reserve)

                # dodanie wartości
                sol.M_sls[chosen_assay, p_metal, qtr] += to_add

                # update magazynu  (po zmianie)
                sol.M_mag_p[chosen_assay, p_metal] -= to_add

            else:
                # ODEJMUJEMY WARTOŚĆ Z KOMÓRKI

                # wyliczenie ile możemy odjąć z komórki (nie możemy odjąć więcej niż w niej jest)
                to_subtract = min(value, sol.M_sls[chosen_assay, p_metal, qtr])

                # odjęcie wartości
                sol.M_sls[chosen_assay, p_metal, qtr] -= to_subtract

                # update magazynu  (po zmianie)
                sol.M_mag_p[chosen_assay, p_metal] += to_subtract
    return sol

###################################################################################################

#Otoczenie 3 - sprzedaż - przeniesienie wartości między losowymi komórkami (próbami) w każdyej kolumnie (dla każdego metalu)
# tak aby sumaryczna ilość w kolumnie pozostawała niezmienna
def sls_surr_3(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 3):

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_p = sol.M_mag_p - sol.M_sls[:, :, qtr]

    for p_metal in set(struct.ch_prod):

        fix_metal_deficiency(sol, qtr, p_metal)

        # lista prób
        metal_assays = [i for i in range(len(struct.K))]

        for _ in range(min(nr_of_changes, len(metal_assays) - 1)):

            # losowy wybór metalu, z którego odbieramy i do którego dokładamy
            assay_to_take_from = metal_assays.pop(np.random.randint(len(metal_assays)))
            assay_to_add_to = random.choice(metal_assays)

            # zapas popytu
            demand_reserve = ograniczenia.calc_demand_reserve_sls(struct, sol, assay_to_add_to, p_metal, qtr)

            # wyliczenie ile maksymalnie możemy przenieść między wylosowanymi wierszami (próbami)
            limit = min(sol.M_sls[assay_to_take_from, p_metal, qtr], demand_reserve, sol.M_mag_p[assay_to_add_to, p_metal])

            # losowy wybór masy do dodania
            if limit == 0:
                to_transfer = 0
            else:
                to_transfer = np.random.randint(int(np.ceil(limit)))

            # przeniesienie wartości
            sol.M_sls[assay_to_take_from, p_metal, qtr] -= to_transfer
            sol.M_sls[assay_to_add_to, p_metal, qtr] += to_transfer

            # update magazynu  (po zmianie)
            sol.M_mag_p[assay_to_take_from, p_metal] += to_transfer
            sol.M_mag_p[assay_to_add_to, p_metal] -= to_transfer

    return sol
