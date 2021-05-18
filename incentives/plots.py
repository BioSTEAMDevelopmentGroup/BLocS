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
import matplotlib.pyplot as plt

folder = os.path.dirname(__file__)
fig = plt.figure()

# %% Plot montecarlo of MFSP reduction across state income tax rates
# Only for incentives that are applied to state income tax; 9-15, 17-19, 23
x_vals = [*range(0,12)]
x_labels = ['State income tax rate'] + x_vals
x_ticks = [0] + x_vals
def set_x_axis(with_labels=True):
    plt.xlim(-1, 13)
    if with_labels:
        plt.xticks(x_ticks, x_labels)
    else:
        plt.xticks(x_ticks, ())
        

readxl = lambda sheet: pd.read_excel(os.path.join(folder, 'uncertainty_across_LCCF_typtax.xlsx'),
                                      sheet_name=sheet,
                                     index_col=0)

MFSP = readxl('Incentive 1 MFSP Reduction')        
x_tick_vals = np.array(MFSP.columns) #* 100 #to make percentage

# Baseline MFSP
bsl_MFSP = readxl('Biorefinery Baseline MFSP')
plt.ylabel('Non-incentivized MFSP [USD/gal]')
plt.xlabel('Location capital cost factor [unitless]')
ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, bsl_MFSP,light_color=colors.CABBI_green_soft.RGBn,dark_color=colors.CABBI_green.RGBn)[2]
plt.ylim([0,7.5])
bst.plots.plot_scatter_points(1, 2.23)

# %% GROUP 1 - PROPERTY TAX EXEMPTIONS NOT APPLIED TO SPECIFIC EQUIPMENT
# use 'uncertainty_across_prop_tax.xlsx'
# MFSP reduction with Incentive 1
# Inc1_MFSP_r = readxl('Incentive 1 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Property tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc1_MFSP_r,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# # MFSP reduction with Incentive 2
# Inc2_MFSP_r = readxl('Incentive 2 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Property tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc2_MFSP_r,light_color=colors.CABBI_blue.RGBn,dark_color=colors.CABBI_teal.RGBn)[2]

# # MFSP reduction with Incentive 6
# Inc6_MFSP_r = readxl('Incentive 6 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Property tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc6_MFSP_r,light_color=colors.red_shade.RGBn,dark_color=colors.red_dark.RGBn)[2]

# %% GROUP 2 - PROPERTY TAX EXEMPTIONS APPLIED TO SPECIFIC EQUIPMENT
# use 'uncertainty_across_prop_tax.xlsx'
# MFSP reduction with Incentive 3
# Inc3_MFSP_r = readxl('Incentive 3 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Property tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc3_MFSP_r,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# # MFSP reduction with Incentive 4
# Inc4_MFSP_r = readxl('Incentive 4 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Property tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc4_MFSP_r,light_color=colors.CABBI_blue.RGBn,dark_color=colors.CABBI_teal.RGBn)[2]

# %% GROUP 3 - STATE INCOME TAX CREDITS, PORTION OF TCI
# use 'uncertainty_across_stincometax.xlsx'
# MFSP reduction with Incentive 9
# Inc9_MFSP_r = readxl('Incentive 9 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc9_MFSP_r,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# # MFSP reduction with Incentive 10
# Inc10_MFSP_r = readxl('Incentive 10 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc10_MFSP_r,light_color=colors.CABBI_blue.RGBn,dark_color=colors.CABBI_teal.RGBn)[2]

# # MFSP reduction with Incentive 12
# Inc12_MFSP_r = readxl('Incentive 12 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc12_MFSP_r,light_color=colors.yellow_shade.RGBn,dark_color=colors.yellow_dark.RGBn)[2]

# # MFSP reduction with Incentive 15
# Inc15_MFSP_r = readxl('Incentive 15 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc15_MFSP_r,light_color=colors.CABBI_green_soft.RGBn,dark_color=colors.CABBI_teal_green.RGBn)[2]

# %% GROUP 4 STATE INCOME TAX CREDITS, VARIED PARAMETERS
# use 'uncertainty_across_stincometax.xlsx'
# MFSP reduction with Incentive 13
# Inc13_MFSP_r = readxl('Incentive 13 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc13_MFSP_r,light_color=colors.red_shade.RGBn,dark_color=colors.red_dark.RGBn)[2]

# # MFSP reduction with Incentive 17
# Inc17_MFSP_r = readxl('Incentive 17 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc17_MFSP_r,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# # MFSP reduction with Incentive 18
# Inc18_MFSP_r = readxl('Incentive 18 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc18_MFSP_r,light_color=colors.CABBI_blue.RGBn,dark_color=colors.CABBI_teal.RGBn)[2]

# # MFSP reduction with Incentive 19
# Inc19_MFSP_r = readxl('Incentive 19 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc19_MFSP_r,light_color=colors.neutral.RGBn,dark_color=colors.CABBI_black.RGBn)[2]

# %%
# MFSP reduction with Incentive 11
# Inc11_MFSP_r = readxl('Incentive 11 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc11_MFSP_r,light_color=colors.blue_shade.RGBn,dark_color=colors.blue_dark.RGBn)[2]

# # MFSP reduction with Incentive 14
# Inc14_MFSP_r = readxl('Incentive 14 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc14_MFSP_r,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]


# MFSP with Incentive 1
# Inc1_MFSP = readxl('Incentive 1 MFSP')
# plt.ylabel('MFSP [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, Inc1_MFSP,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# MFSP reduction including incentive 1
# MFSP_reduc_1 = readxl('Incentive 1 MFSP Reduction')
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('State income tax rate [%]')
# ys = bst.plots.plot_montecarlo_across_coordinate(x_tick_vals, MFSP_reduc_1,light_color=colors.yellow_tint.RGBn,dark_color=colors.yellow.RGBn)[2]

# MFSP_reduc_20 = readxl('Sheet3')
# elec_price = np.array(MFSP.columns)
# plt.ylabel('MFSP Reduction [USD/gal]')
# plt.xlabel('Electricity price [USD/kWh]')
# ys = bst.plots.plot_montecarlo_across_coordinate(elec_price, MFSP_reduc_20,light_color=colors.CABBI_green_soft.RGBn,dark_color=colors.CABBI_green.RGBn)[2]





