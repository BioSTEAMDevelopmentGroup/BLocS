#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 10:49:59 2021

@author: daltonstewart

Analysis of the effect of various location-specific factors on lipidcane
biorefinery TEA and LCA.

"""
###Import necessary modules===================================================
import biosteam as bst
from biorefineries import lipidcane as lc
from chaospy import distributions as shape
import incentives as ti

tea = lc.create_tea(lc.lipidcane_sys,ti.IncentivesTEA)
tea.fuel_tax = 0.332
tea.sales_tax = 0.06
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.12
tea.ethanol_product = lc.ethanol
tea.biodiesel_product = lc.biodiesel
tea.ethanol_group = lc.ethanol_production_units
tea.biodiesel_group = lc.biodiesel_production_units
tea.BT = lc.BT
# tea.incentive_numbers = (1,)

###Create a model and metrics=================================================
#Set metric functions

def solve_bsl_MFSP():
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = lc.lipidcane_tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_1():
    tea.incentive_numbers = (1,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_2():
    tea.incentive_numbers = (2,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_3():
    tea.incentive_numbers = (3,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_4():
    tea.incentive_numbers = (4,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_5():
    tea.incentive_numbers = (5,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_6():
    tea.incentive_numbers = (6,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_7():
    tea.incentive_numbers = (7,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_8():
    tea.incentive_numbers = (8,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_9():
    tea.incentive_numbers = (9,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_10():
    tea.incentive_numbers = (10,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_11():
    tea.incentive_numbers = (11,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_12():
    tea.incentive_numbers = (12,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_13():
    tea.incentive_numbers = (13,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_14():
    tea.incentive_numbers = (14,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_15():
    tea.incentive_numbers = (15,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_16():
    tea.incentive_numbers = (16,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_17():
    tea.incentive_numbers = (17,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_18():
    tea.incentive_numbers = (18,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_19():
    tea.incentive_numbers = (19,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_20():
    tea.incentive_numbers = (20,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

#TODO: incentive 21 doesn't work
# def solve_MFSP_with_inc_21():
#     tea.incentive_numbers = (21,)
#     lc.ethanol.price = 0
#     for i in range(3):
#         MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
#     return MFSP

def solve_MFSP_with_inc_22():
    tea.incentive_numbers = (22,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def solve_MFSP_with_inc_23():
    tea.incentive_numbers = (23,)
    lc.ethanol.price = 0
    for i in range(3):
        MFSP = lc.ethanol.price = tea.solve_price(lc.ethanol)*2.98668849
    return MFSP

def get_incentives_amt_1():
    tea.incentive_numbers = (1,)
    ex = sum(tea.exemptions)
    de = sum(tea.deductions)
    cr = sum(tea.credits)
    re = sum(tea.refunds)
    return ex,de,cr,re
def get_incentives_amt_8():
    tea.incentive_numbers = (8,)
    ex = sum(tea.exemptions)
    de = sum(tea.deductions)
    cr = sum(tea.credits)
    re = sum(tea.refunds)
    return ex,de,cr,re


total_utility_cost = lambda: tea.utility_cost / 10**6 # In 10^6 USD/yr
net_electricity_production = lambda: abs(sum(i.power_utility.rate for i in lc.lipidcane_sys.units))\
                              *tea._operating_hours/1000 #1000 kWh/MWh 
    

#Set metrics
metrics = (bst.Metric('Baseline MFSP',solve_bsl_MFSP,'USD/gal'),
           bst.Metric('MFSP with Inc 1',solve_MFSP_with_inc_1,'USD/gal'),
           bst.Metric('MFSP with Inc 2',solve_MFSP_with_inc_2,'USD/gal'),
           bst.Metric('MFSP with Inc 3',solve_MFSP_with_inc_3,'USD/gal'),
           bst.Metric('MFSP with Inc 4',solve_MFSP_with_inc_4,'USD/gal'),
           bst.Metric('MFSP with Inc 5',solve_MFSP_with_inc_5,'USD/gal'),
           bst.Metric('MFSP with Inc 6',solve_MFSP_with_inc_6,'USD/gal'),
           bst.Metric('MFSP with Inc 7',solve_MFSP_with_inc_7,'USD/gal'),
           bst.Metric('MFSP with Inc 8',solve_MFSP_with_inc_8,'USD/gal'),
           bst.Metric('MFSP with Inc 9',solve_MFSP_with_inc_9,'USD/gal'),
           bst.Metric('MFSP with Inc 10',solve_MFSP_with_inc_10,'USD/gal'),
           bst.Metric('MFSP with Inc 11',solve_MFSP_with_inc_11,'USD/gal'),
           bst.Metric('MFSP with Inc 12',solve_MFSP_with_inc_12,'USD/gal'),
           bst.Metric('MFSP with Inc 13',solve_MFSP_with_inc_13,'USD/gal'),
           bst.Metric('MFSP with Inc 14',solve_MFSP_with_inc_14,'USD/gal'),
           bst.Metric('MFSP with Inc 15',solve_MFSP_with_inc_15,'USD/gal'),
           bst.Metric('MFSP with Inc 16',solve_MFSP_with_inc_16,'USD/gal'),
           bst.Metric('MFSP with Inc 17',solve_MFSP_with_inc_17,'USD/gal'),
           bst.Metric('MFSP with Inc 18',solve_MFSP_with_inc_18,'USD/gal'),
           bst.Metric('MFSP with Inc 19',solve_MFSP_with_inc_19,'USD/gal'),
           bst.Metric('MFSP with Inc 20',solve_MFSP_with_inc_20,'USD/gal'),
           # bst.Metric('MFSP with Inc 21',solve_MFSP_with_inc_21,'USD/gal'),
           bst.Metric('MFSP with Inc 22',solve_MFSP_with_inc_22,'USD/gal'),
           bst.Metric('MFSP with Inc 23',solve_MFSP_with_inc_23,'USD/gal'),
           bst.Metric('Incentives amount', get_incentives_amt_1, 'USD'),
           bst.Metric('Incentives amount8', get_incentives_amt_8, 'USD'),
           bst.Metric('Utility cost', total_utility_cost, '10^6 USD/yr'),
           bst.Metric('Net Electricity Production', net_electricity_production, 'MWh/yr'))
   
#Set model
model = bst.Model(lc.lipidcane_sys, metrics)

###Create parameter distributions=============================================
#Federal income tax rate, currently 35%, see effects at 30-40%
FITR_dist = shape.Triangle(0.3,0.35,0.4)

#State income tax rates, range from 0% to 12%
SITR_dist = shape.Uniform(0, 0.12)

#State property tax rates
SPTR_dist = shape.Uniform(0.0037, 0.0740)

#State motor fuel tax rates
SMFTR_dist = shape.Uniform(0.0895, 0.586)

#State utility tax rates

#State sales tax rates
SSTR_dist = shape.Uniform(0, 0.0725)

#Electricity prices, range from 0.0471 to 0.2610 USD/kWh
EP_dist = shape.Uniform(0.0471, 0.2610)

#Feedstock prices, distribution taken from Yoel's example
lipidcane = lc.lipidcane
FP_L = lipidcane.price * 0.9 #min price
FP_U = lipidcane.price * 1.1 #max price

#Feedstock oil contents

#Gasoline prices, USD/gal
GP_dist = shape.Uniform(2.103, 2.934)

#Location capital cost factors
LCCF_dist = shape.Uniform(0.82, 2.56)

#Electricty generation efficiency
EGeff_dist = shape.Triangle(0.7,0.85,0.9)

###Add Parameters=============================================================
#Federal income tax 
@model.parameter(element='TEA', kind='isolated', units='%', distribution=FITR_dist)
def set_fed_income_tax(F_tax_rate):
    tea.federal_income_tax = F_tax_rate
    
#State income tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SITR_dist)
def set_state_income_tax(S_tax_rate):
    tea.state_income_tax = S_tax_rate
    
#State property tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SPTR_dist)
def set_state_property_tax(S_P_tax_rate):
    tea.property_tax = S_P_tax_rate
    
#State motor fuel tax
@model.parameter(element='TEA', kind='isolated', units='USD/gal', distribution=SMFTR_dist)
def set_motor_fuel_tax(fuel_tax_rate):
    tea.fuel_tax = fuel_tax_rate
    
#State sales tax
@model.parameter(element='TEA', kind='isolated', units='%', distribution=SSTR_dist)
def set_sales_tax(sales_tax_rate):
    tea.sales_tax = sales_tax_rate

#Electricity price
# elec_utility = bst.PowerUtility
# @model.parameter(element=elec_utility, kind='isolated', units='USD/kWh',
#                  distribution=EP_dist)
# def set_elec_price(elec_price):
#     elec_utility.price = elec_price
    
#Feedstock price
@model.parameter(element=lipidcane, kind='isolated', units='USD/kg',
                 distribution=shape.Uniform(FP_L, FP_U))
def set_feed_price(feedstock_price):
    lipidcane.price = feedstock_price
    
#Electricity generation
# @model.parameter(element='Electricity',kind='isolated', units='%',
#                   distribution=EGeff_dist)
# def set_generation(efficiency):
#     elec_utility.rate = elec_utility.rate*efficiency

###Use these to check inputs==================================================
# #Use this to check parameters
# parameters = model.get_parameters()
# #Use this to check parameter distributions
# df_dct = model.get_distribution_summary()
# df_dct['Uniform']
# df_dct['Triangle']
# #Use this to evaluate the model
# model([0.05, 0.85, 8, 100000, 0.040]) # Returns metrics (IRR and utility cost)

###Perform Monte Carlo analysis===============================================
N_samples = 5
rule = 'L' # For Latin-Hypercube sampling
samples = model.sample(N_samples, rule)
model.load_samples(samples)
model.evaluate()
table = model.table
