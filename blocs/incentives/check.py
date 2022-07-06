#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 10:33:42 2022

@author: daltonstewart
"""

import biosteam as bst
from biorefineries import sugarcane as sc
from biorefineries import cornstover as cs

import blocs as blc
tea = blc.create_incentivized_tea(
    system=sc.sugarcane_sys, 
    incentive_numbers=[17], # incentives_info.xlsx
    state='Louisiana',
    isconventional=True, 
    cogeneration_unit=sc.BT,
    feedstock=sc.sugarcane, 
    ethanol_product=sc.ethanol,
    IRR=0.15,
    duration=(2018, 2038),
    depreciation='MACRS7', 
    federal_income_tax=0.21,
    operating_days=180,
    lang_factor=3,
    construction_schedule=(0.4, 0.6),
    WC_over_FCI=0.05,
    labor_cost=2.5e6,
    fringe_benefits=0.4,
    property_tax=0.001,
    property_insurance=0.005,
    supplies=0.20,
    maintenance=0.01,
    administration=0.005,
)
# tea.jobs_50=25
tea.IRR = tea.solve_IRR()

df = tea.get_cashflow_table()
(tea.FCI - 1e6*df['Depreciation [MM$]'].sum()) /1e6

print(df['Incentives [MM$]'])