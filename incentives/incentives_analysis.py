#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:49:59 2021

@author: daltonstewart

Analysis of the effect of various location-specific factors on lipidcane
biorefinery TEA and LCA.

"""
import biosteam as bst
from biorefineries import cornstover as cs
from chaospy import distributions as shape
from biosteam.evaluation.evaluation_tools import triang
import incentives as ti
import numpy as np
import pandas as pd
import os

tea = ti.create_cornstover_tea()
tea.fuel_tax = 0.05
tea.sales_tax = 0.05785
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.065
tea.property_tax = 0.0136
tea.utility_tax = 0.
tea.ethanol_product = cs.ethanol
# tea.biodiesel_product = lc.biodiesel
tea.ethanol_group = bst.UnitGroup(cs.cornstover_sys.units)
# tea.biodiesel_group = lc.biodiesel_production_units
tea.feedstock = cs.cornstover
tea.F_investment = 1
tea.BT = cs.BT
bst.PowerUtility.price = 0.0685

model = bst.Model(tea.system, exception_hook='raise')

@model.metric(name='Utility cost', units='10^6 USD/yr')
def get_utility_cost():
    return tea.utility_cost / 1e6

@model.metric(name='Net electricity production', units='MWh/yr')
def get_electricity_production():
    return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours/1000

@model.metric(name='Ethanol production', units='gal/yr')
def get_ethanol_production():
    return tea.ethanol_product.F_mass * 2.98668849 * tea.operating_hours

@model.metric(name='Total capital investment', units='USD')
def get_TCI():
    return tea.TCI

@model.metric(name="Baseline MFSP", units='USD/gal') #within this function, set whatever parameter values you want to use as the baseline
def MFSP_baseline():
    tea.incentive_numbers = ()
    MFSP_baseline_box[0] = MFSP = 2.98668849 * tea.solve_price(tea.ethanol_product)
    return MFSP

MFSP_baseline_box = [None]

get_exemptions = lambda: tea.exemptions.sum()
get_deductions = lambda: tea.deductions.sum()
get_credits = lambda: tea.credits.sum()
get_refunds = lambda: tea.refunds.sum()

def MFSP_getter(incentive_number):
    def MFSP():
        tea.incentive_numbers = (incentive_number,)
        return 2.98668849 * tea.solve_price(tea.ethanol_product)
    return MFSP

def MFSP_reduction_getter(incentive_number):
    def MFSP():
        tea.incentive_numbers = (incentive_number,)
        return (2.98668849 * tea.solve_price(tea.ethanol_product) - MFSP_baseline_box[0])
    return MFSP

for incentive_number in range(1, 24):
    element = f"Incentive {incentive_number}"
    model.metric(MFSP_getter(incentive_number), 'MFSP', 'USD/gal', element)
    model.metric(MFSP_reduction_getter(incentive_number), 'MFSP Reduction', 'USD/gal', element)
    model.metric(get_exemptions, 'Exemptions', 'USD', element)
    model.metric(get_deductions, 'Deductions', 'USD', element)
    model.metric(get_credits, 'Credits', 'USD', element)
    model.metric(get_refunds, 'Refunds', 'USD', element)

# @model.metric(name="MFSP Reduction", units='USD/gal', element='Incentive 24')
# def MFSP():
#     tea.incentive_numbers = ()
#     tea.depreciation_incentive_24(True)
#     MFSP = 2.98668849 * tea.solve_price(lc.ethanol)
#     tea.depreciation_incentive_24(False)
#     MFSP_baseline = 2.98668849 * tea.solve_price(lc.ethanol)
#     np.testing.assert_allclose(MFSP_baseline, MFSP_baseline_box[0], rtol=1e-3)
#     return MFSP - MFSP_baseline_box[0]

### Create parameter distributions ============================================

# Federal income tax rate, currently 35%, see effects at 30-40%
FITR_dist = shape.Triangle(0.3,0.35,0.4)

# State income tax rates, range from 0% to 12%

SITR_dist = shape.Uniform(0, 0.12)

# State property tax rates
# SPTR_dist = shape.Triangle(0.0037, 0.006, 0.0369) #not simulating full range bc it has extreme effects
SPTR_dist = shape.Uniform(0.0037, 0.0369)

# State motor fuel tax rates
SMFTR_dist = shape.Triangle(0, 0.05, 0.1)

# State utility tax rates
SUTR_dist = shape.Triangle(0, 0.02, 0.05)

# State sales tax rates
SSTR_dist = shape.Triangle(0, 0.055, 0.0725)

# Electricity prices, range from 0.0471 to 0.2610 USD/kWh
EP_dist = shape.Triangle(0.0471, 0.0685, 0.1007) #not simulating full range bc it has extreme effects

# Feedstock prices, distribution taken from Emma's lit review
feedstock = tea.feedstock
FP_L = 0.02 # min price
FP_M = 0.048 # mode price
FP_U = 0.111 # max price

#Total capital investment
TCI_L = tea.TCI * 0.9
TCI_U = tea.TCI * 1.1

# Feedstock oil contents

# Gasoline prices, USD/gal
GP_dist = shape.Uniform(2.103, 2.934)

# Location capital cost factors
LCCF_dist = shape.Triangle(0.82, 1, 1.22) #not simulating full range bc it has extreme effects

# Electricty generation efficiency
EGeff_dist = shape.Triangle(0.7,0.85,0.9)

### Add Parameters =============================================================
## Highly relevant contextual parameters

# # Federal income tax 
# @model.parameter(element='TEA', kind='isolated', units='%', distribution=FITR_dist)
# def set_fed_income_tax(Federal_income_tax_rate):
#     tea.federal_income_tax = Federal_income_tax_rate
    
# State income tax
# @model.parameter(element='TEA', kind='isolated', units='%', distribution=SITR_dist)
# def set_state_income_tax(State_income_tax_rate):
#     tea.state_income_tax = State_income_tax_rate
    
# # State property tax
# @model.parameter(element='TEA', kind='isolated', units='%', distribution=SPTR_dist)
# def set_state_property_tax(State_property_tax_rate):
#     tea.property_tax = State_property_tax_rate
    
# # State motor fuel tax
# @model.parameter(element='TEA', kind='isolated', units='USD/gal', distribution=SMFTR_dist)
# def set_motor_fuel_tax(fuel_tax_rate):
#     tea.fuel_tax = fuel_tax_rate

#State utility tax
# @model.parameter(element='TEA', kind='isolated', units='%', distribution=SUTR_dist)
# def set_util_tax(util_tax_rate):
#     tea.utility_tax = util_tax_rate
    
# State sales tax
# @model.parameter(element='TEA', kind='isolated', units='%', distribution=SSTR_dist)
# def set_sales_tax(sales_tax_rate):
#     tea.sales_tax = sales_tax_rate

# # Electricity price
# elec_utility = bst.PowerUtility
# @model.parameter(element=elec_utility, kind='isolated', units='USD/kWh',
#                   distribution=EP_dist)
# def set_elec_price(electricity_price):
#       elec_utility.price = electricity_price
      
# # Location capital cost factor
# @model.parameter(element='Location', kind='isolated', units='unitless', distribution=LCCF_dist)
# def set_LCCF(LCCF):
#     tea.F_investment = LCCF
      
# Feedstock price
@model.parameter(element=feedstock, kind='isolated', units='USD/kg',
                  distribution=shape.Triangle(FP_L, FP_M, FP_U))
def set_feed_price(feedstock_price):
    feedstock.price = feedstock_price

# Total capital investment
# @model.parameter(element='TEA', kind='isolated', units='USD',
#                   distribution=shape.Uniform(TCI_L, TCI_U))
# def set_TCI(TCI):
#     tea.TCI = TCI
    
#: WARNING: these distributions are arbitrary and a thorough literature search
#: and an analysis of U.S. biodiesel, ethanol price projections should be made 
#: to include these
    
##Innate uncertainty in biorefinery operations

# Plant capacity
@model.parameter(element=feedstock, kind='isolated', units='kg/hr',
                      distribution=triang(feedstock.F_mass))
def set_plant_capacity(plant_capacity):
        feedstock.F_mass = plant_capacity

if tea.BT:
        # Boiler efficiency
        @model.parameter(element=tea.BT, units='%', distribution=triang(tea.BT.boiler_efficiency))
        def set_boiler_efficiency(boiler_efficiency):
            tea.BT.boiler_efficiency = boiler_efficiency    
        
        # Turbogenerator efficiency
        @model.parameter(element=tea.BT, units='%', distribution=EGeff_dist)
        def set_turbogenerator_efficiency(turbo_generator_efficiency):
            tea.BT.turbogenerator_efficiency = turbo_generator_efficiency

# Fermentation efficiency
# fermentation = lc.R301
# @model.parameter(
#     element=fermentation, distribution=shape.Triangle(0.85, 0.90, 0.95),
#     baseline=fermentation.efficiency,
# )
# def set_fermentation_efficiency(efficiency):
#     fermentation.efficiency= efficiency

# # Biodiesel price
# @model.parameter(
#     element=lc.biodiesel, distribution=triang(lc.biodiesel.price),
#     baseline=lc.biodiesel.price,
# )
# def set_biodiesel_price(price):
#     lc.biodiesel.price = price

# # Ethanol price
# @model.parameter(
#     element=lc.ethanol, distribution=triang(lc.ethanol.price),
#     baseline=lc.ethanol.price,
# )
# def set_ethanol_price(price):
#     lc.ethanol.price = price

# Lipid fraction
# Originally 0.10, but this is much to optimistic. In fact,
# even 0.05 is optimistic.
# model.parameter(lc.set_lipid_fraction, element=lc.lipidcane,
#                 distribution=triang(0.05), baseline=0.05)

### Use these to check inputs ==================================================
#  # Use this to check parameters
#  parameters = model.get_parameters()
#  # Use this to check parameter distributions
#  df_dct = model.get_distribution_summary()

### Perform Monte Carlo analysis ===============================================
# model.load_default_parameters(tea.feedstock,operating_days=True)
np.random.seed(1688)
N_samples = 100
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N_samples, rule)
model.load_samples(samples)
model.evaluate()
table = model.table

## Perform correlation analysis
# sp_rho_table, sp_p_table = model.spearman_r()


### Plot across coordinate
##Electricity price, typical taxes
# parameters = list(model.get_parameters())
# parameters.remove(set_elec_price)
# model_without_electricity = bst.Model(lc.lipidcane_sys, 
#                                       metrics=model.metrics,
#                                       parameters=parameters,
#                                       exception_hook='raise')
# samples = model_without_electricity.sample(N_samples, rule)
# model_without_electricity.load_samples(samples)
# folder = os.path.dirname(__file__)
# dct = model_without_electricity.evaluate_across_coordinate(
#     'Electricity price',
#     set_elec_price,
#     np.linspace(
#         set_elec_price.distribution.lower.min(),
#         set_elec_price.distribution.upper.max(),
#         10,
#     ),
#     xlfile=os.path.join(folder, 'uncertainty_across_electricity_typtax.xlsx'),
#     notify=True
# )

##Property tax, typical taxes
# parameters = list(model.get_parameters())
# parameters.remove(set_state_property_tax)
# model_without_st_prop_tax = bst.Model(lc.lipidcane_sys, 
#                                       metrics=model.metrics,
#                                       parameters=parameters,
#                                       exception_hook='raise')
# samples = model_without_st_prop_tax.sample(N_samples, rule)
# model_without_st_prop_tax.load_samples(samples)
# folder = os.path.dirname(__file__)
# dct = model_without_st_prop_tax.evaluate_across_coordinate(
#     'Property tax rate',
#     set_state_property_tax,
#     np.linspace(
#         set_state_property_tax.distribution.lower.min(),
#         set_state_property_tax.distribution.upper.max(),
#         10,
#     ),
#     xlfile=os.path.join(folder, 'uncertainty_across_proptax_typtax.xlsx'),
#     notify=True
# )

##Fuel tax
# parameters = list(model.get_parameters())
# parameters.remove(set_motor_fuel_tax)
# model_without_fuel_tax = bst.Model(lc.lipidcane_sys, 
#                                       metrics=model.metrics,
#                                       parameters=parameters,
#                                       exception_hook='raise')
# samples = model_without_fuel_tax.sample(N_samples, rule)
# model_without_fuel_tax.load_samples(samples)
# folder = os.path.dirname(__file__)
# dct = model_without_fuel_tax.evaluate_across_coordinate(
#     'Fuel tax rate',
#     set_motor_fuel_tax,
#     np.linspace(
#         set_motor_fuel_tax.distribution.lower.min(),
#         set_motor_fuel_tax.distribution.upper.max(),
#         20,
#     ),
#     xlfile=os.path.join(folder, 'uncertainty_across_fueltax.xlsx'),
#     notify=True
# )

##State income tax, typical taxes
# parameters = list(model.get_parameters())
# parameters.remove(set_state_income_tax)
# model_without_st_income_tax = bst.Model(lc.lipidcane_sys, 
#                                       metrics=model.metrics,
#                                       parameters=parameters,
#                                       exception_hook='raise')
# samples = model_without_st_income_tax.sample(N_samples, rule)
# model_without_st_income_tax.load_samples(samples)
# folder = os.path.dirname(__file__)
# dct = model_without_st_income_tax.evaluate_across_coordinate(
#     'State income tax rate',
#     set_state_income_tax,
#     np.linspace(
#         set_state_income_tax.distribution.lower.min(),
#         set_state_income_tax.distribution.upper.max(),
#         10,
#     ),
#     xlfile=os.path.join(folder, 'uncertainty_across_stincometax_typtax.xlsx'),
#     notify=True
# )

##LCCF, typical taxes
# parameters = list(model.get_parameters())
# parameters.remove(set_LCCF)
# model_without_LCCF = bst.Model(lc.lipidcane_sys, 
#                                       metrics=model.metrics,
#                                       parameters=parameters,
#                                       exception_hook='raise')
# samples = model_without_LCCF.sample(N_samples, rule)
# model_without_LCCF.load_samples(samples)
# folder = os.path.dirname(__file__)
# dct = model_without_LCCF.evaluate_across_coordinate(
#     'LCCF',
#     set_LCCF,
#     np.linspace(
#         set_LCCF.distribution.lower.min(),
#         set_LCCF.distribution.upper.max(),
#         10,
#     ),
#     xlfile=os.path.join(folder, 'uncertainty_across_LCCF_typtax.xlsx'),
#     notify=True
# )

# get_param_dct = lambda model: {p.name_with_units:p for p in model.get_parameters()}
# def filter_parameters(model, df, threshold):
#     new_df = pd.concat((df[df>=threshold], df[df<=-threshold]))
#     filtered = new_df.dropna(how='all')
#     param_dct = get_param_dct(model)
#     parameters = set(param_dct[i[1]] for i in filtered.index)
#     return parameters

# num_original_params = len(model.get_parameters())
# key_params = filter_parameters(model, sp_rho_table, 0.1)
# num_key_params = len(key_params)

# table.to_excel(r'/Users/daltonstewart/Desktop/screening_results.xlsx', sheet_name='Simulation Results', index = True)
# sp_rho_table.to_excel(r'/Users/daltonstewart/Desktop/spearmans_rho_all_params.xlsx', sheet_name='Spearmans rho', index = True)
# sp_p_table.to_excel(r'/Users/daltonstewart/Desktop/screening_results3.xlsx', sheet_name='Spearmans p', index = True)

# bst.plots.plot_montecarlo(model.table['Biorefinery']['Baseline MFSP [USD/gal]'])
# bst.plots.plot_montecarlo(model.table['Incentive 1']['MFSP Reduction [USD/gal]'])
# bst.plots.plot_montecarlo(model.table['Incentive 8']['MFSP Reduction [USD/gal]'])
# bst.plots.plot_montecarlo(model.table['Incentive 20']['MFSP Reduction [USD/gal]'])
# fig, ax = bst.plots.plot_spearman_1d(sp_rho_table['Biorefinery']['Baseline MFSP [USD/gal]'])
# labels = [item.get_text() for item in ax.get_yticklabels()]
# ax.set_yticklabels(labels)




# this plot doesnt work
# bst.plots.plot_montecarlo_across_coordinate(model.table['Power utility']['Electricity price [USD/kWh]'],(model.table['Incentive 1']['MFSP Reduction [USD/gal]'],))


# bst.plots.plot_scatter_points(model.table['Power utility']['Electricity price [USD/kWh]'], model.table['Biorefinery']['Baseline MFSP [USD/gal]'])

