#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 15:14:59 2024

@author: Dalton W. Stewart <dalton.w.stewart@gmail.com>

Outputs biorefinery operations data for inputting into the Canada Clean Fuel
Regulations (CFR) data workbook.
"""

import flexsolve as flx
import biosteam as bst
from chaospy import distributions as shape
import blocs as blc
import numpy as np
import pandas as pd
import os

# Model for state specific analysis ===========================================
def create_model(biorefinery):
    biorefinery = biorefinery.lower()
    if biorefinery == 'corn':
        name = 'CN'
        tea = blc.create_corn_tea()

    elif biorefinery == 'cornstover':
        name = 'CS'
        tea = blc.create_cornstover_tea()
      
    else:
        raise ValueError("invalid biorefinery; must be either "
                         "'corn' or 'cornstover'")

    model = bst.Model(tea.system, exception_hook='raise')
    
    @model.metric(name='Biomass use', units='kg/month')
    def get_biomass_use():
        return tea.feedstock.F_mass * tea.operating_hours / 12

    @model.metric(name='Net electricity production', units='MWh/month')
    def get_electricity_production():
        return sum(i.power_utility.rate for i in tea.system.units) * tea.operating_hours / 1000 / 12
    
    @model.metric(name='Natural gas use', units='kg/month')
    def get_ng_use():
        return tea.natural_gas.F_mass * tea.operating_hours / 12

    @model.metric(name='Ethanol production', units='kg/month')
    def get_ethanol_production():
        return tea.ethanol_product.F_mass * tea.operating_hours / 12
    
    if biorefinery == 'corn':
    
        @model.metric(name='DDGS production', units='kg/month')
        def get_DDGS_production():
            return tea.DDGS.F_mass * tea.operating_hours / 12
    
        @model.metric(name='Corn oil production', units='kg/month')
        def get_oil_production():
            return tea.crude_oil.F_mass * tea.operating_hours / 12

    ### Add Parameters =============================================================
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

    if biorefinery == 'corn':

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

    elif biorefinery == 'cornstover':
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

    return model

def evaluate(biorefinery, N=10):
    model = create_model(biorefinery)
    np.random.seed(1688)
    rule = 'L' # For Latin-Hypercube sampling
    samples = model.sample(N, rule)
    model.load_samples(samples)
    model.evaluate()
    return model.table