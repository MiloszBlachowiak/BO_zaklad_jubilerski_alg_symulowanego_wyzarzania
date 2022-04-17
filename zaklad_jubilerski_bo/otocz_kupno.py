""" MiloszBlachowiak """


from struktury import Structures, Solution
import numpy as np
import random
import ograniczenia


# Otoczenie 1 - kupno -losowo wybierane metale do zakupu w danym kwartale, zwiększenie zakupionej ilości o losową wartość
# z dopuszczalnego zakresu lub gdy jest to konieczne, zmniejszenie tej wartosci
def pur_surr_1(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 2):

    # tworzymy listę metali które będziemy przerabiać aby nie kupować tych metali, z których nie będziemy w ogóle wytwarzać produktów
    metals_to_produce = list(set(struct.ch_prod[qtr:]))

    for _ in range(min(nr_of_changes, len(metals_to_produce))):

        # losowy wybór metalu
        p_metal = metals_to_produce.pop(np.random.randint(len(metals_to_produce)))

        # obliczenie zapasu masy metalu, którą możemy dokupić względem popytu (całkowitego, we wszystkich kwartałach i dla wszystkich prób)
        demand_reserve = ograniczenia.calc_demand_reserve_pur(struct, sol, p_metal)

        # losowy wybór masy do dodania
        if demand_reserve == 0:
            to_add = 0
        else:
            to_add = random.randrange(start=0, stop=int(np.ceil(demand_reserve)), step=struct.step)

        # dodanie wartości
        sol.M_pur[p_metal, qtr] += to_add

    # update magazynu  (po zakupie)
    sol.M_mag_m = sol.M_mag_m + sol.M_pur[:, qtr]

    # update macierzy sum
    sol.M_mag_sum = sol.M_mag_sum + sol.M_mag_m

    return sol

#########################################################################################

# Otoczenie 2 - kupno - tak jak w otoczeniu 1 losowo wybieramy metale, ale tutaj dodajemy lub odejmujemy stałą wartość
def pur_surr_2(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 3, value=10):

    metals_to_produce = list(set(struct.ch_prod[qtr:]))

    for _ in range(min(nr_of_changes, len(metals_to_produce))):

        # losowy wybór metalu
        p_metal = metals_to_produce.pop(np.random.randint(len(metals_to_produce)))

        if np.random.randint(3) != 0:  # można losować z większej puli i manipulować prawdopodobieństwem dodawania i odejmowania
            # DODAJEMY WARTOŚĆ DO KOMÓRKI

            # obliczenie zapasu masy metalu, którą możemy dokupić względem popytu (całkowitego, we wszystkich kwartałach i dla wszystkich prób)
            demand_reserve = ograniczenia.calc_demand_reserve_pur(struct, sol, p_metal)

            # wyliczenie ile maksymalnie możemy dodać do komórki (ograniczenia od ilości metalu w magazynie, czasu i popytu)
            to_add = min(value, int(demand_reserve))

            # dodanie wartości
            sol.M_pur[p_metal, qtr] += to_add

        else:
            # ODEJMUJEMY WARTOŚĆ Z KOMÓRKI

            # wyliczenie ile możemy odjąć z komórki (nie możemy odjąć więcej niż w niej jest)
            to_subtract = min(value, int(sol.M_pur[p_metal, qtr]))

            # odjęcie wartości
            sol.M_pur[p_metal, qtr] -= to_subtract

    # update magazynu  (po zakupie)
    sol.M_mag_m = sol.M_mag_m + sol.M_pur[:, qtr]

    # update macierzy sum
    sol.M_mag_sum = sol.M_mag_sum + sol.M_mag_m

    return sol

######################################################################################################################

# Otoczenie 3 - kupno - przenosimy losową wartość między komórkami tak aby sumaryczna ilość w wierszu pozostawała niezmienna
def pur_surr_3(struct: Structures, sol: Solution, qtr: int, nr_of_changes: int = 1):

    # tworzymy listę metali które będziemy przerabiać aby nie kupować tych metali, z których nie będziemy w ogóle wytwarzać produktów
    metals_to_produce = list(set(struct.ch_prod[qtr:]))

    for _ in range(min(nr_of_changes, len(metals_to_produce) - 1)):

        # losowy wybór metalu z którego odbieramy i do którego dokładamy
        met_to_take_from = metals_to_produce.pop(np.random.randint(len(metals_to_produce)))
        met_to_add_to = random.choice(metals_to_produce)

        # obliczenie zapasu masy metalu, którą możemy dokupić względem popytu (całkowitego, we wszystkich kwartałach i dla wszystkich prób)
        demand_reserve = ograniczenia.calc_demand_reserve_pur(struct, sol, met_to_add_to)

        limit = min(sol.M_pur[met_to_take_from, qtr], demand_reserve)

        # losowy wybór masy do dodania
        if limit == 0:
            to_transfer = 0
        else:
            to_transfer = random.randrange(start=0, stop=int(np.ceil(limit)), step=struct.step)

        #odjęcie wartości
        sol.M_pur[met_to_take_from, qtr] -= to_transfer
        # dodanie wartości
        sol.M_pur[met_to_add_to, qtr] += to_transfer

    # update magazynu  (po zakupie)
    sol.M_mag_m = sol.M_mag_m + sol.M_pur[:, qtr]

    # update macierzy sum
    sol.M_mag_sum = sol.M_mag_sum + sol.M_mag_m

    return sol

