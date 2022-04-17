""" Jaromir-hub146 """


from struktury import Structures, Solution
import ograniczenia
import numpy as np
import math
import random
from typing import List, Dict, Tuple, Union
import copy


# Funkcja obliczająca maksymalny zarobek w danym kwartale dla danego metalu - kurs * marża * próba * maksymalny popyt
# daje infomacje kiedy naleoiej sprzedać by osiągnąć maksymalny zysk
# (nie uwzględniono okraniczenia czasowego - dopiero przy produkcji)
def P_max_sol(struct: Structures, qtr_zabronione: List[int], metal_zabroniony: List[int]) -> Dict[int, Tuple[int, int]]:
    d = {}
    for j in range(struct.C.shape[0]):
        if j not in metal_zabroniony:
            gain = float('-inf')
            which_qtr = None
            for num_of_qtr in range(struct.C.shape[1]):
                max_val = 0
                if num_of_qtr not in qtr_zabronione:
                    for i in range(struct.K.shape[0]):
                        max_val += struct.M[i, j, num_of_qtr] * struct.K[i] * struct.C[j, num_of_qtr] * struct.P[i, j, num_of_qtr]
                    if max_val > gain:
                        gain = max_val
                        which_qtr = num_of_qtr
            d[j] = (which_qtr, int(gain))
    return d


# Funkcja zwraca wartość logiczną False gdy sprzedaż dla n metali
# odbywa się w kwartale o indeksie n-1 (licząc od 1) - czyli kolizja produkcji, True - gdy jej nie ma
# To trzeba poprawić żeby dla większej ilości niż 4 kwartały nie było kolizji produkcji
def prod_collision(max_gain_dict: Dict[int, Tuple[int, int]]):
    list = []
    for metal in max_gain_dict:
        list.append(max_gain_dict[metal][0])

    if list.count(0) > 1:
        return False
    elif list.count(0) == 1 and list.count(1) == 2:
        return False
    elif list.count(1) > 2:
        return False
    else:
        return True


def return_opt_sell_dict(struct: Structures, max_gain_dict: Dict[int, Tuple[int, int]]):
    opt_sell_dict = {}
    zabronione = [max_gain_dict[metal][0] for metal in max_gain_dict]
    if zabronione.count(1) == 2:
        zabronione.append(0)
    pozost_qtr = P_max_sol(struct, zabronione, [])
    max_list = [pozost_qtr[metal][1] for metal in pozost_qtr]
    max_value_index = max_list.index(max(max_list))
    for key in max_gain_dict:
        opt_sell_dict[key] = [max_gain_dict[key][0]]

    opt_sell_dict[max_value_index].append(pozost_qtr[max_value_index][0])
    return opt_sell_dict


# Funkcja zwracajaca zoptymalizowane kwartały pod względem produkcji, w których sprzedaż jest najbardziej opłacalna
# Zraca słownik gdzie kluczem jest maetal, a wartością indeks kwartału
# (sytuacja gdzie najbardziej opłaca się sprzedać dla kilku metaalów w tym samym kwartale np. w 0 , 1, 2 ..., n-2 - numer. kwartałów)
def find_sell_qtr(struct: Structures, max_gain_dict: Dict[int, Tuple[int, int]]):
    if prod_collision(max_gain_dict): #Jeżeli nie ma kolizji produkcji
        return return_opt_sell_dict(struct, max_gain_dict)
    else:
        colission_sell_dict = copy.deepcopy(max_gain_dict)
        zab_metal = []
        zab_qtr = []
        min_gain = None
        while not prod_collision(colission_sell_dict):
            liczba_qtr_danego_typu = [colission_sell_dict[metal][0] for metal in colission_sell_dict]
            if liczba_qtr_danego_typu.count(struct.C.shape[0] - 2) == 3:
                min_list = [colission_sell_dict[metal][1] for metal in colission_sell_dict if (metal not in zab_metal)]
                min_value_index = min_list.index(min(min_list))
                for key in colission_sell_dict:
                    if colission_sell_dict[key][1] == min_list[min_value_index]:
                        min_gain = key
                for met in colission_sell_dict:
                    if met is not min_gain:
                        zab_metal.append(met)
                        zab_qtr.append(colission_sell_dict[met][0])
                        zab_qtr.append(int(0))
                pozost_qtr = P_max_sol(struct, list(set(zab_qtr)), list(set(zab_metal)))

            else:
                max_list = [colission_sell_dict[metal][1] for metal in colission_sell_dict if (metal not in zab_metal)]
                max_value_index = max_list.index(max(max_list))
                for key in colission_sell_dict:
                    if colission_sell_dict[key][1] == max_list[max_value_index]:
                        zab_metal.append(key)
                        zab_qtr.append(colission_sell_dict[key][0])
                pozost_qtr = P_max_sol(struct, list(set(zab_qtr)), list(set(zab_metal)))

            for metal in pozost_qtr:
                colission_sell_dict[metal] = pozost_qtr[metal]
        return return_opt_sell_dict(struct, colission_sell_dict)


