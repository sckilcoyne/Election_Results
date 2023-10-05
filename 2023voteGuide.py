# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:47:32 2021

https://docs.google.com/spreadsheets/d/1NzgAYpCYGcOoGnopR5xPZA474-S41oB0cxNsIzdB9Hw/edit#gid=1323809669

@author: Scott
"""

import pandas as pd


# %% Functions
def download_sheet_data():
    '''Download google sheet of guide data

    Google sheet must be published to read
    https://support.google.com/docs/answer/183965?hl=en&co=GENIE.Platform%3DDesktop
    '''
    googleSheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSsrWKP18BjL-X23CsQV3h0zpa5UUXgdXBQzT8DodGNARPI0Nz38XzHmDhQFqJnFaQfjtjTRAcnJiBe/pub?output=xlsx'

    googleData = pd.read_excel(googleSheet, sheet_name='Guide Data')

    googleData.to_pickle('appDataFrames2023/guideData.pkl', protocol=3)
    print('Downloaded Google Sheet data')


def import_saved_data():
    '''Import saved downloaded guide data
    '''
    return pd.read_pickle('appDataFrames2023/guideData.pkl')


# %% Get Guide Data
download_sheet_data()
guideData = import_saved_data()

# %% Create Useable dataframes for app

# Remove CCC endorsements
print('Removing CCC from rankings')
print(f'\t{guideData.shape=}')
guideData.drop(guideData[(guideData['CCC'] == True) & (guideData['Category'].isna())].index,
               axis=0,
               inplace=True)

guideData.drop(['CCC'], axis=1, inplace=True)

print(f'\t{guideData.shape=}')

# Make Table of Candidate endorsements/answers
candidateScore = guideData[guideData['Category'].isna()].drop(
    ['Category', 'Topic Weight'], axis=1)
candidateScore.iloc[:, 2:] = candidateScore.iloc[:, 2:].fillna(0).astype(int)
candidateScore.sort_values(by=['Last'], ascending=True, inplace=True)
candidateScore.reset_index(drop=True, inplace=True)

# Table of data points and thier weights
data = guideData[guideData['Category'].notna()].drop(
    ['First', 'Last', 'Incumbent', 'Topic Weight'], axis=1).set_index('Category').transpose()

# Sub-tables of data points by type of data
questions = data[data['Type'] == 'Question'].drop('Type', axis=1)
endorsements = data[data['Type'] == 'Endorsement'].drop('Type', axis=1)
pledges = data[data['Type'] == 'Pledge'].drop('Type', axis=1)

questions['Weight'] = questions['Weight'].astype(int)
endorsements['Weight'] = endorsements['Weight'].astype(int)
pledges['Weight'] = pledges['Weight'].astype(int)

# Create default Topic weights Table
topicWeights = guideData[guideData['Category'].notna()].drop(
    ['First', 'Last', 'Incumbent'], axis=1).set_index('Category').drop(
        ['Weight', 'Type', 'Notes'], axis=0)['Topic Weight']

# %% Save Data to be used in app
pickleFolder = 'appDataFrames2023/'

candidateScore.to_pickle(pickleFolder + 'candidateScore.pkl', protocol=3)
questions.to_pickle(pickleFolder + 'questions.pkl', protocol=3)
endorsements.to_pickle(pickleFolder + 'endorsements.pkl', protocol=3)
pledges.to_pickle(pickleFolder + 'pledges.pkl', protocol=3)
topicWeights.to_pickle(pickleFolder + 'topicWeights.pkl', protocol=3)
