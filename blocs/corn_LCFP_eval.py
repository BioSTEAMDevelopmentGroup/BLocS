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
CFR_distance_2 = 700 # km
LCFS_distance_2 = 2500 # km

# Ethanol transport distance
distance_4 = 200 # km

# Corn grain ethanol carbon intensities
RFS_CI_reg = 74.464 # g CO2e/MJ, see
RFS_CI_LCA = 57.4 # g CO2e/MJ, see
CFR_CI = 38.417 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI = 73.10 # g CO2e/MJ, see SI for overview of calculation
RFS_LUC_factor = 26.3 # g CO2e/MJ
LCFS_LUC_factor = 19.8 # g CO2e/MJ

# Natural gas and electricity carbon intensities
NG_SD = 0.55 # kg CO2e/kWh
cons_SD = 0.61 # kg CO2e/kWh
NG_CA = 0.61 # kg CO2e/kWh
cons_CA = 0.22 # kg CO2e/kWh
NG_MB = 0.025 # kg CO2e/kWh # TODO From openLCA, check this
cons_MB = 0.025 # kg CO2e/kWh # TODO From openLCA, check this

# Credit values
RFS_credit_value = 0.000649 # (0.000227-0.000958) 2023USD/g CO2e
CFR_credit_value = 0.000154 # (0.0000523-0.000304) 2023USD/g CO2e
LCFS_credit_value = 0.000154 # (0.0000523-0.000304) 2023USD/g CO2e

# %%
# Set up biorefinery system
cn.load()
system = cn.corn_sys

# %% Specify characterization factors for biomass conversion stage inputs on per kilogram (kg) basis


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
    NG = NG / 3.6 * 55.515 # [kg CO2e/kg]
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
    cn.natural_gas.set_CF(key, NG+CO2_CH4)
    bst.settings.set_electricity_CF(key, cons, basis='kWh', units='kg*CO2e')
    # CI_sulfuric_acid = cn.sulfuric_acid.F_mass * (1.3221 / 1000)
    # CI_ammonia = cn.ammonia.F_mass * 0.7107
    # CI_yeast = cn.yeast.F_mass * 2.6154
    # CI_lime = cn.lime.F_mass * (1.2844 * 0.451)
    # CI_gluco_amylase = cn.gluco_amylase.F_mass * 5.7781
    # CI_alpha_amylase = cn.alpha_amylase.F_mass * 1.2595
    # CI_denaturant = cn.denaturant.F_mass * 0.8636
    # CI_natural_gas = cn.natural_gas.F_mass * (NG + CO2_CH4)
    # CI_electricity = sum(i.power_utility.rate for i in tea.system.units) * cons
    
    total_emissions = system.get_net_impact(key=key) / system.get_mass_flow(cn.ethanol) # [kg CO2e/kg ethanol]  
    # total_emissions = CI_sulfuric_acid + CI_ammonia + CI_yeast + CI_lime + CI_gluco_amylase + CI_alpha_amylase + CI_denaturant + CI_natural_gas + CI_electricity
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
# Set up biorefinery model and perform analysis
tea = ti.create_corn_tea()
model = bst.Model(tea.system, exception_hook='raise')
tea.feedstock.set_CF('GWP', 209.6/1000) 

# Model metrics
@model.metric(name='Ethanol production', units='gal/yr')
def get_ethanol_production():
    return tea.ethanol_product.F_mass / 2.98668849 * tea.operating_hours

@model.metric(name='Feedstock production CI', units='g CO2e/MJ')
def get_CI_1():
    return LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP'])

@model.metric(name='Feedstock transportation CI (South Dakota)', units='g CO2e/MJ')
def get_CI_2_SD():
    return LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2)

@model.metric(name='Feedstock transportation CI (California)', units='g CO2e/MJ')
def get_CI_2_CA():
    return LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2)

@model.metric(name='Feedstock transportation CI (Manitoba)', units='g CO2e/MJ')
def get_CI_2_MB():
    return LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=CFR_distance_2)

@model.metric(name='Feedstock conversion CI (South Dakota)', units='g CO2e/MJ')
def get_CI_3_SD():
    return LCA_3(system, NG_SD, cons_SD, flow=tea.ethanol_product.F_mass)

