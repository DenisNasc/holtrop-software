import numpy as np


def appendages_resistance(speed=float, appendages={}, CF=float, water_density=float) -> float:

    total_appendage_area = 0
    sum_coefficient_1_k2 = 0

    for key, value in appendages.items():
        total_appendage_area += value['area'] * value['amount']
        sum_coefficient_1_k2 += value['value'] * \
            value['area'] * value['amount']

    equivalent_1_k2 = sum_coefficient_1_k2/total_appendage_area

    RAPP = 0.0005 * water_density * \
        np.power(speed, 2) * total_appendage_area * equivalent_1_k2*CF
    return RAPP
