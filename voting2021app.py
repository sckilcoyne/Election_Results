# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:23:23 2021

@author: Scott
"""
import streamlit as st
# import os
# import requests
import pandas as pd
import numpy as np
from sklearn import preprocessing
import pickle
import urllib.request

# %% Prep Things
# temp = '/tmp/'
# os.makedirs(temp, exist_ok=True)  # Make temp directory if needed

githubBase = 'https://github.com/sckilcoyne/Election_Results/blob/main/appDataFrames/'
githubRaw = '.pkl?raw=true'

candidatesDf = pd.read_pickle(githubBase + 'candidateScore' + githubRaw)

widgetCount = 0

# %% Layout
st.title('Cambridge 2021 Election Voting Guide')

# %% Preferences
st.sidebar.header('Preferences')

st.sidebar.write('Set weights of topic preferences.')

bikeWeight = st.sidebar.slider('Bikes', min_value=0, max_value=5, value=5)
housingWeight = st.sidebar.slider('Housing', min_value=0, max_value=5, value=5)
environmentWeight = st.sidebar.slider(
    'Environment', min_value=0, max_value=5, value=5)
equityWeight = st.sidebar.slider(
    'Social Equity', min_value=0, max_value=5, value=5)


st.sidebar.write('Set weights of category preferences.')

endorsementsWeight = st.sidebar.slider(
    'Endorsements', min_value=0, max_value=5, value=5)
pledgesWeight = st.sidebar.slider('Pledges', min_value=0, max_value=5, value=5)
questrionsWeight = st.sidebar.slider(
    'Questions', min_value=0, max_value=5, value=5)

# %% Endorsements

endorseDf = pd.read_pickle(githubBase + 'endorsements' + githubRaw)

endorsers = list(endorseDf.index.values)
endorseWeight = list()

with st.expander('Endorsement Weighting'):

    for endorser in endorsers:
        defaultWeight = int(endorseDf.at[endorser, 'Weight'])
        limits = [i * np.sign(defaultWeight) for i in [0, 5]]
        max_value = int(max(limits))
        min_value = int(min(limits))
        endorseWeight.append(st.slider(
            endorser, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
        widgetCount += 1

with st.expander('Endorsements'):
    cols = ['First', 'Last'] + endorsers

    endorsements = candidatesDf[cols]
    st.dataframe(endorsements)

# %% Pledges
pledgeDf = pd.read_pickle(githubBase + 'pledges' + githubRaw)

pledgeList = list(pledgeDf.index.values)
pledgeWeight = list()

with st.expander('Pledge Weighting'):

    for pledge in pledgeList:
        defaultWeight = int(pledgeDf.at[pledge, 'Weight'])
        limits = [i * np.sign(defaultWeight) for i in [0, 5]]
        max_value = int(max(limits))
        min_value = int(min(limits))
        pledgeWeight.append(st.slider(
            pledge, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
        widgetCount += 1

with st.expander('Candidate Pledges'):
    cols = ['First', 'Last'] + pledgeList

    pledges = candidatesDf[cols]
    st.dataframe(pledges)

# %% Questions
questionDf = pd.read_pickle(githubBase + 'questions' + githubRaw)

questionList = list(questionDf.index.values)
questionWeight = list()

with st.expander('Question Weighting'):

    for question in questionList:
        defaultWeight = int(questionDf.at[question, 'Weight'])
        limits = [i * np.sign(defaultWeight) for i in [0, 5]]
        max_value = int(max(limits))
        min_value = int(min(limits))
        questionWeight.append(st.slider(
            question, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
        widgetCount += 1

with st.expander('Candidate Answers'):
    cols = ['First', 'Last'] + questionList

    answers = candidatesDf[cols]
    answers.iloc[:, 2:] = answers.iloc[:, 2:].fillna(0).astype(int)
    st.dataframe(answers)

# %% Voting Calculation

st.header('Voting Guide')

scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))

endorsementsScores = candidatesDf[endorseDf.index.values] * endorseWeight
pledgesScores = candidatesDf[pledgeDf.index.values] * pledgeWeight
questionsScores = candidatesDf[questionDf.index.values] * questionWeight

bikeScore = bikeWeight * (endorsementsWeight *
                          endorsementsScores[endorseDf[endorseDf['Bikes']
                                                       == True].index.values].sum(axis=1) +
                          pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Bikes']
                                                                 == True].index.values].sum(axis=1) +
                          questrionsWeight * questionsScores[questionDf[questionDf['Bikes']
                                                                        == True].index.values].sum(axis=1))

housingScore = housingWeight * (endorsementsWeight *
                                endorsementsScores[endorseDf[endorseDf['Housing']
                                                             == True].index.values].sum(axis=1) +
                                pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Housing']
                                                                       == True].index.values].sum(axis=1) +
                                questrionsWeight * questionsScores[questionDf[questionDf['Housing']
                                                                              == True].index.values].sum(axis=1))

environmentScore = environmentWeight * (endorsementsWeight *
                                        endorsementsScores[endorseDf[endorseDf['Environment']
                                                                     == True].index.values].sum(axis=1) +
                                        pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Environment']
                                                                               == True].index.values].sum(axis=1) +
                                        questrionsWeight * questionsScores[questionDf[questionDf['Environment']
                                                                                      == True].index.values].sum(axis=1))

equityScore = equityWeight * (endorsementsWeight *
                              endorsementsScores[endorseDf[endorseDf['Equity']
                                                           == True].index.values].sum(axis=1) +
                              pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Equity']
                                                                     == True].index.values].sum(axis=1) +
                              questrionsWeight * questionsScores[questionDf[questionDf['Equity']
                                                                            == True].index.values].sum(axis=1))

rawScore = bikeScore + housingScore + environmentScore + equityScore


scoreDf = pd.DataFrame(candidatesDf.iloc[:, :2])

scoreDf['Combined Score'] = rawScore
scoreDf['Bike Score'] = bikeScore
scoreDf['Housing Score'] = housingScore
scoreDf['Environment Score'] = environmentScore
scoreDf['Equity Score'] = equityScore


scoreDf.sort_values(by=['Combined Score'], ascending=False, inplace=True)
scoreDf.reset_index(drop=True, inplace=True)
scoreDf.index += 1

st.write(scoreDf)


# %% Incumbency
with st.expander('Incumbency Notes'):
    st.write('under construction')
