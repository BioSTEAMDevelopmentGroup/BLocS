#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Dalton W. Stewart <dalton.w.stewart@gmail.com>

This file performs life cycle assessment (LCA) of a corn stover biorefinery as 
part of an end-to-end LCA of the overall corn stover ethanol supply chain. The
corn stover carbon intensity was calculated based on an additional LCA integrating
the results of
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
# Define LCA function
def LCA(biorefinery,
        feedstock_CF=None,
        elec_cons_CF=0.36, # https://greet.es.anl.gov/
        elec_prod_CF=0.36, # https://greet.es.anl.gov/
        allocation=None):
   
# Set keys to call material characterization factors (CFs)
    material_cradle_to_gate_key = ('GWP100', 'cradle_to_gate') 
    consumption_key = ('GWP100', 'cradle_to_gate') 
    production_key = ('GWP100', 'cradle_to_gate') 
    
    # Use to adjust methane CF to account for combustion
    CO2_CH4 = 44/16    
           
# Set biorefinery system,then set material flows and characterization factors
    sys = cs.cornstover_sys
    for feed in sys.feeds:
        feed.characterization_factors[material_cradle_to_gate_key] = 0. #assume many are negligible
        feedstock = cs.cornstover
        product = cs.ethanol
        cs.natural_gas.characterization_factors[material_cradle_to_gate_key] = 0.4+CO2_CH4
        cs.FGD_lime.characterization_factors[material_cradle_to_gate_key] = 1.28*0.451 #GREET, *0.451 to adjust from GREET dilution to ours
        cs.caustic.characterization_factors[material_cradle_to_gate_key] = 2.01*0.5 #GREET, *0.5 to adjust from GREET dilution to ours
        cs.cellulase.characterization_factors[material_cradle_to_gate_key] = 8.07*0.02 #GREET, *0.02 to adjust from GREET dilution to ours
        cs.DAP.characterization_factors[material_cradle_to_gate_key] = 1.66 #GREET
        cs.CSL.characterization_factors[material_cradle_to_gate_key] = 1.56 #GREET
        cs.ammonia.characterization_factors[material_cradle_to_gate_key] = 2.58 #GREET
        cs.denaturant.characterization_factors[material_cradle_to_gate_key] = 0.88 #GREET
        chems = cs._chemicals
        if feedstock_CF == None:
            feedstock.characterization_factors[material_cradle_to_gate_key] = 45.67/1000 #GREET #TODO: adjust for moisture content
        else:
            feedstock.characterization_factors[material_cradle_to_gate_key] = feedstock_CF
        
    # Electricity CFs, consumption assumed = to regional mix factor, production assumed = to regional natural gas factor
    bst.PowerUtility.characterization_factors[consumption_key] = elec_cons_CF 
    bst.PowerUtility.characterization_factors[production_key] = elec_prod_CF 
        
# Determine GWP from material flows and GWP from onsite direct emissions of CO2 
    GWP_material = sum([s.get_impact(material_cradle_to_gate_key) if s.ID !='steam' else s.characterization_factors[material_cradle_to_gate_key]*s.H for s in sys.feeds])
        
# Determine net electricity and associated GWP
    net_electricity = bst.PowerUtility.sum([i.power_utility for i in sys.units])
    GWP_electricity_production = net_electricity.get_impact('production')
         
# Determine total GWP
# For net electricity consumers, includes GWP due to electricity
# For net electricity producers, produced electricity is ignored for now  
    if net_electricity.rate > 0:
        GWP_total = GWP_material + GWP_electricity_production #+ GWP_direct_emissions # kg CO2 eq. / hr
    else:
        GWP_total = GWP_material #+ GWP_direct_emissions # kg CO2 eq. / hr
      
# Determine total GWP according to offset allocation method, used by USEPA Renewable Fuel Standard
# For net electricity producers, impact of produced electricity 'offsets' impacts of ethanol production
    GWP_offset = GWP_material + GWP_electricity_production #+ GWP_direct_emissions # kg CO2 eq. / hr

