# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:23:23 2021

@author: Scott
"""
import streamlit as st
import pandas as pd
import numpy as np


# %% Prep Things
# temp = '/tmp/'
# os.makedirs(temp, exist_ok=True)  # Make temp directory if needed

githubBase = 'https://github.com/sckilcoyne/Election_Results/blob/main/appDataFrames/'
githubRaw = '.pkl?raw=true'

candidatesDf = pd.read_pickle(githubBase + 'candidateScore' + githubRaw)

widgetCount = 0

# %% Functions


def normalize(data):
    return (data - data.min()) / (data.max() - data.min())


# %% Layout
st.set_page_config(page_title='Cambridge 2021 Voting Guide',
                   page_icon=':ballot_box_with_ballot:',
                   initial_sidebar_state='expanded',
                   layout='wide')

st.title('Cambridge 2021 Election Voting Guide')

# %% Preferences
st.sidebar.header('Preferences')

st.sidebar.write('Set weights of topic preferences.')

bikeWeight = st.sidebar.slider('Bikes', min_value=0, max_value=5, value=3)
housingWeight = st.sidebar.slider('Housing', min_value=0, max_value=5, value=3)
environmentWeight = st.sidebar.slider(
    'Environment', min_value=0, max_value=5, value=3)
equityWeight = st.sidebar.slider(
    'Social Equity', min_value=0, max_value=5, value=3)


st.sidebar.write('Set weights of category preferences.')

endorsementsWeight = st.sidebar.slider(
    'Endorsements', min_value=0, max_value=5, value=4)
pledgesWeight = st.sidebar.slider('Pledges', min_value=0, max_value=5, value=3)
questrionsWeight = st.sidebar.slider(
    'Questions', min_value=0, max_value=5, value=2)

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

endorsementsScores = candidatesDf[endorseDf.index.values] * endorseWeight
pledgesScores = candidatesDf[pledgeDf.index.values] * pledgeWeight
questionsScores = candidatesDf[questionDf.index.values] * questionWeight

bikeScore = endorsementsWeight *\
    endorsementsScores[endorseDf[endorseDf['Bikes'] == True].index.values].sum(axis=1) + \
    pledgesWeight * \
    pledgesScores[pledgeDf[pledgeDf['Bikes'] == True].index.values].sum(axis=1) + \
    questrionsWeight * \
    questionsScores[questionDf[questionDf['Bikes']
                               == True].index.values].sum(axis=1)

bikeScore = normalize(bikeScore) * bikeWeight

housingScore = (endorsementsWeight *
                endorsementsScores[endorseDf[endorseDf['Housing']
                                             == True].index.values].sum(axis=1) +
                pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Housing']
                                                       == True].index.values].sum(axis=1) +
                questrionsWeight * questionsScores[questionDf[questionDf['Housing']
                                                              == True].index.values].sum(axis=1))
housingScore = normalize(housingScore) * housingWeight

environmentScore = (endorsementsWeight *
                    endorsementsScores[endorseDf[endorseDf['Environment']
                                                 == True].index.values].sum(axis=1) +
                    pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Environment']
                                                           == True].index.values].sum(axis=1) +
                    questrionsWeight * questionsScores[questionDf[questionDf['Environment']
                                                                  == True].index.values].sum(axis=1))
environmentScore = normalize(environmentScore) * environmentWeight

equityScore = (endorsementsWeight *
               endorsementsScores[endorseDf[endorseDf['Equity']
                                            == True].index.values].sum(axis=1) +
               pledgesWeight * pledgesScores[pledgeDf[pledgeDf['Equity']
                                                      == True].index.values].sum(axis=1) +
               questrionsWeight * questionsScores[questionDf[questionDf['Equity']
                                                             == True].index.values].sum(axis=1))
equityScore = normalize(equityScore) * equityWeight

rawScore = bikeScore + housingScore + environmentScore + equityScore


scoreDf = pd.DataFrame(candidatesDf.iloc[:, :2])

scoreDf['Combined Score'] = rawScore

scoreDf['Incumbent'] = candidatesDf['Incumbent'].astype(bool)

scoreDf['Bike Score'] = bikeScore
scoreDf['Housing Score'] = housingScore
scoreDf['Environment Score'] = environmentScore
scoreDf['Equity Score'] = equityScore

# Sort by points
scoreDf.sort_values(by=['Combined Score'], ascending=False, inplace=True)

# Keep only top candidates
incumbentCount = 3
scoreDf.reset_index(drop=True, inplace=True)
incumbenmtThreshold = scoreDf.index[scoreDf['Incumbent']
                                    == True][incumbentCount]
scoreDf = scoreDf.iloc[:incumbenmtThreshold, :]

scoreDf.sort_values(by=['Incumbent'], ascending=True, inplace=True)

scoreDf.reset_index(drop=True, inplace=True)
scoreDf.index += 1

st.dataframe(scoreDf)

'''
Voting guide shows highest scoring candidates up to the third incumbent, sorted 
by non-incumbents first. See below notes for detailed explaination.
'''


# %% Incumbency
with st.expander('Voting Strategy and Incumbency Notes'):

    '''
    Cambridge elects 9 council members every two years. All candidates are in
    the same at-large race. Voting is done through a system of Ranked Choice
    Voting (RCV) where every voter can order their preferred candidates.

    Votes are first counted by every ballot's first choice. In the first round,
    if a candidate does not receive at least 50 votes, they are eliminated and
    the ballots are redistributed to the remaining candidates based on the next
    preference. Once a candidate reaches 10% of the total cast ballots + 1 vote
    (reached the threshold), they are elected to the council. If an elected
    candidate has more votes than the threshold, a random selection of ballots
    equal to the votes excess of the threshold are redistributed based on next
    eligible preference (yay Cambridge having non-deterministic elections!).
    Every round the lowest ranked candidate is eliminated and their votes are
    redistributed. This continues until 9 candidates exceed the threshold or
    there are only 9 candidates remaining.

    Reading the above paragraph, if you want your vote to count the most, you
    should be ranking numerous candidates, even if your top few choices are
    very likely to be elected, since you might have your ballot actually voting
    for a lower preference.

    In the elections since 2013 (last election with easily scrapable results),
    incumbency leads to a huge re-election advantage. On average, only 1 incumbent
    loses re-election per cycle (with 2 being the max). This suggests that the
    optimal voting strategy is to first vote for your most prefered non-incumbent.
    '''

    githubRepo = 'https://raw.githubusercontent.com/sckilcoyne/Election_Results/'
    githubURL = githubRepo + 'main/' + 'cambOutputs/'
    st.markdown('![Subsequent Election Finshing Order](' + githubURL +
                'Finishing%20Place%20in%20Subsequent%20Cycle.png)')
