# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:47:32 2021

@author: Scott
"""

import pandas as pd


# %% Functions
def download_sheet_data():
    googleSheet = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSouvpbGc1D3Q2KhTEAsqHH-LhnSs52N-TbOc351_WRt1Bb8OzmHAUWemlufR_NXbUGve5JNIjUbpcA/pub?output=xlsx'

    guideData = pd.read_excel(googleSheet, sheet_name='Guide Data')

    guideData.to_pickle('appDataFrames/guideData.pkl', protocol=3)


def import_saved_data():
    return pd.read_pickle('appDataFrames/guideData.pkl')


# %% Get Guide Data
download_sheet_data()
guideData = import_saved_data()

# %% Create Useable dataframes for app

# Make Table of Candidate endorsements/answers
candidateScore = guideData[guideData['Category'].isna()].drop(
    ['Category', 'Topic Weight'], axis=1)
candidateScore.iloc[:, 3:] = candidateScore.iloc[:, 3:].fillna(0).astype(int)
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
        ['Weight', 'Type'], axis=0)['Topic Weight']

# %% Save Data to be used in app
pickleFolder = 'appDataFrames/'

candidateScore.to_pickle(pickleFolder + 'candidateScore.pkl', protocol=3)
questions.to_pickle(pickleFolder + 'questions.pkl', protocol=3)
endorsements.to_pickle(pickleFolder + 'endorsements.pkl', protocol=3)
pledges.to_pickle(pickleFolder + 'pledges.pkl', protocol=3)
topicWeights.to_pickle(pickleFolder + 'topicWeights.pkl', protocol=3)
