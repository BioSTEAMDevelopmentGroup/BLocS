#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 12:46:50 2021

@author: daltonstewart
"""

import os
import pandas as pd
import numpy as np
import biosteam as bst
from biosteam.utils import colors
import matplotlib.pyplot as plt

folder = os.path.dirname(__file__)
fig, ax = plt.subplots()

#FOR BASELINE MFSP DATA
# bsl_data = data = pd.read_excel(os.path.join(folder, 'all_boxplot_results_typical_taxes.xlsx'),
#                                       sheet_name='all_boxplot_results_typical_tax',
#                                      index_col=0)
# bsl_MFSP_data = bsl_data['Baseline MFSP [USD/gal]']
# q5, q50, q95 = np.percentile(bsl_MFSP_data,[5,50,95],axis=0)

#FOR DATA WITH ALL TAXES INCLUDED
data = pd.read_excel(os.path.join(folder, 'all_boxplot_results.xlsx'),
                                      sheet_name='MFSP Reduction by Inc',
                                      index_col=0)

#FOR DATA WITH ONLY 'TYPICAL' TAXES INCLUDED AND 'IRRELEVANT' INCENTIVES REMOVED
# data = pd.read_excel(os.path.join(folder, 'all_boxplot_results_typical_taxes.xlsx'),
#                                       sheet_name='MFSP Reduction by Inc',
#                                      index_col=0)

exemptions_data = data[['Incentive 1','Incentive 2','Incentive 3', 'Incentive 4','Incentive 5','Incentive 6']]

deductions_data = data[['Incentive 7','Incentive 24']]

credits_data = data[['Incentive 8','Incentive 9','Incentive 10','Incentive 11',
                     'Incentive 12', 'Incentive 13', 'Incentive 14','Incentive 15',
                     'Incentive 16', 'Incentive 17', 'Incentive 18','Incentive 19','Incentive 20']]

refunds_data = data[['Incentive 21','Incentive 22','Incentive 23']]

# Plot of all incentives
bst.plots.plot_montecarlo(data,
                          positions=(1,2,3,4,6,9,10,11,12,13,14,15,16,17,18,19,20,23,24),
                          light_color=colors.yellow_tint.RGBn,
                          dark_color=colors.yellow_dark.RGBn)
plt.xlabel('Incentive')
plt.ylabel('MFSP Reduction [USD/gal]')

# Exemptions plot
bst.plots.plot_montecarlo(exemptions_data,
                          positions=(1,2,3,4,5,6),
                          light_color=colors.yellow_tint.RGBn,
                          dark_color=colors.yellow_dark.RGBn)
plt.xlabel('Incentive')
plt.ylabel('MFSP Reduction [USD/gal]')

# Deductions plot
bst.plots.plot_montecarlo(deductions_data,
                          positions=(7,24),
                          light_color=colors.yellow_tint.RGBn,
                          dark_color=colors.yellow_dark.RGBn)
plt.xlabel('Incentive')
plt.ylabel('MFSP Reduction [USD/gal]')

# Credits plot
bst.plots.plot_montecarlo(credits_data,
                          positions=(8,9,10,11,12,13,14,15,16,17,18,19,20),
                          light_color=colors.yellow_tint.RGBn,
                          dark_color=colors.yellow_dark.RGBn)
plt.xlabel('Incentive')
plt.ylabel('MFSP Reduction [USD/gal]')

# Refunds plot
bst.plots.plot_montecarlo(refunds_data,
                          positions=(21,22,23),
                          light_color=colors.yellow_tint.RGBn,
                          dark_color=colors.yellow_dark.RGBn)
plt.xlabel('Incentive')
plt.ylabel('MFSP Reduction [USD/gal]')








