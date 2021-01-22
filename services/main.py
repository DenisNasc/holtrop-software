import numpy as np

holtrop_data = {
    'is_ocean': False,
    'LPP': 59.0,
    'LWL': 60.0,
    'breadth': 12.0,
    'draught_AP': 2.0,
    'draught_FP': 2.0,
    'displacement': 1074,
    'LCB_AP': 29.71,
    'transversal_bulb_area': 0,
    'center_bulb_area': 0,
    'CM': 0.883,
    'CWP': 0.97,
    'transom_area': 0.94,
    'appendages': {
        'rudder_behind_skeg': {'amount': 0, 'area': 0, 'value': 2.0},
        'rudder_behind_stern': {'amount': 0, 'area': 0, 'value': 1.5},
        'twin-screw_balance_rudders': {'amount': 0, 'area': 0, 'value': 2.8},
        'shaft_brackets': {'amount': 0, 'area': 0, 'value': 3.0},
        'skeg': {'amount': 0, 'area': 0, 'value': 2.0},
        'strut_bossings': {'amount': 0, 'area': 0, 'value': 3.0},
        'hull_bossings': {'amount': 0, 'area': 0, 'value': 2.0},
        'shafts': {'amount': 0, 'area': 0, 'value': 4.0},
        'stabilizer_fins': {'amount': 0, 'area': 0, 'value': 2.8},
        'dome': {'amount': 0, 'area': 0, 'value': 2.7},
        'bilge_keels': {'amount': 0, 'area': 0, 'value': 1.4},
    },
    'C_STERN': 0,
    'speed': 16.0
}


class Ship:
    WATER_DENSITY_OCEAN = 1025.0
    WATER_DENSITY_RIVER = 1000.0
    GRAVITY = 9.81
    # VISCOSIDADE CINEMÁTICA DA ÁGUA A 25°C
    WATER_VISCOSITY_CINEMATIC = 0.000000893

    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

        self.c_coefficients = {}
        self.ratios = {}
        self.constants = {
            'water_density': None,
            'reynolds': None
        }
        self.resistances = {
            'frictional': None
        }

        if(self.is_ocean):
            self.constants['water_density'] = self.WATER_DENSITY_OCEAN
        else:
            self.constants['water_density'] = self.WATER_DENSITY_RIVER

        self.speed_SI = (self.speed * 1852)/3600

        self.constants['reynolds'] = (
            self.speed_SI*self.LWL)/self.WATER_VISCOSITY_CINEMATIC

        self.draught = (self.draught_AP+self.draught_FP)/2

        self.CB = self.displacement/(self.LWL*self.breadth*self.draught)
        self.CP = self.CB/self.CM

        self.LCB_midship = ((self.LCB_AP+self.LWL-self.LPP) -
                            0.5*self.LWL)*100/self.LWL

        self.__calculate_LR()

        self.ratios['breadth_draught'] = self.breadth/self.draught
        self.ratios['breadth_LWL'] = self.breadth/self.LWL
        self.ratios['breadth_LR'] = self.breadth/self.LR
        self.ratios['draught_LWL'] = self.draught/self.LWL
        self.ratios['LWL_LR'] = self.LWL/self.LR
        self.ratios['LWL3_displacement'] = np.power(
            self.LWL, 3)/self.displacement

        self.__calculate_C12()
        self.__calculate_C14()

        self.__wetted_surface()
        self.__form_factor()

        self.__frictional_resistance()

    def __wetted_surface(self):
        LWL = self.LWL
        draught = self.draught
        breadth = self.breadth
        CM = self.CM
        CB = self.CB
        ratio_breadth_draught = self.ratios['breadth_draught']
        CWP = self.CWP
        transversal_bulb_area = self.transversal_bulb_area

        part_1 = LWL*(2*draught+breadth)*np.sqrt(CM)
        part_2 = (0.453+0.4425*CB-0.2862*CM-0.003467 *
                  ratio_breadth_draught + 0.3696*CWP)
        part_3 = 2.38*transversal_bulb_area/CB

        wetted_surface = part_1 * part_2 + part_3

        setattr(self, 'wetted_surface', wetted_surface)

    def __calculate_LR(self):
        CP = self.CP
        LWL = self.LWL
        LCB_midship = self.LCB_midship

        LR = LWL*(1-CP+0.06*CP*LCB_midship/(4*CP-1))
        setattr(self, 'LR', LR)

    def __calculate_C12(self):
        draught_LWL = self.ratios['draught_LWL']
        C12 = 0.479948

        if(draught_LWL > 0.05):
            C12 = np.power(draught_LWL, 0.2228446)
        elif (draught_LWL <= 0.05 and draught_LWL >= 0.02):
            C12 = 48.2*(np.power(draught_LWL-0.02, 2.078))+0.479948

        self.c_coefficients['C12'] = C12

    def __calculate_C14(self):
        # 1+K1 HOLTROP 1984
        C14 = 1 + 0.011*self.C_STERN
        self.c_coefficients['C14'] = C14

    def __form_factor(self):
        # 1+K1 HOLTROP 1984
        C14 = self.c_coefficients['C14']

        ratio_breadth_LWL = self.ratios['breadth_LWL']
        ratio_draught_LWL = self.ratios['draught_LWL']
        ratio_LWL_LR = self.ratios['LWL_LR']
        ratio_LWL3_displacement = self.ratios['LWL3_displacement']

        LCB_midship = self.LCB_midship
        CP = self.CP

        part_1 = 0.487118*C14*np.power(ratio_breadth_LWL, 1.06806)
        part_2 = np.power(ratio_draught_LWL, 0.46106)
        part_3 = np.power(ratio_LWL_LR, 0.121563)
        part_4 = np.power(ratio_LWL3_displacement, 0.36486)
        part_5 = np.power(1-CP, -0.604247)

        form_factor = 0.93 + (part_1 * part_2 * part_3 * part_4 * part_5)

        setattr(self, 'form_factor', form_factor)

    def __frictional_resistance(self):
        water_density = self.constants['water_density']
        speed = self.speed_SI
        wetted_surface = self.wetted_surface
        reynolds = self.constants['reynolds']
        CF = 0.075/np.power(np.log10(reynolds)-2, 2)

        RF = 0.0005 * water_density * np.power(speed, 2) * wetted_surface * CF
        self.resistances['frictional'] = RF


def main():

    babymetal = Ship(holtrop_data)

    print(f'RF: {babymetal.resistances}')


if __name__ == "__main__":
    main()
