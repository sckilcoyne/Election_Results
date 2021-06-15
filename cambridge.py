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
from matplotlib.lines import Line2D
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

    elected = list(df['CANDIDATE '].loc[df['STATUS'].str.match(
        r' ELECTED*')].drop_duplicates())
    return df, elected


def plot_single_election(df, elected, incumbent, title):
    dfGroup = df.groupby('CANDIDATE ')
    fig, ax = plt.subplots(2, 1, figsize=(18, 10), sharex=True)

    electLine = 'solid'
    defeatLine = 'dashed'
    exhaustLine = 'dotted'
    incumbentColor = 'C0'
    challengeColor = 'C1'
    exhaustColor = 'gray'

    for key, grp in dfGroup:
        if key in elected:
            linestyle = electLine
        elif key == 'EXHAUSTED PILE: ':
            linestyle = exhaustLine
        else:
            linestyle = defeatLine

        if key in incumbent:
            color = incumbentColor
        elif key == 'EXHAUSTED PILE: ':
            color = exhaustColor
        else:
            color = challengeColor

        ax[0].plot(grp['Round'], grp['TOTAL '],
                   label=key, linestyle=linestyle, color=color)

        grp2 = grp.loc[grp['Round'] > 1]
        ax[1].plot(grp2['Round'], grp2['THIS ROUND '],
                   label=key, linestyle=linestyle, color=color)

    ax[0].set_title('Total Votes')
    ax[1].set_title('Added Votes')
    ax[1].set_xlabel('Round')

    # changeMin = min(df['THIS ROUND '].loc[(
    #     df['Round'] > 1) & (df['Round'] < max(df['Round']))])
    changeMin = 0
    # changeMax = max(df['THIS ROUND '].loc[(
    #     df['Round'] > 1) & (df['Round'] < max(df['Round']))])
    changeMax = max(df['THIS ROUND '].loc[(
        df['Round'] > 1) & (df['CANDIDATE '] != 'EXHAUSTED PILE: ')]) * 1.1

    ax[1].set_ylim([changeMin, changeMax])
    # ax[1].set_ylim(bottom=0)
    xMax = max(df['Round'])
    ax[1].set_xlim([1, xMax])
    ax[1].xaxis.set_ticks(np.arange(1, xMax + 1, 1))

    custom_lines = [Line2D([0], [0], color=incumbentColor, linestyle=electLine, lw=3),
                    Line2D([0], [0], color=challengeColor,
                           linestyle=electLine, lw=3),
                    Line2D([0], [0], color=incumbentColor,
                           linestyle=defeatLine, lw=3),
                    Line2D([0], [0], color=challengeColor,
                           linestyle=defeatLine, lw=3),
                    Line2D([0], [0], color=exhaustColor, linestyle=exhaustLine, lw=3)]

    custom_legend = ['Relected Incumbent',
                     'Elected Challenger',
                     'Defeated Incumbent',
                     'Defeated Challenger',
                     'Exhausted Ballots'],
    ax[1].legend(custom_lines, *custom_legend, loc='upper left')

    fig.suptitle(title, size='x-large', weight='bold')
    fig.tight_layout()

    fig.savefig(outputFolder + title + '.png')


def round_gains(df):
    continuing = df.loc[df['STATUS'] == ' CONTINUING']
    contineGroup = continuing.groupby(['Round'])

    gains = pd.DataFrame(columns=['Round', 'GainAboveExpect'])

    for key, grp in contineGroup:
        voteTotal = grp['THIS ROUND '].sum()
        count = grp['THIS ROUND '].count()
        percents = list((1/count) - (grp['THIS ROUND '] / voteTotal))
        percentsArray = np.array([[key]*len(percents), percents]).transpose()

        gains = gains.append(pd.DataFrame(
            percentsArray, columns=gains.columns), ignore_index=True)

    return gains


# %% Run script
folders = glob.glob('camb*results')
outputFolder = 'cambOutputs/'

incumbent = list()
gains = pd.DataFrame()
for folder in folders:
    df, elected = combine_results(folder)
    plot_single_election(df, elected, incumbent, folder)
    gains = gains.append(round_gains(df))

    # print(set(elected) & set(incumbent))
    incumbent = elected

# gains.plot.scatter(x='Round', y='GainAboveExpect')
