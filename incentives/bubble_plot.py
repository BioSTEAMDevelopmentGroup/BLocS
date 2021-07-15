#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:05:14 2021

@author: daltonstewart
"""

#Import necessary modules.
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

#Import data and an 2 empty tables/matrices for use later.
folder = os.path.dirname(__file__)

file = os.path.join(folder, 'bubl_plot_data.xlsx')
data = pd.read_excel(file, index_col=[0])
data = abs(data)
data['size'] *= 500

plt.scatter('x',
            'y',
            s = 'size',
            alpha = 0.5,
            data=data)

plt.xticks(ticks=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24],
           labels=['BSL','1','2','3','4','5','6','7','8','9','10','11','12',
                   '13','14','15','16','17','18','19','20','21','22','23'])

plt.yticks(ticks=[1,2,3,4,5,6,7,8,9,10,11,12,13],
           labels=['Boiler efficiency',
                 'Operating days',
                 'Turbogenerator efficiency',
                 'Plant capacity',
                 'Sales tax rate',
                 'WW system base cost',
                 'Cellulase price',
                 'Fed income tax rate',
                 'State income tax rate',
                 'Feedstock price',
                 'Fuel tax rate',
                 'Property tax rate',
                 'LCCF'])

plt.grid(which='major',axis='both')