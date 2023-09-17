# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 21:31:20 2021

@author: Scott
"""
# %% Set up
import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.stats as stats
import os
import glob
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
# import plotly.graph_objects as go
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

plt.style.use('dark_background')

# %% Functions


def combine_results(folder):
    folder += '/'
    df = pd.DataFrame()

    for file in os.listdir(folder):
        roundResults = pd.read_csv(folder + file, sep='	')
        roundResults['Round'] = file[5:-4]
        df = df.append(roundResults)
        # df = pd.concat(df, roundResults)

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
        # gains = pd.concat(gains, pd.DataFrame(
        #     percentsArray, columns=gains.columns), ignore_index=True)

    return gains


# %% Run script
folders = glob.glob('camb*results')
outputFolder = 'cambOutputs/'

incum2011 = ['Cheung, Leland ',
             'Toomey, Jr., Timothy J. ',
             'Maher, David P. ',
             'Davis Henrietta ',
             'Simmons, E. Denise ',
             'Kelley, Craig A. ',
             'Decker, Majorie C. ',
             'vanBeuzekom, Minka Y. ',
             'Reeves, Kenneth E. ']

# incumbent = list()
incumbent = incum2011
compareResults = pd.DataFrame()
gains = pd.DataFrame()
for folder in folders:
    print(folder)
    df, elected = combine_results(folder)

    plot_single_election(df, elected, incumbent, folder)
    # gains = gains.append(round_gains(df))
    gains = pd.concat((gains, round_gains(df)))

    candidates = list(df['CANDIDATE '].loc[~(df['CANDIDATE '].str.match(
        r'Write*')) & ~(df['CANDIDATE '].str.match(
            'EXHAUSTED PILE: '))].drop_duplicates())

    incumAttempt = list(set(candidates) & set(incumbent))

    reelected = list(set(elected) & set(incumbent))
    reelectCount = len(reelected)

    lowFirstWin = df['THIS ROUND '].loc[(
        df['CANDIDATE '].isin(elected)) & (df['Round'] == 1)].min()
    highFirstLost = df['THIS ROUND '].loc[(
        ~df['CANDIDATE '].isin(elected)) & (df['Round'] == 1)].max()

    lowFirstIncWin = df['THIS ROUND '].loc[(df['CANDIDATE '].isin(elected)) & (
        df['CANDIDATE '].isin(incumbent)) & (df['Round'] == 1)].min()
    highFirstIncLoss = df['THIS ROUND '].loc[(~df['CANDIDATE '].isin(elected)) & (
        df['CANDIDATE '].isin(incumbent)) & (df['Round'] == 1)].max()

    effQuota = df['TOTAL '].loc[(df['CANDIDATE '].isin(elected)) & (
        df['Round'] == df['Round'].max())].min()
    lastOut = df['TOTAL '].loc[(~df['CANDIDATE '].isin(elected)) & (
        df['Round'] == df['Round'].max()-1)].max()

    compareResults['Incumbent'] = sorted(incumbent)
    compareResults['Elected'] = sorted(elected)
    # print(compareResults)
    print('[', len(incumAttempt), '] incumbents attempted re-election.')
    print('[', reelectCount, '] re-elected ')
    # print(sorted(reelected))

    print('Effective Quota: ', effQuota)

    print('Lowest first round elected vote: ', lowFirstWin)
    print('Highest first round defeated vote: ', highFirstLost)

    print('Lowest first round elected incumbent: ', lowFirstIncWin)
    print('Highest first round defeated incumbent: ', highFirstIncLoss)

    print('10th place votes: ', lastOut)
    print('9th-10th delta: ', effQuota - lastOut)

    print()
    incumbent = elected


# gains.plot.scatter(x='Round', y='GainAboveExpect')
# gains.plot.scatter(x='Round', y='GainAboveExpect')

# %% Election-Election Placing

print('Election to election finishing order')
placeDf = pd.DataFrame()

for folder in folders:
    files = os.listdir(folder + '/')
    finalRound = max([int(sub.split('.')[0][5:]) for sub in files])
    file = 'Round' + str(finalRound) + '.txt'
    print(file)

    roundResults = pd.read_csv(folder + '/' + file, sep='	')

    year = folder[4:8]
    roundResults['Place_' + folder[4:8]] = roundResults.index + 1

    roundResults = roundResults[roundResults['CANDIDATE '].str.contains(
        'EXHAUSTED') == False]
    roundResults = roundResults[roundResults['CANDIDATE '].str.contains(
        'Write') == False]

    roundResults.drop(
        columns=['THIS ROUND ', 'TOTAL ', 'STATUS'], inplace=True)

    roundResults.set_index('CANDIDATE ', inplace=True)

    placeDf = placeDf.merge(roundResults, how='outer',
                            left_index=True, right_index=True)


# %% Plot

x = 'Year 0'
y = 'Year +2'

yearCompare = pd.DataFrame(columns=[x, y])
for year in range(placeDf.shape[1]):
    if year < placeDf.shape[1] - 1:

        adjacentYear = placeDf.iloc[:, year:year+2]
        adjacentYear.columns = [x, y]
        yearCompare = yearCompare.append(adjacentYear, ignore_index=True)
        # yearCompare = pd.concat(yearCompare, adjacentYear, ignore_index=True)

yearCompare.dropna(inplace=True)
maxPlace = yearCompare.max().max()

# Filter to contenders
contenderMax = 15
yearContender = yearCompare[(yearCompare['Year 0'] < contenderMax) & (
    yearCompare['Year +2'] < contenderMax)]

fig, ax = plt.subplots(1, 1, figsize=(10, 10), sharex=True)

# Highlight Election Winners
winBox = [Rectangle((0, 0), 9, 9)]
ax.add_collection(PatchCollection(
    winBox, facecolor='g', alpha=0.2, edgecolor='None'))

ax.grid(which='both', alpha=0.2)
ax.minorticks_on()

# Plot finishes
ax.scatter(yearCompare[x], yearCompare[y])

# Add linear fit (of only contenders)
xs = np.arange(1, contenderMax + 1)
coefs = poly.polyfit(yearContender[x], yearContender[y], 1)
ffit = poly.polyval(xs, coefs)
ax.plot(xs, ffit)
slope, intercept, r_value, p_value, std_err = stats.linregress(
    yearContender[x], yearContender[y])
print(f'{slope=:0.2f}\n{intercept=:0.2f}\n{r_value**2=:0.3f}\n')


title = 'Finishing Place in Subsequent Cycle'
ax.set_title(title)
ax.set_xlabel('Elected Order')
ax.set_ylabel('Elected Order in Subsequent Election')
ax.set_xlim(0.5, maxPlace + 0.5)
ax.set_ylim(0.5, maxPlace + 0.5)
ax.set_aspect('equal', adjustable='box')

fig.savefig(outputFolder + title + '.png')
