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

    guideData.to_pickle('appDataFrames/guideData.pkl')


def import_saved_data():
    return pd.read_pickle('appDataFrames/guideData.pkl')


# %% Get Guide Data
# download_sheet_data()
guideData = import_saved_data()

# %% Create Useable dataframes for app
candidateScore = guideData[guideData['Category'].isna()].drop(
    'Category', axis=1)

data = guideData[guideData['Category'].notna()].drop(
    ['First', 'Last', 'Incumbent'], axis=1).set_index('Category').transpose()

questions = data[data['Type'] == 'Question']
endorsements = data[data['Type'] == 'Endorsement']
pledges = data[data['Type'] == 'Pledge']

# %% Save Data to be used in app

candidateScore.to_pickle('appDataFrames/candidateScore.pkl')
questions.to_pickle('appDataFrames/questions.pkl')
endorsements.to_pickle('appDataFrames/endorsements.pkl')
pledges.to_pickle('appDataFrames/pledges.pkl')
