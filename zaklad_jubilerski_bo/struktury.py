""" Rafal711 """


import numpy as np


# zlicza liczbę wymian sprzętu
def counter(tab):
    no_changes = 0
    for i in range(tab.shape[0] - 1):
        if tab[i] != tab[i + 1]:
            no_changes += 1
    return no_changes


# Klasa struktury zawiera stałe wartości
class Structures:
    def __init__(self):
        self.metal_idx = {'zloto': 0, 'srebro': 1, 'platyna': 2, 0: 'zloto', 1: 'srebro', 2: 'platyna'}

        # macierz zawartości metalu w próbie
        self.K = np.array([0.333,             #k = 8
                           0.375,             #k = 9
                           0.5,               #k = 12s
                           0.583,             #k = 14
                           0.750,             #k = 18
                           0.916,             #k = 22
                           0.999])            #k = 24     MOŻEMY DAĆ 1 ALE TO W RZECZYWISTOŚĆI NIEMOŻLIWE

        self.ch_prod = np.random.randint(3, size=(4))   # macierz określająca wybór produkowanego metalu
                                                        # w zależności od kwartału (size - liczba kwartałów)
        self.no_ch = counter(self.ch_prod)              # liczba dokonanych zamian


        self.P = np.random.randint(50, 2000, size=(7, 3, 4))   # macierz popytu, i, j, k - próba, metal, kwartał
        self.C = np.random.randint(1, 10, size=(3, 4))         # ceny metali, C =np.array([c_zl, c_sr, c_pl])
        self.M = np.random.randint(3, 20, size=(7, 3, 4))      # macierz Marż # i, j, k - próba, metal, kwartał
        self.c_mag = np.random.randint(2, 10, size=(3))        # cena magazynowania (za jednostkę masy [g])
                                                               # c_mag = np.array([c_zl, c_sr, c_pl])
        self.c_zam = 20.0                                      # cena jednorazowej zamiany sprzętu
        self.t = np.random.randint(low= 1, high=20, size=(3))  # czas potrzebny na produkcje wybranych surowców
        self.T = 1000000                                       # zasób czasu w jednym kwartale
        self.S = np.random.randint(2, 10, size=(3))            # koszty produkcji 1[g] określonych produktów
        self.step = 10                                         # krok po m.in. masach produktów i surowców


# Klasa Solution zawiera głównie zmienne decyzyjne
class Solution:
    def __init__(self):
        self.M_pr = np.random.randint(20, size=(7, 3, 4))  # masy wyrobow o wybranej probie (całkowita masa przedmiotu)
        self.M_sls = np.random.randint(20, size=(7, 3, 4)) # macierz sprzedaży
        self.M_pur = np.random.randint(20, size=(3, 4))    # macierz zakupu
        self.M_mag_m = np.random.randint(20, size=(3))     # macierz magazynowanego metalu (aktualizowana)
        self.M_mag_p = np.random.randint(20, size=(7, 3))  # macierz magazynowanego produktu
        self.M_mag_sum = np.zeros(shape=3)  # macierz sumy magazynowanego metalu


    def copy(self):
        solution_c = Solution()

        solution_c.M_pr = self.M_pr.copy()
        solution_c.M_sls = self.M_sls.copy()
        solution_c.M_pur = self.M_pur.copy()
        solution_c.M_mag_m = self.M_mag_m.copy()
        solution_c.M_mag_p = self.M_mag_p.copy()
        solution_c.M_mag_sum = self.M_mag_sum.copy()

        return solution_c


    def update_M_pr(self, other):
        self.M_pr = other


    def update_M_sls(self, other):
        self.M_sls = other


    def update_M_pur(self, other):
        self.M_pur = other


    def update_M_mag_m(self, other):
        self.M_mag_m = other


    def update_M_mag_p(self, other):
        self.M_mag_p = other


    def update_M_mag_sum(self, other):
        self.M_mag_sum = other


def mat3d_to_2d(tab3d: np.ndarray):
    tab_3d = tab3d.copy()
    tab_2d = tab_3d.reshape(tab_3d.shape[0], (tab_3d.shape[1] * tab_3d.shape[2]))
    return tab_2d
