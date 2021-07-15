#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 14:38:07 2021

@author: daltonstewart
"""

#Import modules
import biosteam as bst
from biorefineries import cornstover as cs
from chaospy import distributions as shape
from biosteam.evaluation.evaluation_tools import triang
import incentives as ti
import numpy as np
import pandas as pd
import os
import seaborn as sb
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# LCCF_range = np.linspace(2.56, 0.82, 100)
# ep_range = np.linspace(0.0471, 0.2610, 100)
# st_inc_tax_range = np.linspace(0,0.12,100)
# fuel_tax_range = np.linspace(0,0.1,100)
prop_tax_range = np.linspace(0.0037,0.0740,100)
# sales_tax_range = np.linspace(0,0.0725,100)
fs_price_range = np.linspace(0.02,0.111,100)

# output = pd.DataFrame(np.zeros(shape=(100,100)), columns=ep_range, index=LCCF_range)

tea = ti.create_cornstover_tea()

TEA_st_inc_taxes = []
TEA_fs_prices = []
MESPs = []

tea.fuel_tax = 0.
tea.sales_tax = 0.06
tea.federal_income_tax = 0.35
tea.state_income_tax = 0.065
tea.property_tax = 0.013
tea.utility_tax = 0.
tea.incentive_numbers = (5,)
bst.PowerUtility.price = 0.0685

data = pd.DataFrame(np.zeros(shape=(100,100)),columns=prop_tax_range,index=fs_price_range)

#my setup, outputs 100x100 matrix
for i in prop_tax_range:
    tea.property_tax = i
    # TEA_st_inc_taxes.append(i)
    for j in fs_price_range:
        tea.feedstock.price = j
        # TEA_fs_prices.append(j)       
        for m in range(3):
            MESP = tea.solve_price(tea.ethanol_product)
            MESP *= 2.98668849
        data.loc[j][i] = MESP
        # MESPs.append(MESP)
        
#Yalin's setup, outputs 10000x3 matrix
# for i in sales_tax_range:
#     tea.sales_tax = i
#     TEA_st_inc_taxes.append(i)
#     for j in fs_price_range:
#         tea.feedstock.price = j
#         TEA_fs_prices.append(j)
#         for m in range(3):
#             MESP = tea.solve_price(tea.ethanol_product)
#             MESP *= 2.98668849
#         # data.loc[j][i] = MESP
#         MESPs.append(MESP)
      
#activate this to output a plot  
# plot = go.Figure(data = 
#                  go.Contour(
#                      z=data,
#                      x=data.columns,
#                      y=data.index))

# plot.update_layout(xaxis_title='Sales tax rate (decimal)',
#                    yaxis_title='Feedstock price (USD/kg)')

# plot.show(renderer='png')

# TEA_st_inc_taxes = sum([[i]*len(fs_price_range) for i in TEA_st_inc_taxes], [])       
# _data = pd.DataFrame({
#     'State income tax rate [decimal]': TEA_st_inc_taxes,
#     'Feedstock price [USD/kg]': TEA_fs_prices,
#     'MESP [USD/gal]': MESPs
#     })




# with pd.ExcelWriter('prop_tax_fs_price_inc_5_heatmap_data.xlsx') as writer:
#     data.to_excel(writer, sheet_name='data')
        