# Funkcja zwracająca informacje o korzystnych kwartałach kupna danego metalu
def find_opt_buy_qtr(struct: Structures, opt_sell: Dict[int, List[int]]):
    d_buy = {}
    for metal_sell in opt_sell:
        buy = []
        for qtr_sell in opt_sell[metal_sell]:
            better_price = float("inf")
            find_qtr = None
            if qtr_sell == 0:
               buy.append(qtr_sell)
            else:
                for f_qtr in range(qtr_sell):
                    if struct.C[metal_sell][f_qtr] < better_price:
                        better_price = struct.C[metal_sell][qtr_sell]
                        find_qtr = f_qtr
                buy.append(find_qtr)
        d_buy[metal_sell] = buy
    return d_buy


# Funkcja zwraca macierz pomocniczą do ustalenia kwartałów produkcji
def fun_matrix_prod(struct: Structures, opt_sell: Dict[int, List[int]], opt_buy: Dict[int, List[int]]):
    matrix_prod = np.zeros(struct.C.shape)
    for metal in opt_sell:
        for j in range(len(opt_sell[metal])):
            if opt_sell[metal][j] == opt_buy[metal][j]:
                matrix_prod[metal][opt_buy[metal][j]] = 4
            else:
                matrix_prod[metal][opt_sell[metal][j]] = 3
                if matrix_prod[metal][opt_buy[metal][j]] != 4:
                    matrix_prod[metal][opt_buy[metal][j]] = 1

    if len(set(matrix_prod[:, 1])) == 1:
        better_price = float("inf")
        f_metal = None
        for metal in opt_buy:
            if struct.C[metal][0] < better_price:
                better_price = struct.C[metal][1]
                f_metal = metal
        matrix_prod[f_metal][1] = 0
        matrix_prod[f_metal][0] = 1

    return matrix_prod


