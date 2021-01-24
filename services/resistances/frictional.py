import numpy as np


def calculate_C14(C_STERN: float) -> float:
    # 1+K1 HOLTROP 1984
    C14 = 1 + 0.011*C_STERN
    return C14


def calculate_form_factor(C14=float, **kwargs) -> float:
    # 1+K1 HOLTROP 1984
    ratio_breadth_LWL = kwargs['breadth_LWL']
    ratio_draught_LWL = kwargs['draught_LWL']
    ratio_LWL_LR = kwargs['LWL_LR']
    ratio_LWL3_displacement = kwargs['LWL3_displacement']

    CP = kwargs['CP']

    part_1 = 0.487118*C14*np.power(ratio_breadth_LWL, 1.06806)
    part_2 = np.power(ratio_draught_LWL, 0.46106)
    part_3 = np.power(ratio_LWL_LR, 0.121563)
    part_4 = np.power(ratio_LWL3_displacement, 0.36486)
    part_5 = np.power(1-CP, -0.604247)

    form_factor = 0.93 + (part_1 * part_2 * part_3 * part_4 * part_5)

    return form_factor


def frictional_resistance(speed=float, reynolds=float, **kwargs) -> float:
    # CALCULA A RESISTÂNCIA FRICCIONAL EM NEWTONS

    wetted_surface = kwargs['wetted_surface']
    water_density = kwargs['water_density']

    C14 = calculate_C14(C_STERN=kwargs['C_STERN'])

    form_factor = calculate_form_factor(
        C14=C14,
        **kwargs
    )

    CF = 0.075/np.power(np.log10(reynolds)-2, 2)

    RF = 0.0005 * water_density * np.power(speed, 2) * wetted_surface * CF
    return RF, CF
