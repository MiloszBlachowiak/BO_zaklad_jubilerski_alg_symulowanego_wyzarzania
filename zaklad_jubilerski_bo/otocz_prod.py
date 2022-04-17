""" MiloszBlachowiak """


from struktury import Structures, Solution
import numpy as np
import random
import ograniczenia
from fun_pomoc_otoczenia import reduce_deficiency, fix_deficiency


#########################################################################################################

# Otoczenie 1 - produkcja - wybór losowej komórki (próby), do której dodajemy losową wartość z dopuszczalnego zakresu
# lub odejmujemy, gdy zachodzi taka potrzeba
def prod_surr_1(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 4):

    # przetwarzany metal w tym kwartale
    p_metal = struct.ch_prod[qtr]

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_m = sol.M_mag_m - (struct.K @ sol.M_pr[:, :, qtr])
    sol.M_mag_p = sol.M_mag_p + sol.M_pr[:, :, qtr]

    # lista prób
    metal_assays = [i for i in range(len(struct.K))]

    nr_of_changes = min(nr_of_changes, len(struct.K))

    for _ in range(nr_of_changes):

        # losowy wybór próby (nie można wybrać 2 razy tej samej)
        chosen_assay = metal_assays.pop(np.random.randint(len(metal_assays)))

        if sol.M_mag_m[p_metal] > 0:
            # obliczenie zapasu masy, którą możemy dołożyć względem popytu
            demand_reserve = ograniczenia.calc_demand_reserve_prod(struct, sol, chosen_assay, p_metal)

            # obliczenie zapasu czasu i zapasu masy na podstawie zapasu czasu
            time_reserve = ograniczenia.calc_time_reserve_prod(struct, sol, p_metal, qtr)
            product_mass_reserve = int(time_reserve / struct.t[p_metal])

            # wyliczenie ograniczenia od ilości metalu w magazynie
            mag_reserve = ograniczenia.calc_mag_reserve(struct, sol, chosen_assay, p_metal)

            # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
            limit = min(mag_reserve, product_mass_reserve, demand_reserve)

            # losowy wybór masy do dodania i dodanie tej masy
            if limit == 0:
                to_add = 0
            else:
                to_add = np.random.randint(int(np.ceil(limit)))

            sol.M_pr[chosen_assay, p_metal, qtr] += to_add

            # update magazynu  (po dodaniu)
            sol.M_mag_m[p_metal] -= to_add * struct.K[chosen_assay]
            sol.M_mag_p[chosen_assay, p_metal] += to_add

            # tu jeszcze można dodać odejmowanie jak mimo że nie jest to konieczne z powodu niedomiaru w magazynie

        if sol.M_mag_m[p_metal] < 0:
            # sytuacja gdy  nie możemy dodać więcej, konieczne jest odjęcie z jednego z poniższych powodów:
            # -zwiększono ilość produkcji w poprzednich kwartałach względem rozwiązania poprzedniego przez co teraz
            # mamy niedobór metalu w magazynie,
            # -zmniejszono ilość zakupionego metalu względem poprzedniego rozwiązania przez co również mamy niedobór metalu

            reduce_deficiency(struct, sol, p_metal, chosen_assay, qtr)

    if sol.M_mag_m[p_metal] < 0:  # gdy po ostatniej zmianie nadal mamy niedobór w magazynie

        fix_deficiency(struct, sol, p_metal, qtr)

    return sol

##########################################################################################################
##########################################################################################################