@model.metric(name='Feedstock conversion CI (California)', units='g CO2e/MJ')
def get_CI_3_CA():
    return LCA_3(system, NG_CA, cons_CA, flow=tea.ethanol_product.F_mass)

@model.metric(name='Feedstock conversion CI (Manitoba)', units='g CO2e/MJ')
def get_CI_3_MB():
    return LCA_3(system, NG_MB, cons_MB, flow=tea.ethanol_product.F_mass)

@model.metric(name='Biofuel transportation CI', units='g CO2e/MJ')
def get_CI_4():
    return LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4)

@model.metric(name='Total ethanol CI (South Dakota, no LUC or combustion)', units='g CO2e/MJ')
def get_total_CI_SD():
    return (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
            LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
            LCA_3(system, NG_SD, cons_SD, flow=tea.ethanol_product.F_mass) + 
            LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))

@model.metric(name='Total ethanol CI (California, no LUC or combustion)', units='g CO2e/MJ')
def get_total_CI_CA():
    return (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
            LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
            LCA_3(system, NG_CA, cons_CA, flow=tea.ethanol_product.F_mass) + 
            LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))

@model.metric(name='Total ethanol CI (Manitoba, no LUC or combustion)', units='g CO2e/MJ')
def get_total_CI_MB():
    return (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
            LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=CFR_distance_2) + 
            LCA_3(system, NG_MB, cons_MB, flow=tea.ethanol_product.F_mass) + 
            LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))

@model.metric(name='RFS-induced CI differential (regulatory, no LUC or combustion)', units='g CO2e/MJ')
def RFS_CI_diff_reg():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
                    LCA_3(system, NG_SD, cons_SD, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))
    return site_spec_CI - RFS_CI_reg

@model.metric(name='RFS-induced CI differential (LCA, no LUC or combustion)', units='g CO2e/MJ')
def RFS_CI_diff_LCA():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
                    LCA_3(system, NG_SD, cons_SD, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))
    return site_spec_CI - RFS_CI_LCA

@model.metric(name='CFR-induced CI differential (no combustion)', units='g CO2e/MJ')
def CFR_CI_diff_lo():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=RFS_distance_2) + 
                    LCA_3(system, NG_MB, cons_MB, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))
    return site_spec_CI - CFR_CI

@model.metric(name='LCFS-induced CI differential (no LUC)', units='g CO2e/MJ')
def LCFS_CI_diff():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
                    LCA_3(system, NG_CA, cons_CA, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))
    return site_spec_CI - LCFS_CI

@model.metric(name='LCFS-induced CI differential', units='g CO2e/MJ')
def LCFS_CI_diff_LUC():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
                    LCA_3(system, NG_CA, cons_CA, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4) +
                    LCFS_LUC_factor)
    return site_spec_CI - LCFS_CI

# Model uncertain parameters
@model.parameter(name='Feedstock production CI', element=tea.feedstock,
                 units='kg CO2e/kg', distribution=shape.Triangle(118.6/1000, 209.6/1000, 407.5/1000))
def set_feedstock_CI(CI):
    tea.feedstock.set_CF('GWP', CI) 
    
feedstock = tea.feedstock
kg_per_ton = 907.185
def param(name, baseline, bounds=None, **kwargs):
    lb = 0.9 * baseline
    ub = 1.1 * baseline
    if bounds is not None:
        if lb < bounds[0]:
            lb = bounds[0]
        if ub > bounds[1]:
            ub = bounds[1]
    distribution = shape.Uniform(lb, ub)
    return model.parameter(name=name, bounds=bounds, distribution=distribution, baseline=baseline, **kwargs)

@param(name='Plant capacity', element=feedstock, kind='coupled', units='dry US MT/yr',
       baseline=(feedstock.F_mass - feedstock.imass['H2O']) * tea.operating_hours / 1000,
       description="annual feestock processing capacity")
def set_plant_size(flow_rate):
    dry_content = 1 - feedstock.imass['H2O'] / feedstock.F_mass
    feedstock.F_mass = flow_rate / tea.operating_hours / dry_content * 1000

@model.parameter(element=tea.V405, kind='coupled', units='%',
                 distribution=shape.Triangle(0.85, 0.90, 0.95))
def set_ferm_efficiency(conversion):
    tea.V405.reaction.X = conversion

# Perform evaluation
np.random.seed(1688)
N = 10
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N, rule)
model.load_samples(samples)
model.evaluate()
results = model.table