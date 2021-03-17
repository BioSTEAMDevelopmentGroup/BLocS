#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:49:59 2021

@author: daltonstewart

Analysis of the effect of various location-specific factors on lipidcane
biorefinery TEA and LCA.

"""
import biosteam as bst
from biorefineries import lipidcane as lc
from chaospy import distributions as shape
import incentives as ti
import numpy as np
import pandas as pd

tea = lc.create_tea(lc.lipidcane_sys, ti.IncentivesTEA)
tea.fuel_tax = 0.332
tea.sales_tax = 0.06
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.12
tea.utility_tax = 0.
tea.ethanol_product = lc.ethanol
tea.biodiesel_product = lc.biodiesel
tea.ethanol_group = lc.ethanol_production_units
tea.biodiesel_group = lc.biodiesel_production_units
tea.BT = lc.BT

model = bst.Model(lc.lipidcane_sys, exception_hook='raise')

@model.metric(name='Utility cost', units='10^6 USD/yr')
def get_utility_cost():
    return tea.utility_cost / 1e6

@model.metric(name='Net electricity production', units='MWh/yr')
def get_electricity_production():
    return sum(i.power_utility.rate for i in lc.lipidcane_sys.units) * tea._operating_hours/1000

@model.metric(name="Baseline MFSP", units='USD/gal')
def MFSP_baseline():
    tea.incentive_numbers = ()
    return 2.98668849 * tea.solve_price(lc.ethanol)

get_exemptions = lambda: tea.exemptions.sum()
get_deductions = lambda: tea.deductions.sum()
get_credits = lambda: tea.credits.sum()
get_refunds = lambda: tea.refunds.sum()

def MFSP_getter(incentive_number):
    def MFSP():
        tea.incentive_numbers = (incentive_number,)
        return 2.98668849 * tea.solve_price(lc.ethanol)
    return MFSP

for incentive_number in range(1, 24):
    # if incentive_number == 21: continue # Doesn't work yet
    element = f"Incentive {incentive_number}"
    model.metric(MFSP_getter(incentive_number), 'MFSP', 'USD/gal', element)
    model.metric(get_exemptions, 'Excemptions', 'USD', element)
    model.metric(get_deductions, 'Deductions', 'USD', element)
    model.metric(get_credits, 'Credits', 'USD', element)
    model.metric(get_refunds, 'Refunds', 'USD', element)

### Create parameter distributions ============================================

# Federal income tax rate, currently 35%, see effects at 30-40%
FITR_dist = shape.Triangle(0.3,0.35,0.4)

# State income tax rates, range from 0% to 12%
SITR_dist = shape.Uniform(0, 0.12)

# State property tax rates
SPTR_dist = shape.Uniform(0.0037, 0.0740)

# State motor fuel tax rates
SMFTR_dist = shape.Uniform(0.0895, 0.586)

# TODO: State utility tax rates

# State sales tax rates
SSTR_dist = shape.Uniform(0, 0.0725)

# Electricity prices, range from 0.0471 to 0.2610 USD/kWh
EP_dist = shape.Uniform(0.0471, 0.2610)

# Feedstock prices, distribution taken from Yoel's example
lipidcane = lc.lipidcane
FP_L = lipidcane.price * 0.9 # min price
FP_U = lipidcane.price * 1.1 # max price

# Feedstock oil contents

# Gasoline prices, USD/gal
GP_dist = shape.Uniform(2.103, 2.934)

# Location capital cost factors
LCCF_dist = shape.Uniform(0.82, 2.56)

# Electricty generation efficiency
EGeff_dist = shape.Triangle(0.7,0.85,0.9)

### Add Parameters =============================================================

# Federal income tax 
@model.parameter(element='TEA', kind='isolated', units='%', distribution=FITR_dist)
def set_fed_income_tax(Federal_income_tax_rate):
    tea.federal_income_tax = Federal_income_tax_rate
    
# State income tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SITR_dist)
def set_state_income_tax(State_income_tax_rate):
    tea.state_income_tax = State_income_tax_rate
    
# State property tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SPTR_dist)
def set_state_property_tax(State_property_tax_rate):
    tea.property_tax = State_property_tax_rate
    
# State motor fuel tax
@model.parameter(element='TEA', kind='isolated', units='USD/gal', distribution=SMFTR_dist)
def set_motor_fuel_tax(fuel_tax_rate):
    tea.fuel_tax = fuel_tax_rate
    
# State sales tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SSTR_dist)
def set_sales_tax(sales_tax_rate):
    tea.sales_tax = sales_tax_rate

#Electricity price
elec_utility = bst.PowerUtility
@model.parameter(element=elec_utility, kind='isolated', units='USD/kWh',
                  distribution=EP_dist)
def set_elec_price(electricity_price):
      elec_utility.price = electricity_price
    
# Feedstock price
@model.parameter(element=lipidcane, kind='isolated', units='USD/kg',
                 distribution=shape.Uniform(FP_L, FP_U))
def set_feed_price(feedstock_price):
    lipidcane.price = feedstock_price
    
# Turbogenerator efficiency
@model.parameter(element=lc.BT, units='%', distribution=EGeff_dist)
def set_turbogenerator_efficiency(turbo_generator_efficiency):
    lc.BT.turbogenerator_efficiency = turbo_generator_efficiency

### Use these to check inputs ==================================================
#  # Use this to check parameters
#  parameters = model.get_parameters()
#  # Use this to check parameter distributions
#  df_dct = model.get_distribution_summary()
#  df_dct['Uniform']
#  df_dct['Triangle']
#  # Use this to evaluate the model
#  model([0.05, 0.85, 8, 100000, 0.040]) #  Returns metrics (IRR and utility cost)

### Perform Monte Carlo analysis ===============================================
np.random.seed(1688)
N_samples = 1000
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N_samples, rule)
model.load_samples(samples)
model.evaluate()
table = model.table

### Perform correlation analysis
sp_rho_table, sp_p_table = model.spearman_r()

get_param_dct = lambda model: {p.name_with_units:p for p in model.get_parameters()}
def filter_parameters(model, df, threshold):
    new_df = pd.concat((df[df>=threshold], df[df<=-threshold]))
    filtered = new_df.dropna(how='all')
    param_dct = get_param_dct(model)
    parameters = set(param_dct[i[1]] for i in filtered.index)
    return parameters

num_original_params = len(model.get_parameters())
key_params = filter_parameters(model, sp_rho_table, 0.1)
num_key_params = len(key_params)

# table.to_excel(r'/Users/daltonstewart/Desktop/screening_results.xlsx', sheet_name='Simulation Results', index = True)
# sp_rho_table.to_excel(r'/Users/daltonstewart/Desktop/screening_results2.xlsx', sheet_name='Spearmans rho', index = True)
# sp_p_table.to_excel(r'/Users/daltonstewart/Desktop/screening_results3.xlsx', sheet_name='Spearmans p', index = True)

bst.plots.plot_montecarlo(model.table['Incentive 1']['MFSP [USD/gal]'])

bst.plots.plot_spearman(sp_rho_table['Biorefinery']['Baseline MFSP [USD/gal]'],top=10)

# this plot doesnt work
# bst.plots.plot_montecarlo_across_coordinate(model.table['Power utility']['Electricity price [USD/kWh]'],(model.table['Incentive 1']['MFSP [USD/gal]'],))