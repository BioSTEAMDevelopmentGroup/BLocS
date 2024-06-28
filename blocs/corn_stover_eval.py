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
RFS_distance_2 = 100 # km
CFR_distance_2 = 700 # km
LCFS_distance_2 = 2500 # km

# Ethanol transport distance
distance_4 = 200 # km

# Corn stover ethanol carbon intensities
RFS_CI_reg = 37.232 # g CO2e/MJ, see
RFS_CI_LCA = -27.4 # g CO2e/MJ, see
CFR_CI = 22.003 # g CO2e/MJ, see SI for overview of calculation
LCFS_CI = 20.19 # g CO2e/MJ, see SI for overview of calculation

# Natural gas and electricity carbon intensities
NG_SD = 0.55 # kg CO2e/kWh
cons_SD = 0.61 # kg CO2e/kWh
NG_CA = 0.61 # kg CO2e/kWh
cons_CA = 0.22 # kg CO2e/kWh
NG_MB = 0.025 # kg CO2e/kWh # TODO From openLCA, check this
cons_MB = 0.025 # kg CO2e/kWh # TODO From openLCA, check this

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
# Set up biorefinery model and perform analysis
tea = ti.create_cornstover_tea()
model = bst.Model(tea.system, exception_hook='raise')
tea.feedstock.set_CF('GWP', 43.7589/1000)

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
def LCFS_CI_diff_lo():
    site_spec_CI = (LCA_1(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, CF=tea.feedstock.characterization_factors['GWP']) + 
                    LCA_2(mass=tea.feedstock.F_mass, flow=tea.ethanol_product.F_mass, distance=LCFS_distance_2) + 
                    LCA_3(system, NG_CA, cons_CA, flow=tea.ethanol_product.F_mass) + 
                    LCA_4(flow=tea.ethanol_product.F_mass, distance=distance_4))
    return site_spec_CI - LCFS_CI

# Model uncertain parameters
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

@model.parameter(name='Feedstock production CI', element=tea.feedstock,
                 units='kg CO2e/kg', distribution=shape.Triangle(0.5*(43.7589/1000), 43.7589/1000, 1.5*(43.7589/1000)))
def set_feedstock_CI(CI):
    tea.feedstock.set_CF('GWP', CI)
    
cornstover = feedstock
pretreatment_conversions = tea.R201.reactions.X
cofermentation_conversions = tea.R303.cofermentation.X
saccharification_conversions = tea.R303.saccharification.X

@param(name='Plant capacity', element=cornstover, kind='coupled', units='dry US ton/yr',
       baseline=(cornstover.F_mass - cornstover.imass['H2O']) * tea.operating_hours / kg_per_ton,
       description="annual feestock processing capacity")
def set_plant_size(flow_rate):
    dry_content = 1 - cornstover.imass['H2O'] / cornstover.F_mass
    cornstover.F_mass = flow_rate / tea.operating_hours / dry_content * kg_per_ton

@param(name='PT glucan-to-glucose', element=tea.R201, kind='coupled', units='% theoretical',
       description='extent of reaction, glucan + water -> glucose, in pretreatment reactor',
       baseline=pretreatment_conversions[0] * 100,
       bounds=(0, 100))
def set_PT_glucan_to_glucose(X):
    X /= 100.
    pretreatment_conversions[0] = X
    corxns = pretreatment_conversions[1:3]
    corxns[:] = 0.003
    if pretreatment_conversions[:3].sum() > 1.:
        f = corxns / corxns.sum()
        corxns[:] = f * (1. - X) * 0.9999999

@param(name='PT xylan-to-xylose', element=tea.R201, kind='coupled', units='% theoretical',
       description='extent of reaction, xylan + water -> xylose, in pretreatment reactor',
       baseline=pretreatment_conversions[8] * 100,
       bounds=(0, 100))
def set_PT_xylan_to_xylose(X):
    X /= 100.
    pretreatment_conversions[8] = X
    corxns = pretreatment_conversions[9:11]
    corxns[:] = [0.024, 0.05]
    if pretreatment_conversions[8:11].sum() > 1.:
        f = corxns / corxns.sum()
        corxns[:] = f * (1. - X) * 0.9999999

@param(name='PT xylan-to-furfural', element=tea.R201, kind='coupled', units='% theoretical',
       description='extent of reaction, xylan -> furfural + 2 water, in pretreatment reactor',
       baseline=pretreatment_conversions[10] * 100,
       bounds=(0, 100))
def set_PT_xylan_to_furfural(X):
    # To make sure the overall xylan conversion doesn't exceed 100%
    lb = 1. - pretreatment_conversions[8] - pretreatment_conversions[9]
    pretreatment_conversions[10] = min(lb, X / 100.) * 0.9999999

@param(name='EH cellulose-to-glucose', element=tea.R303, kind='coupled', units='% theoretical',
       description='extent of reaction, gluan + water -> glulose, in enzyme hydrolysis',
       baseline=saccharification_conversions[2] * 100,
       bounds=(0, 100))
def set_EH_glucan_to_glucose(X):
    X /= 100.
    saccharification_conversions[2] = X
    corxns = saccharification_conversions[:2]
    corxns[:] = [0.04, 0.0012]
    if saccharification_conversions[:3].sum() > 1.:
        f = corxns / corxns.sum()
        corxns[:] = f * (1. - X) * 0.9999999

@param(name='FERM glucose-to-ethanol', element=tea.R303, kind='coupled', units='% theoretical',
       description='extent of reaction, glucose -> 2 ethanol + 2 CO2, in enzyme hydrolysis',
       baseline=cofermentation_conversions[0] * 100,
       bounds=(0, 100))
def set_FERM_glucose_to_ethanol(X):
    X /= 100.
    cofermentation_conversions[0] = X
    corxns = cofermentation_conversions[1:4]
    corxns[:] = [0.02, 0.0004, 0.006]
    if cofermentation_conversions[:4].sum() > 1.:
        f = corxns / corxns.sum()
        corxns[:] = f * (1. - X) * 0.9999999

@param(name='Boiler efficiency', element=tea.BT, kind='coupled', units='%',
       description='efficiency of burning fuel to produce steam',
       baseline=tea.BT.boiler_efficiency * 100,
       bounds=(0, 100))
def set_boiler_efficiency(X):
    tea.BT.boiler_efficiency = X / 100.

@param(name='Turbogenerator efficiency', element=tea.BT, kind='coupled', units='%',
       description='efficiency of converting steam to power',
       baseline=tea.BT.turbogenerator_efficiency * 100,
       bounds=(0, 100))
def set_turbogenerator_efficiency(X):
    tea.BT.turbogenerator_efficiency = X / 100.

# Perform evaluation
np.random.seed(1688)
N = 10
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N, rule)
model.load_samples(samples)
model.evaluate()
results = model.table