# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 22:08:52 2023

@author: Scott
"""
# %% Initialize
import os
import glob
import pandas as pd
import numpy as np

# Candidates with different names in different years {old: new}
cleanNames = {'Musgrave, Adriane B. ': 'Musgrave, Adriane ',
              'Levy, Ilan S. ': 'Levy, Ilan ',
              }

# %% Merge results from single election


def election(year):
    print(f'\n{year=}')
    folder = f'camb{year}results/'

    df = pd.DataFrame()

    for file in os.listdir(folder):
        roundResults = pd.read_csv(folder + file, sep='	', index_col=0, skiprows=1,
                                   names=['NewVotes', 'TotalVotes', 'Status'])

        roundResults.rename(index=cleanNames, inplace=True)

        roundResults.columns = pd.MultiIndex.from_product([[int(file[5:-4])], roundResults])

        df = pd.concat([df, roundResults], axis=1)

        df = df.reindex(sorted(df.columns), axis=1)

    df.to_csv(f'cambOutputs/{year}_counts.csv')

    lastRound = df.columns.get_level_values(0).max()
    voteThreashold = df.loc[:, (lastRound, 'TotalVotes')][0]
    print(f'{voteThreashold=}')

    dfSummary = pd.DataFrame()
    dfSummary['InitialVotes'] = df.loc[:, (1, 'TotalVotes')]

    dfSummary['finalResults'] = df.loc[:, lastRound]['Status']
    dfSummary['Elected'] = dfSummary['finalResults'].str.contains('ELECTED')

    dfSummary = dfSummary[dfSummary.index.str.contains(',')]

    dfSummary['InitialPercentage'] = dfSummary['InitialVotes'] / voteThreashold

    dfSummary['ElectedRound'] = dfSummary[dfSummary['finalResults'].str.contains(
        'ELECTED')]['finalResults'].str[12:-8]
    dfSummary['DefeatedRound'] = dfSummary[dfSummary['finalResults'].str.contains(
        'DEFEATED')]['finalResults'].str[12:-8]

    dfSummary['ElectedRound'] = pd.to_numeric(dfSummary['ElectedRound'])
    dfSummary['DefeatedRound'] = pd.to_numeric(dfSummary['DefeatedRound'])

    electedCount = 0
    for r, rows in dfSummary.groupby('ElectedRound'):
        count = rows.shape[0]

        if count == 1:
            dfSummary.loc[rows.index, 'Place'] = electedCount + count
        else:
            dfSummary.loc[rows.index, 'Place'] = ((electedCount * 2) + 1 + count) / 2

        electedCount = electedCount + count

    for r, rows in dfSummary.groupby('DefeatedRound', sort=False):
        count = rows.shape[0]

        if count == 1:
            dfSummary.loc[rows.index, 'Place'] = electedCount + count
        else:
            dfSummary.loc[rows.index, 'Place'] = ((electedCount * 2) + 1 + count) / 2

        electedCount = electedCount + count

    # print(dfSummary)
    dfSummary.to_csv(f'cambOutputs/{year}_summary.csv')

    return df, dfSummary

# %% Run Script
# folders = glob.glob('camb*results')


elections = [2013, 2015, 2017, 2019, 2021]

for y in elections:
    electionResults = election(y)
