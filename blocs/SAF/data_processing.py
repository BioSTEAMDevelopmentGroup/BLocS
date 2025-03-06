#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:32:06 2025

@author: daltonwstewart
"""

from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
from openpyxl import load_workbook

file_path = "data_processing.xlsx"  # Ensure this file exists

# Read data
df = pd.read_excel(file_path, sheet_name='raw_data')

df_filtered = []
for state, data in df.groupby('State'):
    data_cleaned = data[['miscanthus CI [kg CO2e/dry kg]', 'miscanthus cost [$/dry kg]']].dropna()
    
    if len(data_cleaned) == 0:  # Skip empty sets
        continue
    
    k = min(500, len(data_cleaned))  # Ensure k does not exceed available points
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10).fit(data_cleaned)

    # Assign labels only to non-NaN rows
    data_cleaned = data_cleaned.copy()
    data_cleaned['Cluster'] = kmeans.labels_

    # Merge cluster labels back to the original dataset
    data = data.merge(data_cleaned[['Cluster']], left_index=True, right_index=True, how='left')

    df_filtered.append(data.groupby('Cluster').first())  # Select one point per cluster

df_reduced = pd.concat(df_filtered).reset_index(drop=True)


try:
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists="replace") as writer:
        df_reduced.to_excel(writer, sheet_name="reduced_data")
except FileNotFoundError:
    print("Error: The file 'data_processing.xlsx' does not exist. Please check the file path.")
    
#%% Generate other samples
