#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:56:52 2024

@author: Dalton W. Stewart <dalton.w.stewart@gmail.com>

Performs site-specific TEA-LCA for a corn stover-to-ethanol biorefinery and compares the
results to those calculated according to low carbon fuel program provisions.
"""

# %%
# Import necessary packages
import biosteam as bst
from biorefineries import cornstover as cs
import numpy as np
from chaospy import distributions as shape
import incentives as ti
import pandas as pd
import os
from biosteam.evaluation.evaluation_tools import triang

# %%
# Define policy-specific parameters

# Biomass transport distance (analysis assumes biomass is produced in South Dakota, USA; see reference)
RFS_distance = 100 # km
CFR_distance = 800 # km
LCFS_distance = 2500 # km

# Ethanol transport distance

# Corn stover ethanol carbon intensities
RFS_CI_reg = 37.232 # g CO2e/MJ, see
RFS_CI_LCA = -27.4 # g CO2e/MJ, see
CFR_CI_lo = 19.736 # g CO2e/MJ, see SI for overview of calculation
CFR_CI_hi = 19.736 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI_lo = 24.840 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI_hi = 24.840 # g CO2e/MJ, see SI for overview of calculation

# Credit values
RFS_credit_value = 0.96 # 2023USD/RIN
CFR_credit_value = 0
LCFS_credit_value = 1

# %%
# Set up biorefinery system
cs.load()
system = cs.cornstover_sys

# %% Specify characterization factors for biomass conversion stage inputs on per kilogram (kg) basis
GWP = 'GWP 100yr'
bst.settings.define_impact_indicator(GWP, 'kg*CO2e')

# Corn stover, adjusted for moisture content (x% original)
cs.cornstover.set_CF(GWP, 0.4, basis='kg', units='kg*CO2e') # TODO: fix this CF

# Sulfuric acid
cs.sulfuric_acid.set_CF(GWP, 43.44/1000) # basis defaults to kg, units default to kg*CO2e # TODO: fix this CF

# Electricity
bst.settings.set_electricity_CF(GWP, 0.4, basis='kWh', units='kg*CO2e')

# Ammonia
cs.ammonia.set_CF(GWP, 2.58) # TODO: fix this CF

# Gasoline denaturant
cs.denaturant.set_CF(GWP, 0.84)

# %%
# Define CI calculation functions for each life cycle stage

# Feedstock production (Life cycle stage 1)
def LCA_1(CF, mass, flow): 
    """
    CF = site-specific crop characterization factor [kg CO2e/kg] 
    mass = biomass flow rate at biorefinery [kg/hr]
    flow = fuel product flow rate at biorefinery [kg/hr]
    """
    ethanol_HHV = # MJ/kg
    total_emissions = CF * mass # [kg CO2e/hr] # TODO adjust for moisture content
    CI_1 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_1

# Feedstock transportation (Life cycle stage 2)
def LCA_2(mass, capacity, distance, economy, flow): 
    """
    mass = biomass feedstock flow rate at biorefinery [kg/hr]
    capacity = biomass transport capacity [kg/vehicle trip]
    distance = distance between farm and biorefinery [km]
    economy = vehicle fuel economy [km/L]
    flow = fuel product flow rate at biorefinery [kg/hr]
    mode = 'truck' or 'train' [dimensionless]
    """
    gasoline_CI = # kg CO2e/L
    ethanol_HHV = # MJ/kg
    total_trips = mass / capacity # trips/hr (one way)
    trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    CI_2 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_2

# Feedstock conversion (Life cycle stage 3)
def LCA_3(system):
    """
    system = BioSTEAM system object [dimensionless]
    """
    CO2_CH4 = 44/16 # Account for methane combustion
    for feed in system.feeds:
        feed.characterization_factors[material_cradle_to_gate_key] = 0. # assume many are negligible
        cs.natural_gas.characterization_factors[material_cradle_to_gate_key] = 0.4+CO2_CH4
        cs.FGD_lime.characterization_factors[material_cradle_to_gate_key] = 1.2844*0.451 # GREET 2023, 0.451 to adjust from GREET dilution to BioSTEAM
        cs.caustic.characterization_factors[material_cradle_to_gate_key] = 2.1203*0.5 # GREET 2023, 0.5 to adjust from GREET dilution to BioSTEAM
        cs.cellulase.characterization_factors[material_cradle_to_gate_key] = 2.2381*0.02 # GREET 2023, *0.02 to adjust from GREET dilution to BioSTEAM
        cs.DAP.characterization_factors[material_cradle_to_gate_key] = 1.7411 # GREET 2023
        cs.CSL.characterization_factors[material_cradle_to_gate_key] = 1.7241 # GREET 2023
        cs.ammonia.characterization_factors[material_cradle_to_gate_key] = 0.7107 # GREET 2023
        cs.denaturant.characterization_factors[material_cradle_to_gate_key] = 0.8636 # GREET 2023
    
    CI_3 = # TODO setup this calculation
    return CI_3

# Product transportation (Life cycle stage 4)
def LCA_4(flow, capacity, distance, economy): 
    """
    flow = fuel product flow rate at biorefinery [kg/hr]
    capacity = fuel transport capacity [kg/vehicle trip]
    distance = distance between biorefinery and demand center [km]
    economy = vehicle fuel economy [km/L]
    mode = 'truck' or 'train' [dimensionless]
    """
    gasoline_CI = # kg CO2e/L
    ethanol_HHV = # MJ/kg
    total_trips = flow / capacity # trips/hr (one way)
    trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    CI_4 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_4

# Product use (Life cycle stage 5)
def LCA_5(flow): # ethanol flow rate at biorefinery [kg/hr]
    """
    flow = fuel product flow rate at biorefinery [kg/hr]
    """
    ethanol_HHV = # MJ/kg
    CO2_mol = 44.01 # kg/kmol 
    stoich = 2 # moles of CO2 per mole of ethanol
    total_emissions = flow.mol * stoich # kmol/hr
    CI_5 = total_emissions / CO2_mol / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_5

# %%
# Set up biorefinery model and perform analysis
tea = ti.create_cornstover_tea()
model = bst.Model(tea.system, exception_hook='raise')

# Model metrics
@model.metric(name='Ethanol production', units='gal/yr')
def get_ethanol_production():
    return tea.ethanol_product.F_mass / 2.98668849 * tea.operating_hours

@model.metric(name='Feedstock production CI', units='g CO2e/MJ')
def get_CI_1():
    return LCA_1(1, tea.feedstock.F_mass) #TODO finish calc

@model.metric(name='Total ethanol CI', units='g CO2e/MJ')
def get_total_CI():
    return (LCA_1() + 
            LCA_2() + 
            LCA_3() + 
            LCA_4() + 
            LCA_5()) #TODO finish calc

@model.metric(name='RFS-induced CI differential (regulatory)', units='g CO2e/MJ')
def RFS_CI_diff_reg():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5())
    return site_spec_CI - RFS_CI_reg

@model.metric(name='RFS-induced CI differential (LCA)', units='g CO2e/MJ')
def RFS_CI_diff_LCA():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5())
    return site_spec_CI - RFS_CI_LCA

@model.metric(name='CFR-induced CI differential (low CI scenario)', units='g CO2e/MJ')
def CFR_CI_diff_lo():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5()) #TODO finish calc
    return site_spec_CI - CFR_CI_lo

@model.metric(name='CFR-induced CI differential (high CI scenario)', units='g CO2e/MJ')
def CFR_CI_diff_hi():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5()) #TODO finish calc
    return site_spec_CI - CFR_CI_hi

@model.metric(name='LCFS-induced CI differential (low CI scenario)', units='g CO2e/MJ')
def LCFS_CI_diff_lo():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5()) #TODO finish calc
    return site_spec_CI - LCFS_CI_lo

@model.metric(name='LCFS-induced CI differential (high CI scenario)', units='g CO2e/MJ')
def LCFS_CI_diff_hi():
    site_spec_CI = (LCA_1() + LCA_2() + LCA_3() + LCA_4() + LCA_5()) #TODO finish calc
    return site_spec_CI - LCFS_CI_hi

# Model uncertain parameters

# Perform evaluation
np.random.seed(1688)
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N, rule)
model.load_samples(samples)
model.evaluate()
results = model.table