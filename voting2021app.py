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
    delta = data.max() - data.min()
    if delta > 0:
        norm = (data - data.min()) / delta
    else:
        norm = data.astype(bool).astype(int) * np.sign(data.min())
    return norm


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
questionsWeight = st.sidebar.slider(
    'Questions', min_value=0, max_value=5, value=2)

# %% Intro
with st.expander('How this works'):
    '''
    ## About this app
    This is an app I created to help me figure out how to vote in the 2021 Cambridge City Council election. I have gathered and coded endorsements, pledges and questionnaire answers for all of the candidates in the race ([Google Doc](https://docs.google.com/spreadsheets/d/195MWS2K34Qgm7pJyC71Rh-lXdjmb8xoc6oKdPIvExlY/edit?usp=sharing)). If you think I am missing something, you can comment on the sheet. As this app was created to help me, the default weights reflect my personal pro-biking/housing/environment/equity views. You can view all of the poorly written source code on [GitHub](https://github.com/sckilcoyne/Election_Results).

    ## About the Election
    Cambridge City Council is composed of 9 seats with 2 year terms. All seats are at-large on the same ballot. Cambridge uses a form of Ranked Choice Voting called Single Transferable Vote, where you list candidates in order of preference and your top vote is counted until that candidate is eliminated, at which point your next non-eliminated candidate is voted for. 

    ### More Detail About Cambridge’s RCV System
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

    ## Voting Strategy
    Reading the above RCV detail section, if you want your vote to count the most, you
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
    st.markdown('![Subsequent Election Finishing Order](' + githubURL +
                'Finishing%20Place%20in%20Subsequent%20Cycle.png)')

    '''
    ## About the Scoring
    This whole system is basically a Pugh Matrix.
    
    On the sidebar, you can change the weights of different topics and types of data. The scale is from 0-5, with 5 being more preferred and 0 ignoring that aspect.
    
    In the “Weighting” expanders, you can see and adjust the weights of each endorsement/pledge/question. In the other expanders, you can see how each candidate is scored for each data point.
    
    The “Voting Guide” table lists the topic scores for each candidate and a combined score, which is a sum of the topic scores. 
    
    The topic scores are calculated for each topic and data type by multiplying the candidates’ score by the weight of the data point, then summing up their scores for each data point for that sub-type, e.g. all endorsements related to bikes or all answers related to housing. Then, all of these scores are normalized within that subtype so the highest scoring candidate gets a 1 and the lowest scoring candidate gets a 0 and everyone in between are scaled linearly. This 0 to 1 score is then multiplied by the type weighting, e.g. pledge weighting. Each type score is then added together and the candidate scores are normalized by the topic and multiplied by the topic weighting, e.g. environment weight.
    
    The sorting of the candidates is something I am still trying to improve. Right now, the first few non-incumbents are sorted above incumbents that may have a higher score because I think this will be a more optimal voting strategy. I am happy to get suggestions on how to better sort.
    '''


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

# Bike Scores
bikeScoreEndorsement = endorsementsScores[endorseDf[endorseDf['Bikes'] == True].index.values].sum(
    axis=1)
bikeScorePledge = pledgesScores[pledgeDf[pledgeDf['Bikes'] == True].index.values].sum(
    axis=1)
bikeScoreAnswers = questionsScores[questionDf[questionDf['Bikes'] == True].index.values].sum(
    axis=1)

bikeScore = endorsementsWeight * normalize(bikeScoreEndorsement) + \
    pledgesWeight * normalize(bikeScorePledge) + \
    questionsWeight * normalize(bikeScoreAnswers)

bikeScore = normalize(bikeScore) * bikeWeight

# Housing Scores
housingScoreEndorsement = endorsementsScores[endorseDf[endorseDf['Housing'] == True].index.values].sum(
    axis=1)
housingScorePledge = pledgesScores[pledgeDf[pledgeDf['Housing'] == True].index.values].sum(
    axis=1)
housingScoreAnswers = questionsScores[questionDf[questionDf['Housing'] == True].index.values].sum(
    axis=1)

housingScore = endorsementsWeight * normalize(housingScoreEndorsement) + \
    pledgesWeight * normalize(housingScorePledge) + \
    questionsWeight * normalize(housingScoreAnswers)

housingScore = normalize(housingScore) * housingWeight

# Environment Scores
environmentScoreEndorsement = endorsementsScores[endorseDf[endorseDf['Environment'] == True].index.values].sum(
    axis=1)
environmentScorePledge = pledgesScores[pledgeDf[pledgeDf['Environment'] == True].index.values].sum(
    axis=1)
environmentScoreAnswers = questionsScores[questionDf[questionDf['Environment'] == True].index.values].sum(
    axis=1)

environmentScore = endorsementsWeight * normalize(housingScoreEndorsement) + \
    pledgesWeight * normalize(housingScorePledge) + \
    questionsWeight * normalize(housingScoreAnswers)

environmentScore = normalize(environmentScore) * environmentWeight

# Equity Scores
equityScoreEndorsement = endorsementsScores[endorseDf[endorseDf['Equity'] == True].index.values].sum(
    axis=1)
equityScorePledge = pledgesScores[pledgeDf[pledgeDf['Equity'] == True].index.values].sum(
    axis=1)
equityScoreAnswers = questionsScores[questionDf[questionDf['Equity'] == True].index.values].sum(
    axis=1)

equityScore = endorsementsWeight * normalize(housingScoreEndorsement) + \
    pledgesWeight * normalize(housingScorePledge) + \
    questionsWeight * normalize(housingScoreAnswers)

equityScore = normalize(equityScore) * equityWeight

# Combined Scores
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
by non-incumbents first. See intro notes for detailed explaination.
'''