# Determine total GWP according to energy allocation method, used by EU Renewable Energy Directive
# Impacts are distributed to products (ethanol) and coproducts (electricity) according to energy content
   
    # First determine energy fractions of ethanol, and electricity products
    # higher heating value array for chemicals in J/mol, this is like the CF array, but note that it is per mol, not per kg
    HHVs = np.array([i.HHV for i in chems]) 
    # for ethanol
    mol_ethanol = product.mol # in kmol/hr
    e_ethanol = (HHVs * mol_ethanol).sum() # kmol/hr * J/mol, you have kJ/hr
    
    # for electricity, using net_electricity parameter calculated above
    # convert to kJ/hr
    e_electricity = net_electricity.rate * 3600 # 1 kW = 3600 kJ/hr
    # determine energy ratios
    e_array = np.array((e_ethanol, e_electricity))
    e_array /= e_array.sum() # ethanol | electricity

    ethanol_Efrac = e_array[0]
    elec_Efrac = e_array[1]

    GWP_eng = GWP_total * ethanol_Efrac
           
# Return final GWP values according to argument specifying allocation method
# Allocation cannot be performed for only one product
    if allocation == 'displacement':
        if net_electricity.rate > 0:
            raise RuntimeError("Allocation cannot be performed for only one product.")
        else:
            GWP_ethanol = GWP_offset / product.F_mass * 2.98668849 # kg CO2 eq. / gal ethanol
    elif allocation == 'energy':
        if net_electricity.rate > 0:
            raise RuntimeError("Allocation cannot be performed for only one product.")
        else:
            GWP_ethanol = GWP_eng / product.F_mass * 2.98668849 # kg CO2 eq. / gal ethanol
    elif allocation == None:
        GWP_ethanol = GWP_total / product.F_mass * 2.98668849 # kg CO2 eq. / gal ethanol
    else: raise ValueError("invalid allocation method; must be either"
                           "'displacement' or 'energy'")
        
    return GWP_ethanol

# %%

def create_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        tea = ti.create_corn_tea()
    elif biorefinery == 'cornstover':
        tea = ti.create_cornstover_tea()
    elif biorefinery == 'sugarcane':
        tea = ti.create_sugarcane_tea()
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn', 'cornstover', or 'sugarcane'")
    
    model = bst.Model(tea.system, exception_hook='raise')
    
    ## Define model metrics
    # Net electricity production
    @model.metric(name='Net electricity production', units='MWh/yr')
    def get_electricity_production():
        return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours/1000
    
    # Ethanol production
    @model.metric(name='Ethanol production', units='gal/yr')
    def get_ethanol_production():
        return tea.ethanol_product.F_mass * 2.98668849 * tea.operating_hours
    
    # Ethanol GWP according to displacement allocation
    @model.metric(name='Displacement GWP', units='kg CO2e/kg ethanol')
    def GWP_getter():
        feedstock_CF = 0.06 # TODO: fix this CF
        elec_cons_CF = 0.66 # from BLocS state specific data file for Illinois
        elec_prod_CF = 0.56 # from BLocS state specific data file for Illinois
        return LCA(biorefinery,feedstock_CF,elec_cons_CF=elec_cons_CF,elec_prod_CF=elec_prod_CF,allocation='displacement')
    
    ## Define model parameters subject to uncertainty
    # Plant capacity
    @model.parameter(element=tea.feedstock, kind='isolated', units='kg/hr',
                      distribution=triang(tea.feedstock.F_mass))
    def set_plant_capacity(plant_capacity):
        tea.feedstock.F_mass = plant_capacity
        
    # Electricty generation efficiency distribution
    EGeff_dist = shape.Triangle(0.7,0.85,0.9)
    TBGeff_dist = shape.Triangle(0.7,0.85,0.9)
    
    if tea.BT:
        # Boiler efficiency
        @model.parameter(name='boiler efficiency', element=tea.BT, units='%', distribution=EGeff_dist)
        def set_boiler_efficiency(boiler_efficiency):
            tea.BT.boiler_efficiency = boiler_efficiency    
        
        # Turbogenerator efficiency
        @model.parameter(name='turbogenerator efficiency', element=tea.BT, units='%', distribution=TBGeff_dist)
        def set_turbogenerator_efficiency(turbo_generator_efficiency):
            tea.BT.turbogenerator_efficiency = turbo_generator_efficiency

    return model

def evaluate(biorefinery, N=10):
    model = create_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table
    