# Wynkcja zwracjaca informacje kiedy produkować dla każdego metalu
def when_pro(struct: Structures, opt_sell: Dict[int, List[int]], opt_buy: Dict[int, List[int]]):
    matrix_prod = fun_matrix_prod(struct, opt_sell, opt_buy)
    qtr_prod = np.zeros(4)
    qtr_zabr = []
    list_of_number_of_met_prod = []
    dict_which_number = {}
    for metal in opt_sell:
        for i in range(len(opt_sell[metal])):
            list_of_number_of_met_prod.append(metal)
            dict_which_number[metal] = list()


    for qtr in range(matrix_prod.shape[1]):
        if qtr not in qtr_zabr:
            if 4 in matrix_prod[:, qtr]:
                metal = list(matrix_prod[:, qtr]).index(4)
                if metal in list_of_number_of_met_prod:
                    qtr_prod[qtr] = int(metal)
                    qtr_zabr.append(qtr)
                    list_of_number_of_met_prod.remove(metal)
                    dict_which_number[metal].append(1)
                    continue
            if 3 in matrix_prod[:, qtr]:
                t_id = [x for x in range(len(list(matrix_prod[:, qtr]))) if list(matrix_prod[:, qtr])[x] == 3]
                for metal in t_id:
                    if metal in list_of_number_of_met_prod:
                        if len(dict_which_number[metal]) == 0:
                            qtr_prod[qtr] = int(metal)
                            qtr_zabr.append(qtr)
                            list_of_number_of_met_prod.remove(metal)
                            dict_which_number[metal].append(1)
                            break
                        if len(dict_which_number) != 0:
                            qtr_prod[qtr] = int(metal)
                            qtr_zabr.append(qtr)
                            list_of_number_of_met_prod.remove(metal)
                            break
                continue
            if 1 in matrix_prod[:, qtr]:
                o_id = [x for x in range(len(list(matrix_prod[:, qtr]))) if list(matrix_prod[:, qtr])[x] == 1]
                for metal in o_id:
                    if metal in list_of_number_of_met_prod:
                        if len(dict_which_number[metal]) == 0:
                            qtr_prod[qtr] = int(metal)
                            qtr_zabr.append(qtr)
                            list_of_number_of_met_prod.remove(metal)
                            dict_which_number[metal].append(1)
                            break
                        if len(dict_which_number) != 0:
                            qtr_prod[qtr] = int(metal)
                            qtr_zabr.append(qtr)
                            list_of_number_of_met_prod.remove(metal)
                            break
                continue
            else:
                for metal in [x for x in range(len(list(matrix_prod[:, qtr])))]:
                    if metal in list_of_number_of_met_prod:
                        qtr_prod[qtr] = int(metal)
                        qtr_zabr.append(qtr)
                        list_of_number_of_met_prod.remove(metal)
                        break

    return qtr_prod


# funkcja zwraca macierz produkcji i kupna(kupno optymalne
# (kupujemy tyle ile możemy wyprodukować) - można zmienić żeby nie była taka)
def fill_M_pr(struct: Structures, opt_buy):
    M_pr_sol = np.zeros((7, 3, 4))
    buy_matrix = np.zeros((3, 4))
    for qtr, p_metal in enumerate(struct.ch_prod):
        p_metal = int(p_metal)
        num_of_k = random.randrange(1, struct.K.shape[0] + 1, 1)  # losowo wygenerowana liczba prób
        which_of_k = np.random.randint(struct.K.shape[0], size=num_of_k)  # lososwo wygenerowana która próba/ poprawić na which
        it_ = math.inf
        while not (ograniczenia.check_time_prod(struct, M_pr_sol, qtr) and ograniczenia.check_popyt_prod(struct, M_pr_sol, qtr, p_metal) and it_ <= 0):
            # obliczenie zapasu czasu i zapasu masy na podstawie zapasu czasu
            time_reserve = struct.T - struct.t[p_metal] * np.sum(M_pr_sol[:, p_metal, qtr])
            product_mass_reserve = int(time_reserve / struct.t[p_metal])
            it_ = num_of_k
            if which_of_k.size == 0:
                it_ = 0
            for el in which_of_k:
                mass_dop = struct.P[el, p_metal, qtr] - M_pr_sol[el, p_metal, qtr]
                if mass_dop > product_mass_reserve:
                    mass_dop = product_mass_reserve
                else:
                    mass_dop = mass_dop
                if mass_dop < 0:
                    continue
                mass_wygen = random.randrange(0, mass_dop + struct.step, struct.step)
                if mass_dop - mass_wygen <= 0: #tutaj w tym ifie torzy ujemną wartość w magazynie
                    M_pr_sol[el, p_metal, qtr] = M_pr_sol[el, p_metal, qtr] + int(mass_dop)
                    buy_matrix[p_metal, int(min(opt_buy[p_metal]))] = buy_matrix[p_metal, int(min(opt_buy[p_metal]))] + int(round((mass_dop+1*struct.step) * struct.K[el]))
                else:
                    M_pr_sol[el, p_metal, qtr] = M_pr_sol[el, p_metal, qtr] + int(mass_wygen)
                    buy_matrix[p_metal, int(min(opt_buy[p_metal]))] = buy_matrix[p_metal, int(min(opt_buy[p_metal]))] + int(round((mass_wygen+1*struct.step) * struct.K[el]))
                it_ = it_ - 1
            if not (ograniczenia.check_time_prod(struct, M_pr_sol, qtr) and ograniczenia.check_popyt_prod(struct, M_pr_sol, qtr, p_metal)):
                M_pr_sol[:, p_metal, qtr] = 0
                buy_matrix[p_metal, int(min(opt_buy[p_metal]))] = 0
    return M_pr_sol, buy_matrix