# Otoczenie 2 - produkcja - tak jak w otoczeniu 1 próby są wybierane losowo, ale dodajemy lub odejmujemy stałą wartość
# lub jeśli to niemożlwe to największą możliwą
def prod_surr_2(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 4, value=10):

    # przetwarzany metal w tym kwartale
    p_metal = struct.ch_prod[qtr]

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_m = sol.M_mag_m - (struct.K @ sol.M_pr[:, :, qtr])
    sol.M_mag_p = sol.M_mag_p + sol.M_pr[:, :, qtr]

    # lista prób
    metal_assays = [i for i in range(len(struct.K))]

    nr_of_changes = min(nr_of_changes, len(struct.K))

    for _ in range(nr_of_changes):

        # losowy wybór próby (nie można wybrać 2 razy tej samej)
        chosen_assay = metal_assays.pop(np.random.randint(len(metal_assays)))

        if sol.M_mag_m[p_metal] > 0:
            if np.random.randint(3) != 0:  # można losować z większej puli i manipulować prawdopodobieństwem dodawania i odejmowania
                # DODAJEMY WARTOŚĆ DO KOMÓRKI
                # obliczenie zapasu masy, którą możemy dołożyć względem popytu
                demand_reserve = ograniczenia.calc_demand_reserve_prod(struct, sol, chosen_assay, p_metal)

                # obliczenie zapasu czasu i na jego podstawie maksymalnej dodatkowej masie produktów
                time_reserve = ograniczenia.calc_time_reserve_prod(struct, sol, p_metal, qtr)
                product_mass_reserve = int(time_reserve / struct.t[p_metal])

                # wyliczenie ograniczenia od ilości metalu w magazynie
                mag_reserve = ograniczenia.calc_mag_reserve(struct, sol, chosen_assay, p_metal)

                # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
                to_add = min(value, mag_reserve, product_mass_reserve, demand_reserve)

                # dodanie wartości
                sol.M_pr[chosen_assay, p_metal, qtr] += to_add


                # update magazynu (po produkcji)
                sol.M_mag_m[p_metal] -= to_add * struct.K[chosen_assay]
                sol.M_mag_p[chosen_assay, p_metal] += to_add

            else:
                # ODEJMUJEMY WARTOŚĆ Z KOMÓRKI

                # wyliczenie ile możemy odjąć z komórki (nie możemy odjąć więcej niż w niej jest)
                to_subtract = min(value, sol.M_pr[chosen_assay, p_metal, qtr])

                # odjęcie wartości
                sol.M_pr[chosen_assay, p_metal, qtr] -= to_subtract


                # update magazynu  (po produkcji)
                sol.M_mag_m[p_metal] += to_subtract * struct.K[chosen_assay]
                sol.M_mag_p[chosen_assay, p_metal] -= to_subtract


        if sol.M_mag_m[p_metal] < 0:
            # sytuacja gdy  nie możemy dodać więcej, konieczne jest odjęcie z jednego z poniższych powodów:
            # -zwiększono ilość produkcji w poprzednich kwartałach względem rozwiązania poprzedniego przez co teraz
            # mamy niedobór metalu w magazynie,
            # -zmniejszono ilość zakupionego metalu względem poprzedniego rozwiązania przez co również mamy niedobór metalu

            # odejmujemy losową wartość (ale maksymalnie połowę tego co mamy)
            reduce_deficiency(struct, sol, p_metal, chosen_assay, qtr)

    if sol.M_mag_m[p_metal] < 0:  # gdy po ostatniej zmianie nadal mamy niedobór w magazynie
        fix_deficiency(struct, sol, p_metal, qtr)

    return sol


# Otoczenie 3 - produkcja - przenosimy losowe wartości między komórkami tak aby sumaryczna ilość w kolumnie pozostawała niezmienna
def prod_surr_3(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 2):

    # przetwarzany metal w tym kwartale
    p_metal = struct.ch_prod[qtr]

    # update magazynu (po produkcji, względem dotychczasowego rozwiązania)
    sol.M_mag_m = sol.M_mag_m - (struct.K @ sol.M_pr[:, :, qtr])
    sol.M_mag_p = sol.M_mag_p + sol.M_pr[:, :, qtr]

    # lista prób
    metal_assays = [i for i in range(len(struct.K))]

    nr_of_changes = min(nr_of_changes, len(struct.K) - 1)

    for _ in range(nr_of_changes):

        # losowy wybór metalu z którego odbieramy i do którego dokładamy
        assay_to_take_from = metal_assays.pop(np.random.randint(len(metal_assays)))
        assay_to_add_to = random.choice(metal_assays)

        if sol.M_mag_m[p_metal] > 0:

            # obliczenie zapasu masy, którą możemy dołożyć względem popytu
            demand_reserve = ograniczenia.calc_demand_reserve_prod(struct, sol, assay_to_add_to, p_metal)

            # ile możemy przenieść względem tego co mamy w magazynie
            mag_metal_reserve = (sol.M_mag_m[p_metal] + sol.M_pr[assay_to_take_from, p_metal, qtr] * struct.K[assay_to_take_from])

            # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
            limit = min(mag_metal_reserve/struct.K[assay_to_add_to], demand_reserve, sol.M_pr[assay_to_take_from, p_metal, qtr])

            if limit < 0:
                print(sol.M_mag_m[p_metal]/struct.K[assay_to_add_to])

            if limit == 0:
                to_transfer = 0
            else:
                to_transfer = np.random.randint(int(np.ceil(limit)))

            # przeniesienie wartości między komórkami
            sol.M_pr[assay_to_take_from, p_metal, qtr] -= to_transfer
            sol.M_pr[assay_to_add_to, p_metal, qtr] += to_transfer

            # update magazynu  (po dodaniu)
            sol.M_mag_m[p_metal] += to_transfer * struct.K[assay_to_take_from]
            sol.M_mag_m[p_metal] -= to_transfer * struct.K[assay_to_add_to]

            sol.M_mag_p[assay_to_take_from, p_metal] -= to_transfer
            sol.M_mag_p[assay_to_add_to, p_metal] += to_transfer

        if sol.M_mag_m[p_metal] < 0:
            # sytuacja gdy  nie możemy dodać więcej, konieczne jest odjęcie z jednego z poniższych powodów:
            # -zwiększono ilość produkcji w poprzednich kwartałach względem rozwiązania poprzedniego przez co teraz
            # mamy niedobór metalu w magazynie,
            # -zmniejszono ilość zakupionego metalu względem poprzedniego rozwiązania przez co również mamy niedobór metalu

            # odejmujemy losową wartość (ale maksymalnie połowę tego co mamy)
            reduce_deficiency(struct, sol, p_metal, assay_to_add_to, qtr)

    if sol.M_mag_m[p_metal] < 0:  # gdy po ostatniej zmianie nadal mamy niedobór w magazynie
        fix_deficiency(struct, sol, p_metal, qtr)

    return sol
