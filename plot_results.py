# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 19:40:44 2023

@author: Scott
"""
# %% Initialize
import numpy as np
import pandas as pd
import numpy.polynomial.polynomial as poly
import scipy.stats as stats

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

plt.style.use('dark_background')

outputFolder = 'cambOutputs/'

# %% Import Data

x = 'Election'
y = 'Following_Election'

years = [2013, 2015, 2017, 2019, 2021]
summaryCols = ['Elected', 'InitialPercentage', 'Place']

results = []
allResults = pd.DataFrame()

# Import data and combine
for year in years:
    print(year)
    colsYear = [f'{col}_{year}' for col in summaryCols]
    df = pd.read_csv(f'cambOutputs/{year}_summary.csv',
                     index_col=0)
    df = df[summaryCols]
    df.columns = colsYear

    results.append(df)
    allResults = pd.concat([allResults, df], axis=1)

# Create subsetss of data that compare subsequent years
# ipHistory = pd.DataFrame()
# placeHistory = pd.DataFrame()
adjacentElection = pd.DataFrame()
maxPlace = 0
for i in range(len(years)-1):
    compareCols = [f'InitialPercentage_{years[i]}', f'InitialPercentage_{years[i+1]}',
                   f'Place_{years[i]}', f'Place_{years[i+1]}']
    adjElect = allResults[compareCols].dropna()
    adjElect.columns = [f'InitialPercentage_{x}', f'InitialPercentage_{y}',
                        f'Place_{x}', f'Place_{y}']
    adjElect.reset_index(drop=True, inplace=True)

    adjacentElection = pd.concat([adjacentElection, adjElect])

    maxPlace = max(
        maxPlace, allResults[[f'Place_{years[i]}', f'Place_{years[i+1]}']].max(axis=None))


# %% Create plots

# Filter to contenders
contenderMax = 15
adjacentContenders = adjacentElection[(adjacentElection[f'Place_{x}'] < contenderMax) & (
    adjacentElection[f'Place_{y}'] < contenderMax)]

xRegressPlace = np.arange(1, contenderMax + 1)
xRegressPercent = np.linspace(adjacentContenders[f'InitialPercentage_{x}'].min(
), adjacentContenders[f'InitialPercentage_{x}'].max(), num=10)

maxInitialPercent = max(adjacentContenders[f'InitialPercentage_{x}'].max(
), adjacentContenders[f'InitialPercentage_{y}'].max())


def plot_results(axis, xCol, yCol, regressArrange):

    axis.grid(which='both', alpha=0.2)
    axis.minorticks_on()

    # Plot finishes
    axis.scatter(adjacentElection[xCol], adjacentElection[yCol])

    # Add linear fit (of only contenders)
    xs = regressArrange
    coefs = poly.polyfit(adjacentContenders[xCol], adjacentContenders[yCol], 1)
    ffit = poly.polyval(xs, coefs)
    axis.plot(xs, ffit)
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        adjacentContenders[xCol], adjacentContenders[yCol])

    regressStr = f'{slope=:0.2f}\n{intercept=:0.2f}\n{r_value**2=:0.3f}'

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', alpha=0.5)

    # place a text box in upper left in axes coords
    axis.text(0.05, 0.95, regressStr, transform=axis.transAxes, fontsize=14,
              verticalalignment='top', bbox=props)


# Place vs Place
title1 = 'Finishing Place in Subsequent Cycle'
fig1, ax1 = plt.subplots(1, 1, figsize=(10, 10), sharex=True)

ax1.set_title(title1)
ax1.set_xlabel('Elected Order')
ax1.set_ylabel('Elected Order in Subsequent Election')

ax1.set_xlim(0.5, maxPlace + 0.5)
ax1.set_ylim(0.5, maxPlace + 0.5)
ax1.set_aspect('equal', adjustable='box')

# Highlight Election Winners
winBox = [Rectangle((0, 0), 9, 9)]
ax1.add_collection(PatchCollection(
    winBox, facecolor='g', alpha=0.2, edgecolor='None'))

plot_results(ax1, f'Place_{x}', f'Place_{y}', xRegressPlace)

# Percent vs Percent
title2 = 'First Round Percentage of Threshold in Subsequent Cycle'
fig2, ax2 = plt.subplots(1, 1, figsize=(10, 10), sharex=True)

ax2.set_title(title2)
ax2.set_xlabel('First Round Percentage of Threshold')
ax2.set_ylabel('First Round Percentage of Threshold in Subsequent Election')

ax2.set_xlim(0, maxInitialPercent * 1.1)
ax2.set_ylim(0, maxInitialPercent * 1.1)
ax2.set_aspect('equal', adjustable='box')

plot_results(ax2, f'InitialPercentage_{x}', f'InitialPercentage_{y}', xRegressPercent)

# Percent vs Place
title3 = 'First Round Percentage of Threshold vs. Finish in Subsequent Cycle'
fig3, ax3 = plt.subplots(1, 1, figsize=(10, 10), sharex=True)

ax3.set_title(title3)
ax3.set_xlabel('First Round Percentage of Threshold')
ax3.set_ylabel('Elected Order in Subsequent Election')

ax3.set_xlim(0, maxInitialPercent * 1.1)
ax3.set_ylim(0.5, maxPlace + 0.5)

plot_results(ax3, f'InitialPercentage_{x}', f'Place_{y}', xRegressPercent)

# Save Plots
fig1.savefig(outputFolder + title1 + '.png')
fig2.savefig(outputFolder + title2 + '.png')
fig3.savefig(outputFolder + title3 + '.png')