def fill_sell_matrix(struct: Structures, sol: Solution, opt_sell):
    matrix = np.zeros((7, 3, 4))
    for s_metal in opt_sell:
        qtr_s = opt_sell[s_metal][0]
        qtr_ava = [x for x in range(matrix.shape[2])]
        for x in range(len(opt_sell[s_metal])):
            for qtr, p_metal in enumerate(struct.ch_prod):
                if s_metal == p_metal:
                    if qtr in qtr_ava:
                        if qtr_s >= opt_sell[s_metal][x]:
                            matrix[:, int(s_metal), int(qtr_s)] = matrix[:, int(s_metal), int(qtr_s)] + sol.M_pr[:, int(p_metal), int(qtr)]
                            qtr_ava.remove(qtr)
                            break
                        else:
                            matrix[:, int(s_metal), int(opt_sell[s_metal][x])] = matrix[:, int(s_metal), int(opt_sell[s_metal][x])] + sol.M_pr[:, int(p_metal), int(qtr)]
                            qtr_ava.remove(qtr)

    return matrix




# funkcja ustalajaca od kiedy i przez ile magazynujey surowce
def mag_sur(struct: Structures, sol: Solution) -> Tuple[np.ndarray, np.ndarray]:
    mag_buy = np.zeros(sol.M_pur.shape)
    mag_buy_2 = np.zeros(sol.M_pur.shape)
    matrix_pur = sol.M_pur
    matrix_prod = sol.M_pr
    mag_buy[:, 0] = (matrix_pur[:, 0] - (struct.K @ matrix_prod[:, :, 0]).T).astype(int) #np.array([struct.K @ matrix_prod[:, x, 0] for x in range(mag_buy.shape[0])]).sum(axis=0)
    mag_buy_2[:, 0] = matrix_pur[:, 0]
    for metal in range(mag_buy.shape[0]):
        for qtr in range(1, mag_buy.shape[1]):
            mag_buy[metal, qtr] = int(mag_buy[metal, qtr - 1] + matrix_pur[metal, qtr] - (struct.K @ matrix_prod[:, metal, qtr]).T)
            mag_buy_2[metal, qtr] = int(mag_buy_2[metal, qtr - 1] + matrix_pur[metal, qtr])
    return mag_buy.astype(int), mag_buy_2.astype(int)


# funkcja ustalajaca od kiedy i przez ile magazynujey produkty
def mag_prod(sol: Solution):
    mag_p = np.zeros(sol.M_pr.shape)
    matrix_prod = sol.M_pr
    mag_p[:, :, 0] = matrix_prod[:, :, 0]
    for proba in range(mag_p.shape[0]):
        for metal in range(mag_p.shape[1]):
            for qrt in range(1, mag_p.shape[2]):
                mag_p[proba, metal, qrt] = mag_p[proba, metal, qrt - 1] + matrix_prod[proba, metal, qrt]
    return mag_p


# macierz magazynowania surowców (1,3)
def M_mag_m_(struct: Structures, mag_buy):
    M_mag_m = np.zeros(mag_buy.shape[0])

    for p_metal in range(mag_buy.shape[0]):
        suma = mag_buy[p_metal, 0]
        for qtr in range(1, mag_buy.shape[1]):
            value = mag_buy[p_metal, qtr - 1] - mag_buy[p_metal, qtr]
            suma = suma - value
        if -1*struct.step < suma < struct.step:
            M_mag_m[p_metal] = int(0)
        else:
            M_mag_m[p_metal] = suma
    return M_mag_m

