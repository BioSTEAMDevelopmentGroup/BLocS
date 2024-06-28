#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 12:28:04 2024

@author: Dalton W. Stewart <dalton.w.stewart@gmail.com>

Performs site-specific TEA-LCA for a miscanthus (-to-ethanol)-to-jet fuel biorefinery
and compares the results to those calculated according to low carbon fuel program provisions.
"""

# %%
# Import necessary packages
import biosteam as bst
from biorefineries import SAF as saf
import numpy as np
from chaospy import distributions as shape
import incentives as ti
import pandas as pd
import os
from biosteam.evaluation.evaluation_tools import triang

# %%
# Define important parameters
# Biomass transport distance
distance_2 = 100 # km

# Biofuel transport distance
distance_4 = 600 # km

# Miscanthus SAF carbon intensities #TODO
RFS_CI_reg = 37.232 # g CO2e/MJ, see
# RFS_CI_LCA =  # g CO2e/MJ, not available
CFR_CI = 22.003 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI = 20.19 # g CO2e/MJ, see SI for overview of calculation

# State-specific data
folder = os.path.dirname(__file__)
st_data_file = os.path.join(folder, 'state_scenarios_for_import.xlsx')
st_data = pd.read_excel(st_data_file, index_col=[0])

# States to evaluate
states = ['Alabama',
          'Arkansas',
          'Connecticut',
          'Delaware',
          'Florida',
          'Georgia',
          'Illinois',
          'Indiana',
          'Iowa',
          'Kansas',
          'Kentucky',
          'Louisiana',
          'Maine',
          'Maryland',
          'Massachusetts',
          'Michigan',
          'Minnesota',
          'Mississippi',
          'Missouri',
          'Nebraska',
          'New Hampshire',
          'New Jersey',
          'New York',
          'North Carolina',
          'North Dakota',
          'Ohio',
          'Oklahoma',
          'Pennsylvania',
          'South Carolina',
          'South Dakota',
          'Tennessee',
          'Texas',
          'Vermont',
          'Virginia',
          'West Virginia',
          'Wisconsin']

# %%
# Set up biorefinery system
# saf.load()
# system = saf.saf_sys
from biorefineries.SAF.systems_miscanthus import sys as system

# %% Specify characterization factors for biomass conversion stage inputs on per kilogram (kg) basis
GWP = 'GWP 100yr'
# bst.settings.define_impact_indicator(GWP, 'kg*CO2e')

# # Corn stover, adjusted for moisture content (x% original)
# saf.cornstover.set_CF(GWP, 0.4, basis='kg', units='kg*CO2e') # TODO: fix this CF

# # Sulfuric acid
# saf.sulfuric_acid.set_CF(GWP, 43.44/1000) # basis defaults to kg, units default to kg*CO2e # TODO: fix this CF

# # Electricity
# bst.settings.set_electricity_CF(GWP, 0.4, basis='kWh', units='kg*CO2e')

# # Ammonia
# saf.ammonia.set_CF(GWP, 2.58) # TODO: fix this CF

# # Gasoline denaturant
# saf.denaturant.set_CF(GWP, 0.84)

# %%
# Define CI calculation functions for each life cycle stage

# Feedstock production (Life cycle stage 1)
def LCA_1(mass, flow, CF): 
    """
    CF = site-specific crop characterization factor [kg CO2e/kg] 
    mass = biomass flow rate at biorefinery [kg/hr]
    flow = fuel product flow rate at biorefinery [kg/hr]
    """
    ethanol_HHV = 29.830 # MJ/kg
    total_emissions = CF * mass # [kg CO2e/hr]
    CI_1 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_1

# Feedstock transportation (Life cycle stage 2)
def LCA_2(mass, flow, distance):
    """
    mass = biomass feedstock flow rate at biorefinery [kg/hr]
    capacity = biomass transport capacity [kg/vehicle trip]
    distance = distance between farm and biorefinery [km]
    economy = vehicle fuel economy [km/L]
    flow = fuel product flow rate at biorefinery [kg/hr]
    factor = transport emissions factor [kg CO2e/metric ton-km]
    mode = 'truck' or 'train' [dimensionless]
    """
    if distance > 200:
        factor = 0.0148
        factor_2 = 0.0514
        total_emissions = 2 * ((factor_2 * mass / 0.85 * 50) + (factor * mass / 0.85 * distance)) / 1000 # [kg CO2e/hr]
    else:
        factor = 0.0514
        total_emissions = 2 * factor * mass / 0.85 * distance / 1000 # [kg CO2e/hr]
            
    # gasoline_CI = 0.0013580 # kg CO2e/L
    ethanol_HHV = 29.830 # MJ/kg
    # total_trips = mass / capacity # trips/hr (one way)
    # trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    # total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    # total_emissions = 2 * factor * mass / 0.85 * distance / 1000 # [kg CO2e/hr]
    CI_2 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_2

# Feedstock conversion (Life cycle stage 3)
def LCA_3(system, NG, cons, flow):
    """
    system = BioSTEAM system object [dimensionless]
    NG = natural gas characterization factor [kg CO2e/kWh]
    cons = electricity consumption characterization factor, assumed = to regional mix factor [kg CO2e/kWh]
    """    
    ethanol_HHV = 29.830 # MJ/kg
    # NG = NG / 3.6 * 55.515 # [kg CO2e/kg]
    key = 'GWP'
    bst.settings.define_impact_indicator(key=key, units='kg*CO2e')

    for feed in system.feeds:
        feed.set_CF(key, 0.) # assume many are negligible
    cs.sulfuric_acid.set_CF(key, 1.3221/1000) # GREET 2023
    cs.ammonia.set_CF(key, 0.7107) # GREET 2023
    cs.cellulase.set_CF(key, 2.2381*50/1000) # GREET 2023, 50/1000 to adjust from GREET dilution to BioSTEAM
    cs.CSL.set_CF(key, 1.7241) # GREET 2023
    cs.DAP.set_CF(key, 1.7411) # GREET 2023
    cs.denaturant.set_CF(key, 0.8636) # GREET 2023
    cs.caustic.set_CF(key, 2.1203) # GREET 2023
    cs.FGD_lime.set_CF(key, 1.2844*0.451) # GREET 2023, 0.451 to adjust from GREET dilution to BioSTEAM
    bst.settings.set_electricity_CF(key, NG, basis='kWh', units='kg*CO2e')
    
    total_emissions = system.get_net_impact(key=key) / system.get_mass_flow(cs.ethanol) # [kg CO2e/kg ethanol]
    CI_3 = total_emissions / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_3

# Product transportation (Life cycle stage 4)
def LCA_4(flow, distance): 
    """
    flow = fuel product flow rate at biorefinery [kg/hr]
    capacity = fuel transport capacity [kg/vehicle trip]
    distance = distance between biorefinery and demand center [km]
    economy = vehicle fuel economy [km/L]
    mode = 'truck' or 'train' [dimensionless]
    """
    if distance > 200:
        factor = 0.0148
        factor_2 = 0.0514
        total_emissions = 2 * ((factor_2 * flow * 50) + (factor * flow * distance)) / 1000 # [kg CO2e/hr]
    else:
        factor = 0.0514
        total_emissions = 2 * factor * flow * distance / 1000 # [kg CO2e/hr]
    # gasoline_CI = 0.0013580 # kg CO2e/L
    ethanol_HHV = 29.830 # MJ/kg
    # total_trips = flow / capacity # trips/hr (one way)
    # trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    # total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    # total_emissions = 2 * factor * flow * distance / 1000 # [kg CO2e/hr]
    CI_4 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_4

# Product use (Life cycle stage 5) # TODO seems like this number turns out way too high
def LCA_5(flow):
    """
    flow = fuel product flow rate at biorefinery [kg/hr]
    """
    ethanol_HHV = 29.830 # MJ/kg
    ethanol_mol = 46.068 # kg/kmol 
    CO2_mol = 44.01 # kg/kmol 
    stoich = 2 # moles of CO2 per mole of ethanol
    total_emissions = flow / ethanol_mol * stoich # kmol/hr
    CI_5 = total_emissions * CO2_mol / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_5

# %%