""" ....... """


# import funkcji odpowiadających za poszczególne otoczenia
from otocz_kupno import pur_surr_1, pur_surr_2, pur_surr_3
from otocz_prod import prod_surr_1, prod_surr_2, prod_surr_3
from otocz_sprz import sls_surr_1, sls_surr_2, sls_surr_3


# znajdywanie rozwiązania z sąsiedztwa:


# zmienna zawierająca uchwyty do poszczególnych funkcji otoczeń
surrs_funs = {'purchase': [pur_surr_1, pur_surr_2, pur_surr_3],
              'production': [prod_surr_1, prod_surr_2, prod_surr_3],
              'sales': [sls_surr_1, sls_surr_2, sls_surr_3]}
