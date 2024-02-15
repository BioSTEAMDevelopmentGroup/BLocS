#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 11:29:14 2024

@author: Dalton W. Stewart <dalton.w.stewart@gmail.com>

Performs site-specific TEA-LCA for a corn grain-to-ethanol biorefinery and compares the
results to those calculated according to low carbon fuel program provisions.
"""

# %%
# Import necessary packages
import biosteam as bst
from biorefineries import corn as cn
import numpy as np
from chaospy import distributions as shape
import incentives as ti
import pandas as pd
import os
from biosteam.evaluation.evaluation_tools import triang

# %%
# Define policy-specific parameters

# Biomass transport distance (analysis assumes biomass is produced in South Dakota, USA; see reference)
RFS_distance_2 = 100 # km
CFR_distance_2 = 800 # km
LCFS_distance_2 = 2500 # km

# Ethanol transport distance
distance_4 = 200 # km

# Corn grain ethanol carbon intensities
RFS_CI_reg = 74.464 # g CO2e/MJ, see
RFS_CI_LCA = 57.4 # g CO2e/MJ, see
CFR_CI_lo = 80 # g CO2e/MJ, see SI for overview of calculation
# CFR_CI_hi = 80 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI_lo = 80 # g CO2e/MJ, see SI for overview of calculation
# LCFS_CI_hi = 80 # g CO2e/MJ, see SI for overview of calculation

# Natural gas and electricity carbon intensities
NG_SD = 0.55 # kg CO2e/kWh
cons_SD = 0.61 # kg CO2e/kWh
NG_CA = 0.61 # kg CO2e/kWh
cons_CA = 0.22 # kg CO2e/kWh

# Credit values
RFS_credit_value = 2 # 2023USD/RIN
CFR_credit_value = 0
LCFS_credit_value = 0

# %%
# Set up biorefinery system
cn.load()
system = cn.corn_sys

# %% Specify characterization factors for biomass conversion stage inputs on per kilogram (kg) basis
key = 'GWP'
bst.settings.define_impact_indicator(key=key, units='kg*CO2e')
CO2_CH4 = 44/16 # Account for methane combustion

for feed in system.feeds:
    feed.set_CF(key, 0.) # assume many are negligible
cn.sulfuric_acid.set_CF(key, 1.3221/1000) # GREET 2023
cn.ammonia.set_CF(key, 0.7107) # GREET 2023
cn.yeast.set_CF(key, 2.6154) # GREET 2023
cn.lime.set_CF(key, 1.2844*0.451) # GREET 2023, 0.451 to adjust from GREET dilution to BioSTEAM
cn.gluco_amylase.set_CF(key, 5.7781) # GREET 2023
cn.alpha_amylase.set_CF(key, 1.2595) # GREET 2023
cn.denaturant.set_CF(key, 0.8636) # GREET 2023

# %%
# Define CI calculation functions for each life cycle stage

# Feedstock production (Life cycle stage 1)
def LCA_1(mass, flow, CF=209.6/1000): 
    """
    CF = site-specific crop characterization factor [kg CO2e/kg] 
    mass = biomass flow rate at biorefinery [kg/hr]
    flow = fuel product flow rate at biorefinery [kg/hr]
    """
    ethanol_HHV = 29.830 # MJ/kg
    total_emissions = CF * mass # [kg CO2e/hr] # TODO adjust for moisture content
    CI_1 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_1

# Feedstock transportation (Life cycle stage 2)
def LCA_2(mass, flow, distance, capacity=None, economy=None, factor=0.0514): # for rail factor is 0.0148
    """
    mass = biomass feedstock flow rate at biorefinery [kg/hr]
    capacity = biomass transport capacity [kg/vehicle trip]
    distance = distance between farm and biorefinery [km]
    economy = vehicle fuel economy [km/L]
    flow = fuel product flow rate at biorefinery [kg/hr]
    factor = transport emissions factor [kg CO2e/metric ton-km]
    mode = 'truck' or 'train' [dimensionless]
    """
    # gasoline_CI = 0.0013580 # kg CO2e/L
    ethanol_HHV = 29.830 # MJ/kg
    # total_trips = mass / capacity # trips/hr (one way)
    # trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    # total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    total_emissions = 2 * factor * mass * distance / 1000 # [kg CO2e/hr]
    CI_2 = total_emissions / flow / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_2

# Feedstock conversion (Life cycle stage 3)
def LCA_3(system, NG, cons):
    """
    system = BioSTEAM system object [dimensionless]
    NG = natural gas characterization factor [kg CO2e/kWh]
    cons = electricity consumption characterization factor, assumed = to regional mix factor [kg CO2e/kWh]
    """    
    ethanol_HHV = 29.830 # MJ/kg
    NG = NG / 3.6 * 55.515 # [kg CO2e/kg]
    cn.natural_gas.set_CF(key, NG+CO2_CH4)
    bst.settings.set_electricity_CF(key, cons, basis='kWh', units='kg*CO2e')
    total_emissions = system.get_net_impact(key=key) / system.get_mass_flow(cn.ethanol) # [kg CO2e/kg ethanol]  
    CI_3 = total_emissions / ethanol_HHV * 1000 # [g CO2e/MJ]
    return CI_3

# Product transportation (Life cycle stage 4)
def LCA_4(flow, capacity=None, distance=None, economy=None, factor=0.0514): 
    """
    flow = fuel product flow rate at biorefinery [kg/hr]
    capacity = fuel transport capacity [kg/vehicle trip]
    distance = distance between biorefinery and demand center [km]
    economy = vehicle fuel economy [km/L]
    mode = 'truck' or 'train' [dimensionless]
    """
    # gasoline_CI = 0.0013580 # kg CO2e/L
    ethanol_HHV = 29.830 # MJ/kg
    # total_trips = flow / capacity # trips/hr (one way)
    # trip_emissions = 2 * distance / economy * gasoline_CI # kg CO2e/round trip
    # total_emissions = total_trips * trip_emissions # [kg CO2e/hr]
    total_emissions = 2 * factor * flow * distance / 1000 # [kg CO2e/hr]
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
# Set up biorefinery model and perform analysis
tea = ti.create_corn_tea()
model = bst.Model(tea.system, exception_hook='raise')

# Model metrics
@model.metric(name='Ethanol production', units='gal/yr')
def get_ethanol_production():
    return tea.ethanol_product.F_mass / 2.98668849 * tea.operating_hours

@model.metric(name='Feedstock production CI', units='g CO2e/MJ')
def get_CI_1():
    return LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass)

@model.metric(name='Total ethanol CI (South Dakota)', units='g CO2e/MJ')
def get_total_CI_SD():
    return (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + 
            LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
            LCA_3(system, NG_SD, cons_SD) + 
            LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) + 
            LCA_5(tea.ethanol_product.F_mass)) #TODO replicate for Canada

@model.metric(name='Total ethanol CI (California)', units='g CO2e/MJ')
def get_total_CI_CA():
    return (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + 
            LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
            LCA_3(system, NG_CA, cons_CA) + 
            LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) + 
            LCA_5(tea.ethanol_product.F_mass))

@model.metric(name='RFS-induced CI differential (regulatory)', units='g CO2e/MJ')
def RFS_CI_diff_reg():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
                    LCA_3(system, NG_SD, cons_SD) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) + 
                    LCA_5(tea.ethanol_product.F_mass))
    return site_spec_CI - RFS_CI_reg

@model.metric(name='RFS-induced CI differential (LCA)', units='g CO2e/MJ')
def RFS_CI_diff_LCA():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
                    LCA_3(system, NG_SD, cons_SD) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) + 
                    LCA_5(tea.ethanol_product.F_mass))
    return site_spec_CI - RFS_CI_LCA

@model.metric(name='CFR-induced CI differential (low CI scenario)', units='g CO2e/MJ')
def CFR_CI_diff_lo():
    site_spec_CI = () #TODO finish calc
    return site_spec_CI - CFR_CI_lo

# @model.metric(name='CFR-induced CI differential (high CI scenario)', units='g CO2e/MJ')
# def CFR_CI_diff_hi():
#     site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + LCA_2() + LCA_3() + LCA_4() + LCA_5()) 
#     return site_spec_CI - CFR_CI_hi

@model.metric(name='LCFS-induced CI differential (low CI scenario)', units='g CO2e/MJ')
def LCFS_CI_diff_lo():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
                    LCA_3(system, NG_CA, cons_CA) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) + 
                    LCA_5(tea.ethanol_product.F_mass))
    return site_spec_CI - LCFS_CI_lo

# @model.metric(name='LCFS-induced CI differential (high CI scenario)', units='g CO2e/MJ')
# def LCFS_CI_diff_hi():
#     site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass) + LCA_2() + LCA_3() + LCA_4() + LCA_5()) 
#     return site_spec_CI - LCFS_CI_hi

# Model uncertain parameters
@model.parameter(name='Feedstock production CI', element=tea.feedstock,
                 units='kg CO2e/kg', distribution=shape.Triangle(118.6/1000, 209.6/1000, 407.5/1000))
def set_feedstock_CI(CI):
    tea.feedstock.characterization_factors = CI

# Perform evaluation
np.random.seed(1688)
N = 10
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N, rule)
model.load_samples(samples)
model.evaluate()
results = model.table