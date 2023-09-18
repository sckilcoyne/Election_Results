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


# %% Merge results from single election

def election(year):
    print(f'\n{year=}')
    folder = f'camb{year}results/'

    df = pd.DataFrame()

    for file in os.listdir(folder):
        roundResults = pd.read_csv(folder + file, sep='	', index_col=0, skiprows=1,
                                   names=['NewVotes', 'TotalVotes', 'Status'])
        # roundResults['Round'] = file[5:-4]
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

    print(dfSummary)
    dfSummary.to_csv(f'cambOutputs/{year}_summary.csv')

    return df, dfSummary

# %% Run Script
# folders = glob.glob('camb*results')


elections = [2013, 2015, 2017, 2019, 2021]

for y in elections:
    electionResults = election(y)
