# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 10:02:05 2019

@author: yoelr
Modified by Dalton Stewart.
"""
import biosteam as bst

__all__ = ('load_process_settings', 'price',)

# %% Process settings

def load_process_settings():
    bst.CE = 567 # 2013
    bst.PowerUtility.price = 0.065
    HeatUtility = bst.HeatUtility
    steam_utility = HeatUtility.get_agent('low_pressure_steam')
    steam_utility.heat_transfer_efficiency = 0.85
    steam_utility.regeneration_price = 0.30626
    steam_utility.T = 529.2
    steam_utility.P = 44e5
    HeatUtility.get_agent('cooling_water').regeneration_price = 0
    HeatUtility.get_agent('chilled_water').heat_transfer_price = 0

# Raw material price (USD/kg)
price = {'Lipid cane': 0.03455, # 70% m.c
         'Methanol': 0.547,
         'Water': 0.000353,
         'HCl': 0.205,
         'Lime': 0.077,
         'H3PO4': 0, # 0.700, # TODO: find price
         'NaOCH3': 2.93,
         'NaOH':0.41,
         'Protease': 0.5,
         'Polymer': 0, # TODO: find price
         'Crude glycerol': 0.21,
         'Biodiesel': 1.38, # assuming density = 870 kg/m3
         'Ethanol': 0.789,
         'Waste': -0.33,
         'Gasoline': 0.756} # 2 USD/gal


#Input characterization factors from GREET
CFs = {}

#100-year global warming potential [kg CO2-eq / kg]
#If I could not find the compound in GREET I assumed 0 for now.
GWP_CFs = {'H3PO4': 1.06,
           'HCl1': 1.96,
           'HCl2': 1.96,
           'NaOH': 2.19,
           'biodiesel_wash_water':0,
           'boiler_makeup_water':0,
           'catalyst': 4.06,
           'cooling_tower_makeup_water':0,
           'd.23':0,
           'd302':0,
           'd303':0,
           'd304':0,
           'd305':0,
           'denaturant': 20.48,
           'enzyme':0,
           'imbibition_water':0,
           'lime': 1.28,
           'makeup_water':0,
           'methanol': 0.53, #NA NG no co-products
           'natural_gas': 0.33, #NA NG from shale and conventional recovery
           'oil_wash_water':0,
           'polymer':0,
           'recirculated_chilled_water':0,
           'rvf_wash_water':0,
           'stripping_water':0,
           'yeast': 2.51}

GWP_CF_array = chems.kwarray(GWP_CFs)
#in kg CO2-eq/kg of material
GWP_CF_stream = tmo.Stream('GWP_CF_stream', GWP_CF_array, units='kg/hr')

GWP_CFs['Lipidcane'] = 78.90/1000 #for miscanthus, Yalin also multiplied by 0.8, not sure why; for sugarcane in Brazil it's 29.31/1000, wasn't sure what might be more accurate
GWP_CFs['Ethanol_GREET'] = 1.43
GWP_CFs['Biodiesel_GREET'] = 1.14 #from soybeans
#in kg CO2-eq/kWh of electricity
GWP_CFs['Electricity'] = 0.71 #Distributed - US Central and Southern Plains Mix

CFs['GWP_CFs'] = GWP_CFs
CFs['GWP_CF_stream'] = GWP_CF_stream
