# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 21:31:20 2021

@author: Scott
"""
# %% Set up
import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
# import plotly.graph_objects as go

# %% Functions


def combine_results(folder):
    folder += '/'
    df = pd.DataFrame()

    for file in os.listdir(folder):
        roundResults = pd.read_csv(folder + file, sep='	')
        roundResults['Round'] = file[5:-4]
        df = df.append(roundResults)

    df['Round'] = df['Round'].astype(int)
    df.sort_values('Round', ignore_index=True, inplace=True)

    df.replace(0, np.nan, inplace=True)
    return df


def plot_single_election(df, title):
    dfGroup = df.groupby('CANDIDATE ')
    fig, ax = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    for key, grp in dfGroup:
        ax[0].plot(grp['Round'], grp['TOTAL '], label=key)
        ax[1].plot(grp['Round'], grp['THIS ROUND '], label=key)

    ax[0].set_title('Total Votes')
    ax[1].set_title('Vote Change')
    ax[1].set_xlabel('Round')

    changeMin = min(df['THIS ROUND '].loc[(
        df['Round'] > 1) & (df['Round'] < max(df['Round']))])
    changeMax = max(df['THIS ROUND '].loc[(
        df['Round'] > 1) & (df['Round'] < max(df['Round']))])

    ax[1].set_ylim([changeMin, changeMax])

    fig.suptitle(title)


# %% Run script
folders = glob.glob('camb*results')

for folder in folders:
    df = combine_results(folder)
    plot_single_election(df, folder)
