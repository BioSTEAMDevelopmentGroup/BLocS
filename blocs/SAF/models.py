#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 17 13:57:09 2024

@author: wenjun
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
results_1 = os.path.join(results_path, '_model_table_0.935.xlsx')
results_2 = os.path.join(results_path, '_rho_0.935.xlsx')
results_3 = os.path.join(results_path, '_p_0.935.xlsx')

_gal_per_m3 = 1000/3.785412
_L_per_gal = 3.785412
_GGE_per_J = 1 / 116090 / 1055.06 # 1 BTU = 1055.06 J, gasoline LHV is 116 090 BTU per gal from https://afdc.energy.gov/fuels/properties
_kJpersec_to_kJhr = 3600

__all__ = ('create_model')

#%%
# This function is not actiavted for figure 1, set split ratio = 0.935283376404842
@sys.add_bounded_numerical_specification(x0=0, x1=0.3, xtol=1e-4, ytol=100)
def adjust_bagasse_to_boiler(fraction_burned):
    F.S102.split[:] = 1 - fraction_burned
    sys.simulate()
    F.BT._design()
    excess = F.BT._excess_electricity_without_natural_gas
    if fraction_burned == 0 and excess > 0:
        return 0
    elif fraction_burned == 0.3 and excess < 0:
        return 0
    else:
        return excess

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
get_biomass_split_to_ethanol = lambda: F.S102.split[0]

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


