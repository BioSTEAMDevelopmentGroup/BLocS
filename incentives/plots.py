#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 21:51:17 2021

@author: daltonstewart
"""
import os
import pandas as pd
import numpy as np
import biosteam as bst
from biosteam.utils import colors

folder = os.path.dirname(__file__)

# %% Plot montecarlo of lipidcane across lipid fraction
import matplotlib.pyplot as plt
x_vals = [*range(0,26)]
x_labels = ['Electricity price'] + x_vals
x_ticks = [0] + x_vals
def set_x_axis(with_labels=True):
    plt.xlim(-1, 30)
    if with_labels:
        plt.xticks(x_ticks, x_labels)
    else:
        plt.xticks(x_ticks, ())
        
# Plot metrics across lipid fraction

readxl = lambda sheet: pd.read_excel(os.path.join(folder, 'uncertainty_across_electricity.xlsx'),
                                     sheet_name="Incentive 1 MFSP", index_col=0)

fig = plt.figure()        
   
# # MFSP_ax = plt.subplot(3, 2, 1)
MFSP = readxl('Sheet1')
# elec_price = np.array(MFSP.columns)
# plt.ylabel('Baseline MFSP [USD/gal]')
# plt.xlabel('Electricity price [USD/kWh]')
# ys = bst.plots.plot_montecarlo_across_coordinate(elec_price, MFSP)[2] # p50
# # bst.plots.annotate_line('Baseline MFSP', 3, elec_price, ys,
# #               dy=6, dy_text=0.8, position='over')

MFSP_reduc_1 = readxl('Sheet2')
elec_price = np.array(MFSP.columns)
plt.ylabel('MFSP Reduction [USD/gal]')
plt.xlabel('Electricity price [USD/kWh]')
ys = bst.plots.plot_montecarlo_across_coordinate(elec_price, MFSP_reduc_1,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

MFSP_reduc_20 = readxl('Sheet3')
elec_price = np.array(MFSP.columns)
plt.ylabel('MFSP Reduction [USD/gal]')
plt.xlabel('Electricity price [USD/kWh]')
ys = bst.plots.plot_montecarlo_across_coordinate(elec_price, MFSP_reduc_20,light_color=colors.CABBI_green_soft.RGBn,dark_color=colors.CABBI_green.RGBn)[2]