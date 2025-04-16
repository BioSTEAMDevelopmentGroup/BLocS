#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 13:48:51 2025

@author: daltonwstewart
"""

import numpy as np
import pandas as pd
from chaospy import distributions as shape
import biosteam as bst
from biosteam.evaluation import Model, Metric
from biosteam.evaluation.evaluation_tools.parameter import Setter
from biorefineries.SAF._chemicals import SAF_chemicals
from biorefineries.SAF.systems_miscanthus import sys, BT_sys, F, process_groups_dict, process_groups
from biorefineries.SAF._tea import create_SAF_tea
from biorefineries.SAF._process_settings import price, GWP_CFs, load_preferences_and_process_settings
from warnings import warn
from warnings import filterwarnings; filterwarnings('ignore')

import os
folder = os.getcwd()
results_path = folder + '/results/'
results_1 = os.path.join(results_path, '_model_table_BT.xlsx')
results_2 = os.path.join(results_path, '_rho_BT.xlsx')
results_3 = os.path.join(results_path, '_p_BT.xlsx')

_gal_per_m3 = 1000/3.785412
_L_per_gal = 3.785412
_GGE_per_J = 1 / 116090 / 1055.06 # 1 BTU = 1055.06 J, gasoline LHV is 116 090 BTU per gal from https://afdc.energy.gov/fuels/properties
_kJpersec_to_kJhr = 3600

__all__ = ('create_BT_model')



#%%
# This function is not actiavted for figure 1, set split ratio = 0.935283376404842
# @sys.add_bounded_numerical_specification(x0=0, x1=0.3, xtol=1e-4, ytol=100)
# def adjust_bagasse_to_boiler(fraction_burned):
#     F.S102.split[:] = 1 - fraction_burned
#     sys.simulate()
#     F.BT._design()
#     excess = F.BT._excess_electricity_without_natural_gas
#     if fraction_burned == 0 and excess > 0:
#         return 0
#     elif fraction_burned == 0.3 and excess < 0:
#         return 0
#     else:
#         return excess

load_preferences_and_process_settings(T='K',
                                      flow_units='kg/hr',
                                      N=100,
                                      P_units='Pa',
                                      CE=798, # Average 2023 https://toweringskills.com/financial-analysis/cost-indices/
                                      indicator='GWP100',
                                      electricity_EI=GWP_CFs['electricity'],
                                      electricity_price=price['electricity'])
sys.set_tolerance(rmol=1e-6, mol=1e-5, maxiter=400)
tea_SAF = create_SAF_tea(sys=sys)
sys.operating_hours = tea_SAF.operating_days * 24


def set_price_of_streams():
    for i in [F.preprocessing_sys,
              F.pretreatment_sys,
              F.fermentation_sys,
              F.upgrading_sys,
              F.WWT,
              F.BT,
              F.CT,
              F.CWP,
              F.PWC]:
        for j in i.ins:
            if j.ID in price.keys():
                j.price = price[j.ID]
        for k in i.outs:
            if k.ID in price.keys():
                k.price = price[k.ID]

def set_GWP_of_streams(indicator):
    F.caustic.set_CF(key='GWP100', value=GWP_CFs['caustic']) # caustic in WWT
    for i in [F.preprocessing_sys,
              F.pretreatment_sys,
              F.fermentation_sys,
              F.upgrading_sys,
              F.WWT,
              F.BT,
              F.CT,
              F.CWP,
              F.PWC]:
        for j in i.ins:
            if j.ID in GWP_CFs.keys():                
                j.characterization_factors[indicator]= GWP_CFs[j.ID]            
        for k in i.outs:
            if k.ID in GWP_CFs.keys():                
                k.characterization_factors[indicator] = GWP_CFs[k.ID]

set_prices = set_price_of_streams()
set_GWP = set_GWP_of_streams(indicator='GWP100')


# For simplification 
feedstock = F.feedstock
ethanol = F.ethanol_to_storage
jet_fuel = F.jet_fuel
diesel = F.diesel
gasoline = F.gasoline
natural_gas = F.natural_gas
BT = F.BT
HXN = F.HXN

get_annual_factor = lambda: tea_SAF.operating_days * 24

##### Functions to calculate all the metrics #####

# 1. Product characteristics

get_feedstock_use = lambda: feedstock.F_mass * get_annual_factor()
get_h2_use = lambda: F.hydrogen.F_mass * get_annual_factor()

get_feedstock_per_eth = lambda: feedstock.F_mass / ethanol.LHV * 1000 # kg feedstock/ MJ EtOH
get_eth_per_SAF = lambda: ethanol.LHV / jet_fuel.LHV # MJ EtOH / MJ SAF
get_h2_per_SAF = lambda: F.hydrogen.LHV / jet_fuel.LHV # MJ H2/ MJ SAF
get_diesel_per_SAF = lambda: diesel.LHV / jet_fuel.LHV # MJ diesel / MJ SAF
get_gaso_per_SAF = lambda: gasoline.LHV / jet_fuel.LHV # MJ diesel / MJ SAF

get_ethanol_yield = lambda: ethanol.F_vol * _gal_per_m3 * get_annual_factor() / 1e6 # in MMGal (million gallon)
get_jet_yield = lambda:  jet_fuel.F_vol * _gal_per_m3 * get_annual_factor() / 1e6
get_diesel_yield = lambda:  diesel.F_vol * _gal_per_m3 * get_annual_factor() / 1e6
get_gasoline_yield = lambda:  gasoline.F_vol * _gal_per_m3 * get_annual_factor() / 1e6
get_total_yield = lambda:  get_jet_yield() + get_diesel_yield() + get_gasoline_yield()
get_jet_vol_ratio = lambda:  get_jet_yield() / get_total_yield() * 100
get_jet_to_eth_ratio = lambda:  get_jet_yield() / get_ethanol_yield() * 100

get_ethanol_energy = lambda:  ethanol.LHV * get_annual_factor() / 1000 # in MJ a year
get_jet_energy = lambda:  jet_fuel.LHV * get_annual_factor() / 1000
get_diesel_energy = lambda:  diesel.LHV * get_annual_factor() / 1000
get_gasoline_energy = lambda:  gasoline.LHV * get_annual_factor() / 1000

get_total_energy_hour = lambda: (jet_fuel.LHV + diesel.LHV + gasoline.LHV) / 1000
get_total_energy_year = lambda:  get_jet_energy() + get_diesel_energy() + get_gasoline_energy()

get_conversion_efficiency = lambda: get_total_energy_year() / get_ethanol_energy()

get_jet_energy_ratio = lambda: jet_fuel.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV) 
get_diesel_energy_ratio = lambda: diesel.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV) 
get_gasoline_energy_ratio = lambda: gasoline.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV) 


# 2. TEA

get_MPSP = lambda: tea_SAF.solve_price(F.jet_fuel)  # $/kg

_jet_price_conversion_index_vol = lambda: _L_per_gal * jet_fuel.rho / 1000 # from $/kg to $/gal
#_jet_price_conversion_index_energy = lambda: jet_fuel.F_mass / jet_fuel.LHV / 1000 / _GGE_per_J

get_MPSP_per_gallon = lambda: get_MPSP() * _jet_price_conversion_index_vol()
#get_jet_price_per_GGE = lambda: get_MPSP() * _jet_price_conversion_index_energy()
    
get_NPV = lambda: tea_SAF.NPV
solve_IRR = lambda: tea_SAF.solve_IRR()
get_overall_TCI = lambda: tea_SAF.TCI / 1e6 # in $MM      
get_overall_AOC = lambda: tea_SAF.AOC / 1e6 # Excludes electricity credit
get_material_cost = lambda: tea_SAF.material_cost / 1e6 #  Excludes electricity credit but includes the money spent on ash disposal 
get_annual_sale = lambda: tea_SAF.sales / 1e6

# Electricity 
get_excess_power = lambda: -sum(i.power_utility.rate for i in sys.units) * sys.operating_hours # in kWh (+)


metrics = [
           Metric('Minimum selling price_1', get_MPSP, '$/kg'),
           Metric('Minimum selling price', get_MPSP_per_gallon, '$/gal'),
           Metric('Jet volume yield', get_jet_yield, '10^6 Gal/yr'),
           Metric('Total volume yield', get_total_yield, '10^6 Gal/yr'),
           Metric('Jet volume ratio', get_jet_vol_ratio, '%'),
           Metric('Jet energy ratio', get_jet_energy_ratio, '%'),
           Metric('Jet volume ratio to ethanol', get_jet_to_eth_ratio, '%'),
           Metric('Conversion efficiency', get_conversion_efficiency, '%'),
           
           Metric('Total capital investment', get_overall_TCI, '10^6 $'),
           Metric('Annual operating cost', get_overall_AOC, '10^6 $/yr'),
           Metric('Annual material cost', get_material_cost, '10^6 $/yr'),
           
           Metric('Annual excess power', get_excess_power, 'kWh/yr'),]

           


# 3. LCA
# in g CO2 eq / MJ blend fuel

main_product = [jet_fuel]
coproducts = [diesel, gasoline]
#impurities = [CH4_C2H6] # not counted here

emissions = [i for i in F.stream if i.source and not i.sink and i not in main_product and i not in coproducts]


# Carbon balance
total_C_in = lambda: sum([feed.get_atomic_flow('C') for feed in sys.feeds])
total_C_out = lambda: sum([i.get_atomic_flow('C') for i in emissions]) + sum([i.get_atomic_flow('C') for i in main_product]) +\
              sum([i.get_atomic_flow('C') for i in coproducts]) 
get_C_bal_error = lambda: (total_C_out() - total_C_in())/total_C_in()

metrics.extend((Metric('Carbon error', get_C_bal_error, '', 'Carbon'),))


# Feedstock contribution
get_GWP_feedstock_input = lambda: sys.get_material_impact(feedstock, key='GWP100') * 1000 / get_total_energy_year()

# Only consider non-biogenic emissions (M301+CSL+NG)
get_GWP_emissions_non_BT = lambda: (F.CSL.get_atomic_flow('C') + F.enzyme_M301.get_atomic_flow('C'))\
                                  * SAF_chemicals.CO2.MW * 1000 / get_total_energy_hour()
# NG emissions (BT)
get_GWP_emissions_BT = lambda: F.natural_gas.get_atomic_flow('C') * SAF_chemicals.CO2.MW * 1000 / get_total_energy_hour()

# Transportation contribution
get_GWP_emissions_trans_feedstock = lambda: (feedstock.F_mass * 100) * 0.0514 / get_total_energy_hour() # g CO2 for MJ fuel

get_GWP_emissions_trans_SAF = lambda: (jet_fuel.F_mass * 600) * 0.0514 / get_total_energy_hour() # g CO2 for MJ fuel

# Material contribution
get_GWP_material_total = lambda: sys.get_total_feeds_impact('GWP100') * 1000 / get_total_energy_year()

get_GWP_NG = lambda: sys.get_material_impact(natural_gas, key='GWP100') * 1000 / get_total_energy_year()


# Total = material + emission
get_GWP_total = lambda: get_GWP_material_total() + get_GWP_emissions_BT() + get_GWP_emissions_non_BT() + \
    + get_GWP_emissions_trans_feedstock() + get_GWP_emissions_trans_SAF() # in g CO2 for MJ fuel

# GWP allocation (displacement)
get_total_energy_year_inc_ele = lambda: (jet_fuel.LHV + diesel.LHV + gasoline.LHV + get_excess_electricity_energy()) * get_annual_factor() / 1000 # MJ per year

get_GWP_electricity_credit = lambda: get_excess_power() * bst.PowerUtility.characterization_factors['GWP100'][0] * 1000 / get_total_energy_year_inc_ele() # g CO2/MJ

get_GWP_fuel_credit = lambda: (sys.get_material_impact(diesel, key='GWP100') + \
                               sys.get_material_impact(gasoline, key='GWP100')) * 1000 / get_total_energy_year_inc_ele()

get_GWP_jet_disp = lambda: get_GWP_total() * get_total_energy_year() / get_total_energy_year_inc_ele() - get_GWP_electricity_credit() + get_GWP_fuel_credit()

# GWP allocation (energy)
get_excess_electricity_energy = lambda: get_excess_power() * 3600 / sys.operating_hours # KJ per hour

jet_energy_ratio_2 = lambda: jet_fuel.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV + get_excess_electricity_energy()) 
diesel_energy_ratio_2 = lambda: diesel.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV + get_excess_electricity_energy())
gasoline_energy_ratio_2 = lambda: gasoline.LHV / (jet_fuel.LHV + diesel.LHV + gasoline.LHV + get_excess_electricity_energy())
excess_electricity_energy_ratio_2 = lambda: get_excess_electricity_energy() / (jet_fuel.LHV + diesel.LHV + gasoline.LHV + get_excess_electricity_energy())
    
get_GWP_jet_energy = lambda: get_GWP_total() * get_total_energy_year() / get_total_energy_year_inc_ele() * jet_energy_ratio_2()

get_GWP_diesel_energy= lambda: get_GWP_total() * get_total_energy_year() / get_total_energy_year_inc_ele() * diesel_energy_ratio_2()

get_GWP_gasoline_energy = lambda: get_GWP_total() * get_total_energy_year() / get_total_energy_year_inc_ele() * gasoline_energy_ratio_2()

get_GWP_electricity_energy = lambda: get_GWP_total() * get_total_energy_year() / get_total_energy_year_inc_ele() * excess_electricity_energy_ratio_2()

# GWP allocation (hybrid)
get_GWP_electricity_credit_2 = lambda: get_excess_power() * bst.PowerUtility.characterization_factors['GWP100'][0] * 1000 / get_total_energy_year() # g CO2/MJ

get_GWP_jet_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_jet_energy_ratio()

get_GWP_diesel_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_diesel_energy_ratio()

get_GWP_gasoline_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_gasoline_energy_ratio()

# Power generation (per hour)
get_steam_heating = lambda: sum([i.duty for i in BT.steam_utilities]) # kJ/hr

get_steam_electricity = lambda: 3600 * BT.power_utility.production / BT.turbogenerator_efficiency

get_steam_electricity_excess = lambda: 3600 * get_excess_power_hourly() / BT.turbogenerator_efficiency

get_steam_total = lambda: get_steam_heating() + get_steam_electricity()

get_steam_total_per_mis = lambda: get_steam_total() / (1-F.S102.split[0]) / feedstock.F_mass

get_excess_power_hourly = lambda: -sum(i.power_utility.rate for i in sys.units)

get_excess_power_per_mis = lambda: get_excess_power_hourly() / (1-F.S102.split[0]) / feedstock.F_mass



metrics.extend((Metric('GWP - total', get_GWP_total, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - electricity credit', get_GWP_electricity_credit, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - feedstock', get_GWP_feedstock_input, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - NG', get_GWP_NG, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - non biogenic emissions', get_GWP_emissions_BT, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - other non biogenic emissions', get_GWP_emissions_non_BT, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - transp_feedstock', get_GWP_emissions_trans_feedstock, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP - transp_SAF', get_GWP_emissions_trans_SAF, 'g CO2-eq/MJ blend fuel', 'LCA'),))

metrics.extend((Metric('GWP_displacement - jet', get_GWP_jet_disp, 'g CO2-eq/MJ jet fuel', 'LCA'),))

metrics.extend((Metric('GWP_displacement', get_GWP_fuel_credit, 'g CO2-eq/MJ jet fuel', 'LCA'),))

metrics.extend((Metric('GWP_energy - jet', get_GWP_jet_energy, 'g CO2-eq/MJ jet fuel', 'LCA'),))

metrics.extend((Metric('GWP_energy - diesel', get_GWP_diesel_energy, 'g CO2-eq/MJ diesel', 'LCA'),))

metrics.extend((Metric('GWP_energy - gasoline', get_GWP_gasoline_energy, 'g CO2-eq/MJ gasoline', 'LCA'),))

metrics.extend((Metric('GWP_energy - elec', get_GWP_electricity_energy, 'g CO2-eq/MJ elec', 'LCA'),))

metrics.extend((Metric('GWP_hybrid- jet', get_GWP_jet_hybrid, 'g CO2-eq/MJ jet', 'LCA'),))

metrics.extend((Metric('GWP_hybrid- diesel', get_GWP_diesel_hybrid, 'g CO2-eq/MJ diesel', 'LCA'),))

metrics.extend((Metric('GWP_hybrid- gsaoline', get_GWP_gasoline_hybrid, 'g CO2-eq/MJ diesel', 'LCA'),))

metrics.extend((Metric('Total_energy', get_total_energy_year, 'MJ fuel', 'LCA'),))

metrics.extend((Metric('Total_energy_inc_ele', get_total_energy_year_inc_ele, 'MJ', 'LCA'),))

metrics.extend((Metric('BT-get_steam_heating', get_steam_heating, 'kJ/hr', 'Biorefinery'),))

metrics.extend((Metric('BT-get_steam_electricity', get_steam_electricity, 'kJ/hr', 'Biorefinery'),))

metrics.extend((Metric('BT-get_steam_electricity_excess', get_steam_electricity_excess, 'kJ/hr', 'Biorefinery'),))

metrics.extend((Metric('BT-get_steam_total', get_steam_total, 'kJ/hr', 'Biorefinery'),))

metrics.extend((Metric('BT-get_steam_total_per_mis', get_steam_total_per_mis, 'kJ/kg', 'Biorefinery'),))

metrics.extend((Metric('BT-get_excess_power_hourly', get_excess_power_hourly, 'kW', 'Biorefinery'),))

metrics.extend((Metric('BT-get_excess_power_per_mis', get_excess_power_per_mis, 'kW/kg', 'Biorefinery'),))




# Generate split values from 0 to 1 with a step of 0.01
split_values = np.linspace(0.1, 1, 91)  # More robust than np.arange

def run_simulation(split):
    results = []

    for i in range(3):  # Run simulation 3 times for robustness
        F.S102.split = split
        sys.simulate()
        
        excess_power = get_excess_power_hourly()
        excess_power_per_ethanol = excess_power * 3600 / ethanol.LHV
        excess_power_per_jet = excess_power * 3600 / jet_fuel.LHV
        jet_CI_hybrid = get_GWP_jet_hybrid()
        jet_CI_energy = get_GWP_jet_energy()
        
        results.append([excess_power, excess_power_per_ethanol, excess_power_per_jet, jet_CI_hybrid, jet_CI_energy])
    
    # Compute the average across 3 runs
    avg_excess_power, avg_excess_power_per_ethanol, avg_excess_power_per_jet, avg_jet_CI_hybrid, avg_jet_CI_energy = np.mean(results, axis=0)
    
    return avg_excess_power, avg_excess_power_per_ethanol, avg_excess_power_per_jet, avg_jet_CI_hybrid, avg_jet_CI_energy

# Store results
results_data = []

for split in split_values:
    avg_results = run_simulation(split)
    results_data.append([split] + list(avg_results))  # First column: split ratio

# Convert results to DataFrame
columns = ["Split Ratio", "Excess Power", "Excess Power per Ethanol", "Excess Power per Jet", "Jet_CI_hybrid", "Jet_CI_energy"]
df_results = pd.DataFrame(results_data, columns=columns)

# Save results to an Excel sheet
df_results.to_excel("simulation_results.xlsx", index=False)






#%%
def create_model():
    model = Model(sys, metrics, exception_hook='raise')
    param = model.parameter
    
    # D = shape.Uniform(0, 1.0)
    @param(name='Split ratio', element='S102', kind='coupled', units='%',
           baseline=None, distribution=None)
    def set_split_ratio(X):
        F.S102.specifications[0].args[0] = X
    
    @param(name='Feedstock price', element='feedstock', kind='isolated', units='$/kg',
           baseline=None, distribution=None)
    def set_feedstock_price(feedstock_price):
        feedstock.price = feedstock_price
        
    return model

model = create_model()
system = model._system

def reset_and_reload():
    print('Resetting cache and emptying recycles ...')
    system.reset_cache()
    system.empty_recycles()
def reset_and_switch_solver(solver_ID):
    system.reset_cache()
    system.empty_recycles()
    system.converge_method = solver_ID
    print(f"Trying {solver_ID} ...")
def run_bugfix_barrage():
    try:
        reset_and_reload()
        system.simulate()
    except Exception as e:
        print(str(e))
        try:
            reset_and_switch_solver('fixedpoint')
            system.simulate()
        except Exception as e:
            print(str(e))
            try:
                reset_and_switch_solver('aitken')
                system.simulate()
            except Exception as e:
                print(str(e))
                # print(_yellow_text+"Bugfix barrage failed.\n"+_reset_text)
                print("Bugfix barrage failed.\n")
                # breakpoint()
                raise e
def model_specification():
    try:
        system.simulate()
    except Exception as e:
        str_e = str(e).lower()
        print('Error in model spec: %s'%str_e)
        run_bugfix_barrage()

def run_model(model=model, notify_runs=10):
    df = pd.read_excel('data_processing.xlsx',sheet_name='samples_BT')
    sample_list = []
    for i in range(1,102):
        row_as_list = df.iloc[i, 0:].tolist() 
        sample_list.append(row_as_list)    
    sample_list = np.array(sample_list)
    model.load_samples(sample_list)
    model.evaluate(notify=notify_runs)
    model.table.to_excel(results_1)
    df_rho,df_p = model.spearman_r()
    df_rho.to_excel(results_2)
    df_p.to_excel(results_3)
    return model



run_model()


        