metrics = [Metric('Split ratio', get_biomass_split_to_ethanol, ''),
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

get_GWP_electricity_credit = lambda: get_excess_power() * bst.PowerUtility.characterization_factors['GWP100'] * 1000 / get_total_energy_year_inc_ele() # g CO2/MJ

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
get_GWP_electricity_credit_2 = lambda: get_excess_power() * bst.PowerUtility.characterization_factors['GWP100'] * 1000 / get_total_energy_year() # g CO2/MJ

get_GWP_jet_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_jet_energy_ratio()

get_GWP_diesel_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_diesel_energy_ratio()

get_GWP_gasoline_hybrid = lambda: (get_GWP_total() - get_GWP_electricity_credit_2()) * get_gasoline_energy_ratio()



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


#%%
def create_model():
    model = Model(sys, metrics, exception_hook='raise')
    param = model.parameter
    
    @param(name='Feedstock GWP', element='feedstock', kind='isolated', units='kg CO2/kg',
           baseline=None, distribution=None)
    def set_feedstock_GWP(feedstock_GWP):
        feedstock.characterization_factors['GWP100'] = feedstock_GWP
    
    @param(name='Feedstock price', element='feedstock', kind='isolated', units='$/kg',
           baseline=None, distribution=None)
    def set_feedstock_price(feedstock_price):
        feedstock.price = feedstock_price
    
    @param(name='Electricity GWP', element='electricity', kind='isolated', units='kg CO2/kWh',
           baseline=None, distribution=None)
    def set_electricity_GWP(electricity_GWP):
        bst.PowerUtility.characterization_factors['GWP100'] = electricity_GWP
        
    @param(name='Electricity price', element='electricity', kind='isolated', units='$/kWh',
           baseline=None, distribution=None)
    def set_electricity_price(electricity_price):
        bst.PowerUtility.price = electricity_price
    
    @param(name='LCCF', element='TEA', kind='isolated', units='% baseline',
           baseline=None, distribution=None)
    def set_TCI_ratio(new_ratio):
        old_ratio = tea_SAF._TCI_ratio_cached
        for unit in sys.units:
            if hasattr(unit, 'cost_items'):
                for item in unit.cost_items:
                    unit.cost_items[item].cost /= old_ratio
                    unit.cost_items[item].cost *= new_ratio
        tea_SAF._TCI_ratio_cached = new_ratio
    
    # D = shape.Triangle(0.84, 0.9, 0.96)
    # @param(name='Plant uptime', element='TEA', kind='isolated', units='%',
    #        baseline=0.9, distribution=D)
    # def set_operating_days(uptime):
    #     tea_SAF.operating_days = 365. * uptime
    
  
    
    # D = shape.Triangle(10, 20, 30)
    # @param(name='Enzyme loading', element=F.M301, kind='coupled', units='mg/g',
    #        baseline=20, distribution=D)
    # def set_R301_enzyme_loading(loading):
    #     F.M301.enzyme_loading = loading
    
    # D = shape.Triangle(0.75, 0.9, 0.948-1e-6)
    # @param(name='Enzymatic hydrolysis glucan-to-glucose', element=F.R301, kind='coupled', units='%',
    #        baseline=0.9, distribution=D)
    # def set_R301_glucan_to_glucose_conversion(X):
    #     F.R301.saccharification_rxns[3].X = X
    
    # D = shape.Triangle(0.9, 0.95, 0.97)
    # @param(name='Fermentation glucose-to-ethanol', element=F.R301, kind='coupled', units='%',
    #        baseline=0.95, distribution=D)
    # def set_R301_glucose_to_ethanol_conversion(X):
    #     F.R301.cofermentation_rxns[0].X = X
    
    # D = shape.Uniform(0.995*0.988*0.9, 0.995*0.988)
    # @param(name='Dehydration ethanol-to-ethylene', element=F.R401, kind='coupled', units='%',
    #         baseline=0.995*0.988, distribution=D)
    # def set_R401_ethanol_conversion(X):
    #     F.R401.dehydration_rxns[0].X = X
    
    # BT = F.BT
    # D = shape.Uniform(0.8*(1-0.1), 0.8*(1+0.1))
    # @param(name='Boiler efficiency', element=BT, kind='coupled', units='',
    #        baseline=0.8, distribution=D)
    # def set_boiler_efficiency(efficiency):
    #     BT.boiler_efficiency = efficiency
        
    # BT = F.BT
    # D = shape.Uniform(0.765, 0.935)
    # @param(name='Turbogenerator efficiency', element=BT, kind='coupled', units='',
    #        baseline=0.85, distribution=D)
    # def set_turbo_efficiency(efficiency):
    #     BT.turbo_generator_efficiency = efficiency
    
    # D = shape.Uniform(1.5624*(1-0.5), 1.5624*(1+0.5))
    # @param(name='H2 GWP', element='H2', kind='isolated', units='kg CO2-eq/kg',
    #        baseline=1.5624, distribution=D)
    # def set_H2_GWP(X):
    #     F.hydrogen.characterization_factors['GWP100'] = X
    
    # D = shape.Triangle(50, 100, 500)
    # @param(name='feed_trans_d', element='tran', kind='isolated', units='km',
    #        baseline=100, distribution=D)
    # def set_feed_trans_d(X):
    #     tea_SAF.feedstock_trans_d = X
    
    # D = shape.Triangle(200, 600, 3000)
    # @param(name='SAF_trans_d', element='tran', kind='isolated', units='km',
    #        baseline=600, distribution=D)
    # def set_SAF_trans_d(X):
    #     tea_SAF.SAF_trans_d = X
    
    # D = shape.Uniform(0.0000514*0.5, 0.0000514*1.5)
    # @param(name='truck CI', element='tran', kind='isolated', units='kg CO2e/km/kg',
    #        baseline=0.0000514, distribution=D)
    # def set_truck_CI(X):
    #     tea_SAF.truck_CI = X
    
    # D = shape.Uniform(0.0000148*0.5, 0.0000148*1.5)
    # @param(name='train CI', element='tran', kind='isolated', units='kg CO2e/km/kg',
    #        baseline=0.0000148, distribution=D)
    # def set_train_CI(X):
    #     tea_SAF.train_CI = X
    
    # D = shape.Uniform(0.61, 1.76)
    # @param(name='RFS credit price', element='TEA', kind='isolated', units='$/D4RIN',
    #        baseline=1.2, distribution=D)
    # def set_RFS(X):
    #     tea_SAF.RFS_credit = X
    
    # D = shape.Uniform(34, 335)
    # @param(name='LCFS credit price', element='TEA', kind='isolated', units='$/credit',
    #        baseline=154, distribution=D)
    # def set_LCFS(X):
    #     tea_SAF.LCFS_credit = X
        
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
    df = pd.read_excel('data_processing.xlsx',sheet_name='samples')
    sample_list = []
    for i in range(2,12750):
        row_as_list = df.iloc[i, 1:].tolist() 
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








