import numpy as np
import json

from resistances.frictional import frictional_resistance


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
    'speeds': [16.0, 15.0]
}


class Constants:
    WATER_DENSITY_OCEAN = 1025.0
    WATER_DENSITY_RIVER = 1000.0
    GRAVITY = 9.81
    # VISCOSIDADE CINEMÁTICA DA ÁGUA A 25°C
    WATER_VISCOSITY_CINEMATIC = 0.000000893


class Ship(Constants):
    def __init__(self, data={}):
        self.form_coefficients = {}
        self.parameters = {}
        self.speeds = {}

        self.is_ocean = data['is_ocean']
        self.parameters['LPP'] = data['LPP']
        self.parameters['LWL'] = data['LWL']
        self.parameters['breadth'] = data['breadth']
        self.parameters['draught'] = (
            data['draught_AP'] + data['draught_FP'])/2
        self.parameters['displacement'] = data['displacement']
        self.parameters['LCB_midship'] = ((data['LCB_AP']+data['LWL']-data['LPP']) -
                                          0.5*data['LWL'])*100/data['LWL']

        self.parameters['transversal_bulb_area'] = data['transversal_bulb_area']
        self.parameters['center_bulb_area'] = data['center_bulb_area']
        self.parameters['transom_area'] = data['transom_area']
        self.parameters['appendages'] = data['appendages']
        self.parameters['C_STERN'] = data['C_STERN']

        self.form_coefficients['CM'] = data['CM']
        self.form_coefficients['CWP'] = data['CWP']

        self.__calculate_speeds(data['speeds'])
        self.__calculate_form_coefficients()

    def __calculate_speeds(self, speeds_knots):
        speeds = {}
        for speed_knot in speeds_knots:
            speed_SI = (speed_knot * 1852)/3600
            reynolds = speed_SI * \
                self.parameters['LWL']/self.WATER_VISCOSITY_CINEMATIC

            speeds[str(speed_knot)] = {'speed_SI': speed_SI,
                                       'reynolds': reynolds
                                       }

        setattr(self, 'speeds', speeds)

    def __calculate_form_coefficients(self):
        CB = self.parameters['displacement'] / \
            (self.parameters['breadth']*self.parameters['LWL']
             * self.parameters['draught'])
        CP = CB/self.form_coefficients['CM']

        self.form_coefficients['CB'] = CB
        self.form_coefficients['CP'] = CP


class Holtrop(Constants):
    def __init__(self, ship: Ship):
        self.ratios = {}
        self.parameters = {}

        if(ship.is_ocean):
            self.parameters['water_density'] = self.WATER_DENSITY_OCEAN
        else:
            self.parameters['water_density'] = self.WATER_DENSITY_RIVER

        self.__calculate_LR(ship)
        self.__calculate_ratios(ship)
        self.__calculate_wetted_surface(ship)

    def __calculate_LR(self, ship):
        CP = ship.form_coefficients['CP']
        LWL = ship.parameters['LWL']
        LCB_midship = ship.parameters['LCB_midship']

        LR = LWL*(1-CP+0.06*CP*LCB_midship/(4*CP-1))
        self.parameters['LR'] = LR

    def __calculate_ratios(self, ship: Ship):
        breadth = ship.parameters['breadth']
        LWL = ship.parameters['LWL']
        draught = ship.parameters['draught']
        displacement = ship.parameters['displacement']

        LR = self.parameters['LR']

        self.ratios['breadth_draught'] = breadth/draught
        self.ratios['breadth_LWL'] = breadth/LWL
        self.ratios['breadth_LR'] = breadth/LR
        self.ratios['draught_LWL'] = draught/LWL
        self.ratios['LWL_LR'] = LWL/LR
        self.ratios['LWL3_displacement'] = np.power(LWL, 3)/displacement

    def __calculate_wetted_surface(self, ship):
        LWL = ship.parameters['LWL']
        draught = ship.parameters['draught']
        breadth = ship.parameters['breadth']
        transversal_bulb_area = ship.parameters['transversal_bulb_area']

        CM = ship.form_coefficients['CM']
        CB = ship.form_coefficients['CB']
        CWP = ship.form_coefficients['CWP']

        ratio_breadth_draught = self.ratios['breadth_draught']

        part_1 = LWL*(2*draught+breadth)*np.sqrt(CM)
        part_2 = (0.453+0.4425*CB-0.2862*CM-0.003467 *
                  ratio_breadth_draught + 0.3696*CWP)
        part_3 = 2.38*transversal_bulb_area/CB

        wetted_surface = part_1 * part_2 + part_3

        self.parameters['wetted_surface'] = wetted_surface


def main():
    babymetal = Ship(holtrop_data)
    babymetal_holtrop = Holtrop(babymetal)

    resistances = {}

    for (speed_knots, value) in babymetal.speeds.items():
        speed_SI = value['speed_SI']
        reynolds = value['reynolds']

        RF = frictional_resistance(
            speed=speed_SI, reynolds=reynolds, **babymetal.parameters, **babymetal.form_coefficients, **babymetal_holtrop.parameters, **babymetal_holtrop.ratios)

        # RAPP = appendages_resistance(
        #     speed=speed_SI, reynolds=reynolds, **babymetal.parameters, **babymetal.form_coefficients, **babymetal_holtrop.parameters, **babymetal_holtrop.ratios)
        resistances[str(speed_knots)] = {
            'RF': RF,
            # 'RAPP': RAPP
        }

    print(json.dumps(resistances))


if __name__ == "__main__":
    main()
