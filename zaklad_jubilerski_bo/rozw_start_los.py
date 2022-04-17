""" Jaromir-hub146, MiloszBlachowiak """


from struktury import Structures, Solution
import numpy as np
import random
import ograniczenia


def fill_qtr_purchase_matrix(sol: Solution, struct: Structures, qtr:int):

    metals_to_produce = list(set(struct.ch_prod[qtr:]))

    for p_metal in metals_to_produce:
        # obliczenie zapasu masy metalu, którą możemy dokupić względem popytu (całkowitego, we wszystkich kwartałach i dla wszystkich prób)
        demand_reserve = ograniczenia.calc_demand_reserve_pur(struct, sol, p_metal)

        # losowy wybór masy do dodania
        if demand_reserve == 0:
            to_add = 0
        else:
            to_add = random.randrange(start=0, stop=int(np.ceil(demand_reserve)), step=struct.step) / sol.M_pur.shape[0]

        sol.M_pur[p_metal, qtr] += to_add

        sol.M_mag_m[p_metal] += to_add

    return sol


def fill_qtr_production_matrix(sol: Solution, struct: Structures, qtr:int):
    # przetwarzany metal w tym kwartale
    p_metal = struct.ch_prod[qtr]

    for assay in range(sol.M_pr.shape[0]):

        # obliczenie zapasu masy, którą możemy dołożyć względem popytu
        demand_reserve = ograniczenia.calc_demand_reserve_prod(struct, sol, assay, p_metal)

        # obliczenie zapasu czasu i zapasu masy na podstawie zapasu czasu
        time_reserve = ograniczenia.calc_time_reserve_prod(struct, sol, p_metal, qtr)
        product_mass_reserve = int(time_reserve / struct.t[p_metal])

        # wyliczenie ograniczenia od ilości metalu w magazynie
        mag_reserve = ograniczenia.calc_mag_reserve(struct, sol, assay, p_metal)

        # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
        limit = min(mag_reserve, product_mass_reserve, demand_reserve) / struct.ch_prod.shape[0]

        # losowy wybór masy do dodania i dodanie tej masy
        if limit == 0:
            to_add = 0
        else:
            to_add = np.random.randint(int(np.ceil(limit)))

        # aktualizacja macierzy prrodukcji oraz magazynów
        sol.M_pr[assay, p_metal, qtr] += to_add
        sol.M_mag_m[p_metal] -= to_add * struct.K[assay]
        sol.M_mag_p[assay, p_metal] += to_add

    return sol


def fill_qtr_selling_matrix(sol: Solution, struct: Structures, qtr:int):

    for p_metal in range(sol.M_pur.shape[0]):
        for assay in range(sol.M_pr.shape[0]):

            # zapas popytu
            demand_reserve = ograniczenia.calc_demand_reserve_sls(struct, sol, assay, p_metal, qtr)

            # limit ile możemy zwiększyć
            limit = min(sol.M_mag_p[assay, p_metal], demand_reserve)

            # losowy wybór masy do dodania i dodanie tej masy
            if limit == 0:
                to_add = 0
            else:
                to_add = np.random.randint(int(np.ceil(limit))) / sol.M_pr.shape[0]

            # aktualizacja macierzy prrodukcji oraz magazynów
            sol.M_sls[assay, p_metal, qtr] += to_add
            sol.M_mag_p[assay, p_metal] -= to_add

    return sol


def find_start_sol_random(S_start: Structures):
    # rozwiązania
    R_start = Solution()

    # zerowanie macierzy
    R_start.M_pr = np.zeros((7, 3, 4)) # masy wyrobow o wybranej probie (całkowita masa przedmiotu)
    R_start.M_sls = np.zeros((7, 3, 4))  # macierz sprzedaży
    R_start.M_pur = np.zeros((3, 4))  # macierz zakupu
    R_start.M_mag_m = np.zeros(3)  # macierz magazynowanego metalu (aktualizowana)
    R_start.M_mag_p = np.zeros((7, 3))  # macierz magazynowanego produktu
    R_start.M_mag_sum = np.zeros(shape=3)

    for qtr in range(np.size(S_start.ch_prod)):

        fill_qtr_purchase_matrix(R_start, S_start, qtr)
        fill_qtr_production_matrix(R_start, S_start, qtr)
        fill_qtr_selling_matrix(R_start, S_start, qtr)

    return R_start
