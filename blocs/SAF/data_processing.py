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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Sample Data (Replace with your actual dataset)
df = pd.read_excel("Fig3b.xlsx", sheet_name="0.9")  # Ensure your data has 'state' and price columns
# Sorting values for cumulative percentage
df_sorted = df.sort_values(by=["price_di_CFR", "price_di_LCFS", "price_di_RFS"])
df_sorted["cum_percent"] = np.linspace(0, 100, len(df_sorted))
# Select only the states of interest
highlight_states = ["IL", "IA", "WI", "MI", "KY", "VA", "MS"]
df_highlight = df_sorted[df_sorted["state"].isin(highlight_states)]
fig, ax = plt.subplots(figsize=(10, 6))
# Plot the three price curves
ax.plot(df_sorted["price_di_CFR"], df_sorted["cum_percent"], color="blue", label="price_di_CFR", linewidth=2)
ax.plot(df_sorted["price_di_LCFS"], df_sorted["cum_percent"], color="green", label="price_di_LCFS", linewidth=2)
ax.plot(df_sorted["price_di_RFS"], df_sorted["cum_percent"], color="red", label="price_di_RFS", linewidth=2)
# Colors for the selected states
state_colors = {"IL": "cyan", "IA": "orange", "WI": "yellow", "MI": "purple", "KY": "green", "VA": "green", "MS": "green"}
# Highlight selected states with fill and labels
for state in highlight_states:
    state_data = df_highlight[df_highlight["state"] == state]
    if not state_data.empty:
        min_x, max_x = state_data["price_di_RFS"].min(), state_data["price_di_RFS"].max()
        min_pct, max_pct = state_data["cum_percent"].min(), state_data["cum_percent"].max()
        print(f"State: {state}")
        print(f"Price range: {min_x} to {max_x}")
        print(f"Pct range: {min_pct} to {max_pct}")
        ax.fill_betweenx(state_data["cum_percent"], min_x, max_x, color=state_colors[state], alpha=0.3)
        for _, row in state_data.iterrows():
            ax.text(row["price_di_CFR"], row["cum_percent"], state, fontsize=10, color="black", weight="bold")
ax.set_xlabel("Price Value")
ax.set_ylabel("Cumulative Percentage (%)")
ax.set_title("Accumulative Percentage Profile (Highlighted States: IL, IA, WI, MI)")
ax.legend()
plt.grid()
plt.show()