# macierz magazynoania produktów (7,3)
def M_mag_p_(mag_p):
    M_mag_p = np.zeros((mag_p.shape[0], mag_p.shape[1]))

    for p_metal in range(mag_p.shape[1]):
        for proba in range(mag_p.shape[0]):
            suma = mag_p[proba, p_metal, 0]
            for qtr in range(1, mag_p.shape[2]):
                value = mag_p[proba, p_metal, qtr - 1] - mag_p[proba, p_metal, qtr]
                suma = suma - value
            M_mag_p[proba, p_metal] = suma
    return M_mag_p


# 2. wybranie rozwiązania początkowego na podstawie wartości kursów.
def find_start_sol(struct):
    sol = Solution()
    #print("========================================================")
    #print("Iteracja: ", 10-i)
    #print("+++++++++++++++++++max_pinindz+++++++++++")
    max_piniondz = P_max_sol(struct, [], [])
    #print(max_piniondz)
    #print(struct.C)
    #print(prod_collision(max_piniondz))
    #print("+++++++++++++++++++Find_sell_qtr+++++++++++")
    opt_sell = find_sell_qtr(struct, max_piniondz)
    #print(opt_sell)
    #print("+++++++++++++++++++Find_buy_qtr+++++++++++")
    opt_buy = find_opt_buy_qtr(struct, opt_sell)
    #print(opt_buy)
    #print("+++++++++++++++++++matrix_prod+++++++++++")
    #print(fun_matrix_prod(struct, opt_sell, opt_buy))
    #print("+++++++++++++++++++Find_prod_qtr+++++++++++")
    ch_prod_ = when_pro(struct, opt_sell, opt_buy)
    struct.ch_prod = ch_prod_.astype(int)
    #print(ch_prod_)
    #print("+++++++++++++++++++Macierz kupna+++++++++++")
    M_prod_pur = fill_M_pr(struct, opt_buy)
    sol.update_M_pr(M_prod_pur[0].astype(int))
    sol.update_M_pur(M_prod_pur[1].astype(int))
    #print(M_prod_pur[1])
    #print("+++++++++++++++++++Macierz produkcji+++++++++++")
    #print(M_prod_pur[0])
    #print("+++++++++++++++++++Macierz sprzedaży+++++++++++")
    M_sell = fill_sell_matrix(struct, sol, opt_sell)
    sol.update_M_sls(M_sell.astype(int))
    matrix_mag_prod = np.sum(M_sell, axis=2)
    #print(M_sell.shape)
    #print(matrix_mag_prod)
    #print("+++++++++++++++++++Macierz mag surowców+++++++++++")
    mag_buy_ = mag_sur(struct, sol)
    M_mag_ = M_mag_m_(struct, mag_buy_[0])
    sol.update_M_mag_m(M_mag_.astype(int))
    #print(M_mag_)
    #print("+++++++++++++++++++Macierz mag prod+++++++++++")
    mag_prod_ = mag_prod(sol)
    M_prod_ = M_mag_p_(mag_prod_)
    M_prod_ = M_prod_ - matrix_mag_prod
    sol.update_M_mag_p(M_prod_.astype(int))
    #print(M_prod_)
    #print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    #for qtr, p_metal in enumerate(struct.ch_prod):

        #print("Ograniczenie czasowe:", ograniczenia.check_time(struct, sol, qtr))
        #print("Ograniczenia popoytu:", ograniczenia.check_storehouse_sell(M_sell, qtr, p_metal, mag_prod_))
        #print("Ograniczenie magazynu:", ograniczenia.check_masses(struct, sol.M_pr, qtr, mag_buy_[1]))
        #print("Prod: ", sol.M_pr)
        #print("Buy: ", mag_buy_)
    return sol



def proba_generalna():
    i = 100
    while i > 0:
        struct = Structures()
        find_start_sol(struct)
        i = i - 1

#proba_generalna()
