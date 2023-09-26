# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:23:23 2021

https://discuss.streamlit.io/t/oserror-winerror-10013-an-attempt-was-made-to-access-a-socket-in-a-way-forbidden-by-its-access-permissions/1545
streamlit run voting2023app.py --server.port 5998

@author: Scott
"""
import streamlit as st
import pandas as pd
import numpy as np

# Pylint doesn't like text blocks for streamlit
#pylint: disable=pointless-string-statement, line-too-long


print('\n\nNew Run')
# %% Prep Things
# temp = '/tmp/'
# os.makedirs(temp, exist_ok=True)  # Make temp directory if needed

githubBase = 'https://github.com/sckilcoyne/Election_Results/blob/main/appDataFrames2023/'
githubRaw = '.pkl?raw=true'

# print(githubBase + 'candidateScore' + githubRaw)
candidatesDf = pd.read_pickle(githubBase + 'candidateScore' + githubRaw)

endorseDf = pd.read_pickle(githubBase + 'endorsements' + githubRaw)
pledgeDf = pd.read_pickle(githubBase + 'pledges' + githubRaw)
questionDf = pd.read_pickle(githubBase + 'questions' + githubRaw)

topicWeights = pd.read_pickle(githubBase + 'topicWeights' + githubRaw)

topics = endorseDf.columns.values[:-1]

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
st.set_page_config(page_title='2023 Cambridge Voting Guide',
                   page_icon=':ballot_box_with_ballot:',
                   initial_sidebar_state='expanded',
                   layout='wide')

st.title('2023 Cambridge Council Election Voting Guide')

# tabNames = ['Voting Guide',
#             'How this works',
#             'Endorsement Weights',
#             'Endorsements',
#             'Pledge Weights',
#             'Candidate Pledges',
#             'Question Weights',
#             'Candidate Answers',
#             'Fine Tune'
#             'Manual Adjustments'
#             ]
# tabVote, tabIntro, tabEndorsWeight, tabEndorse, tabPledgeWeight, tabPledge, tabQuestionWeight, tabAnswers, tabManual, tabTune = st.tabs(tabNames)
tabNames = ['Voting Guide',
            'How this works',
            'Endorsements',
            'Candidate Pledges',
            'Candidate Answers',
            'Fine Tune'
            ]
tabVote, tabIntro, tabEndorse, tabPledge, tabAnswers, tabTune = st.tabs(tabNames)

# %% Preferences
st.sidebar.title('Preferences')

st.sidebar.write('Set weights of topic preferences.')

topicWeight = pd.DataFrame()
for topic in topics:
    print(f'{topic=}  |  {topicWeights[topic]=}')
    weight = topicWeights[topic] # .astype(int).item()
    topicWeight.loc[topic, 'Weight'] = st.sidebar.slider(
        topic, min_value=0, max_value=5, value=int(weight))

st.sidebar.write('Set weights of category preferences.')

endorsementsWeight = st.sidebar.slider(
    'Endorsements', min_value=0, max_value=5, value=3)
pledgesWeight = st.sidebar.slider(
    'Pledges', min_value=0, max_value=5, value=3)
questionsWeight = st.sidebar.slider(
    'Questions', min_value=0, max_value=5, value=3)

# %% Intro
githubRepo = 'https://raw.githubusercontent.com/sckilcoyne/Election_Results/'
githubURL = githubRepo + 'main/' + 'cambOutputs/'

with tabIntro:
    '''
    ## About this app
    This is an app I created to help me figure out how to vote in the Cambridge City Council election.
    I have gathered and coded endorsements, pledges and questionnaire answers for all of the candidates in the race
    ([Google Doc](https://docs.google.com/spreadsheets/d/1NzgAYpCYGcOoGnopR5xPZA474-S41oB0cxNsIzdB9Hw/edit?usp=sharing)).
    If you think I am missing something, you can comment on the sheet.
    As this app was created to help me, the default weights reflect my personal pro-biking/housing/environment/equity views.
    You can view all of the poorly written source code on [GitHub](https://github.com/sckilcoyne/Election_Results).
    
    I first created this system to help me understand the local politics of the city and be a better informed voter.
    Going through this exercise has achieved those goals and led me to explicitly support ABC and CBS, both financially and with my time,
    primarily responding to action alerts and giving comment to the council.
    However, nothing in this guide reflects anyone's (including ABC or CBS) opinions other than mine.

    ## About the Scoring
    This whole system is basically a Pugh Matrix.
    
    On the sidebar, you can change the weights of different topics and types of data. 
    The scale is from 0-5, with 5 being more preferred and 0 ignoring that aspect.
    
    In the “Weighting” expanders, you can see and adjust the weights of each endorsement/pledge/question. 
    In the other expanders, you can see how each candidate is scored for each data point.
    
    The “Voting Guide” table lists the topic scores for each candidate and a combined score, which is a sum of the topic scores. 
    
    The topic scores are calculated for each topic and data type by multiplying the candidates’ score by 
    the weight of the data point, then summing up their scores for each data point for that sub-type, 
    e.g. all endorsements related to bikes or all answers related to housing. 
    Then, all of these scores are normalized within that subtype so the highest scoring candidate gets 
    a 1 and the lowest scoring candidate gets a 0 and everyone in between are scaled linearly. 
    This 0 to 1 score is then multiplied by the type weighting, e.g. pledge weighting. 
    Each type score is then added together and the candidate scores are normalized by the topic and 
    multiplied by the topic weighting, e.g. environment weight.
    
    The sorting of the candidates is something I am still trying to improve. 
    Right now, the first few non-incumbents are sorted above incumbents that may have a higher score because 
    I think this will be a more optimal voting strategy. I am happy to get suggestions on how to better sort.
    
    ## About the Election
    Cambridge City Council is composed of 9 seats with 2 year terms. All seats are at-large on the same ballot. 
    Cambridge uses a form of Ranked Choice Voting called Single Transferable Vote, where you list candidates in 
    order of preference and your top vote is counted until that candidate is eliminated, at which point your next 
    non-eliminated candidate is voted for. 

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
    [More Details](https://www.cambridgema.gov/Departments/electioncommission/cambridgemunicipalelections)

    ## Voting Strategy
    Reading the above RCV detail section, if you want your vote to count the most, you
    should be ranking numerous candidates, even if your top few choices are
    very likely to be elected, since you might have your ballot actually voting
    for a lower preference.

    In the elections since 2013 (last election with easily scrapable results),
    incumbency leads to a huge re-election advantage. On average, only 1 incumbent
    loses re-election per cycle (with 2 being the max). Further, we can look at how 
    results in one election correlate to results in the subsequent election. Looking 
    at finish place in one election to the next, first round vote totals from one 
    election to the next, and to finishing place in the next election, we can see
    that viable candidates generally improve upon their previous results, but 
    even incumbents are not fully safe if they were one of the last few elected. 
    This suggests the optimal voting strategy is to prioritize voting for candidates 
    near the cut off.

    For simplicity (since I haven't figured out a good way to integrate the below 
    correlations yet), there is a slight de-rating of incumbents by default. If you
    have a suggestion on a better method to take past performance into account, I'd 
    love to discuss it.

    '''

    st.markdown('![Subsequent Election Finishing Order](' + githubURL +
                'Finishing%20Place%20in%20Subsequent%20Cycle.png)')

    st.markdown('![First Round Percentage of Threshold in Subsequent Cycle](' + githubURL +
                'First%20Round%20Percentage%20of%20Threshold%20in%20Subsequent%20Cycle.png)')

    st.markdown('![Subsequent Election Finishing Order](' + githubURL +
                'First%20Round%20Percentage%20of%20Threshold%20vs.%20Finish%20in%20Subsequent%20Cycle.png)')

# %% Manual Fine Tune Adjustments
endorsers = list(endorseDf.index.values)
endorseWeight = list()

pledgeList = list(pledgeDf.index.values)
pledgeWeight = list()

questionList = list(questionDf.index.values)
questionWeight = list()

manualAdjustment = pd.DataFrame()

with tabTune:
    '''
    You can adjust indiviual endorsement, pledge, and question weights bleow.
    '''
    with st.expander('Endorsements'):
        for endorser in endorsers:
            defaultWeight = int(endorseDf.at[endorser, 'Weight'])
            limits = [i * np.sign(defaultWeight) for i in [0, 5]]
            if limits == [0, 0]:
                limits = [-3, 3]
            max_value = int(max(limits))
            min_value = int(min(limits))
            endorseWeight.append(st.slider(
                endorser, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
            widgetCount += 1

    with st.expander('Pledges'):
        for pledge in pledgeList:
            defaultWeight = int(pledgeDf.at[pledge, 'Weight'])
            limits = [i * np.sign(defaultWeight) for i in [0, 5]]
            if limits == [0, 0]:
                limits = [-3, 3]
            max_value = int(max(limits))
            min_value = int(min(limits))
            pledgeWeight.append(st.slider(
                pledge, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
            widgetCount += 1

    with st.expander('Questions'):
        for question in questionList:
            defaultWeight = int(questionDf.at[question, 'Weight'])
            limits = [i * np.sign(defaultWeight) for i in [0, 5]]
            if limits == [0, 0]:
                limits = [-3, 3]
            max_value = int(max(limits))
            min_value = int(min(limits))
            questionWeight.append(st.slider(
                question, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
            widgetCount += 1

    with st.expander('Personal Preferences'):
        for index, candidate in candidatesDf.iterrows():
            name = candidate['First'] + ' ' + candidate['Last']
            candidateAdjustment = st.slider(
                name, min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
            manualAdjustment.loc[candidate['Last'],
                                'Manual Adjustment'] = candidateAdjustment

# %% Endorsements

# with tabEndorsWeight:

#     for endorser in endorsers:
#         defaultWeight = int(endorseDf.at[endorser, 'Weight'])
#         limits = [i * np.sign(defaultWeight) for i in [0, 5]]
#         if limits == [0, 0]:
#             limits = [-3, 3]
#         max_value = int(max(limits))
#         min_value = int(min(limits))
#         endorseWeight.append(st.slider(
#             endorser, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
#         widgetCount += 1

with tabEndorse:
    cols = ['First', 'Last'] + endorsers

    endorsements = candidatesDf[cols]
    st.dataframe(endorsements, hide_index=True, height=880)

# %% Pledges

# with tabPledgeWeight:

#     for pledge in pledgeList:
#         defaultWeight = int(pledgeDf.at[pledge, 'Weight'])
#         limits = [i * np.sign(defaultWeight) for i in [0, 5]]
#         if limits == [0, 0]:
#             limits = [-3, 3]
#         max_value = int(max(limits))
#         min_value = int(min(limits))
#         pledgeWeight.append(st.slider(
#             pledge, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
#         widgetCount += 1

with tabPledge:
    cols = ['First', 'Last'] + pledgeList

    pledges = candidatesDf[cols]
    st.dataframe(pledges, hide_index=True, height=880)

# %% Questions



# with tabQuestionWeight:

#     for question in questionList:
#         defaultWeight = int(questionDf.at[question, 'Weight'])
#         limits = [i * np.sign(defaultWeight) for i in [0, 5]]
#         if limits == [0, 0]:
#             limits = [-3, 3]
#         max_value = int(max(limits))
#         min_value = int(min(limits))
#         questionWeight.append(st.slider(
#             question, min_value=min_value, max_value=max_value, step=1, value=defaultWeight, key=widgetCount))
#         widgetCount += 1

with tabAnswers:
    cols = ['First', 'Last'] + questionList

    answers = candidatesDf[cols]
    # print(answers)
    # answers.loc[:, 2:] = answers.iloc[:, 2:].fillna(0).astype(int)
    answers = answers.fillna(0)

    st.dataframe(answers, hide_index=True, height=880)

# %% Manual Adjustments

# with tabManual:
#     # st.write(candidatesDf)
#     for index, candidate in candidatesDf.iterrows():
#         name = candidate['First'] + ' ' + candidate['Last']
#         candidateAdjustment = st.slider(
#             name, min_value=-5.0, max_value=5.0, value=0.0, step=0.1)
#         manualAdjustment.loc[candidate['Last'],
#                              'Manual Adjustment'] = candidateAdjustment

# %% Voting Calculation

with tabVote:
    st.header('Voting Guide')

    endorsementsScores = candidatesDf[endorseDf.index.values] * endorseWeight
    pledgesScores = candidatesDf[pledgeDf.index.values] * pledgeWeight
    questionsScores = candidatesDf[questionDf.index.values] * questionWeight

    # Topic Scores
    scoreDf = pd.DataFrame(candidatesDf.iloc[:, :2])
    for topic in topics:
        scoreEndorse = endorsementsScores[endorseDf[endorseDf[topic] == True].index.values].sum(axis=1)
        scorePledge = pledgesScores[pledgeDf[pledgeDf[topic] == True].index.values].sum(axis=1)
        scoreAnswers = questionsScores[questionDf[questionDf[topic] == True].index.values].sum(axis=1)

        topicScore = endorsementsWeight * normalize(scoreEndorse) + \
            pledgesWeight * normalize(scorePledge) + \
            questionsWeight * normalize(scoreAnswers)

        topicScore = normalize(topicScore) * topicWeight.loc[topic, 'Weight']
        scoreDf[topic] = topicScore


    # Combined Scores
    scoreDf = scoreDf.merge(manualAdjustment, how='inner',
                            left_on='Last', right_index=True)

    # print(scoreDf)
    # print(scoreDf.sum(axis=1))
    scoreDf['Combined Score'] = scoreDf.loc[:,topics].sum(axis=1)

    scoreDf['Incumbent'] = candidatesDf['Incumbent'].fillna(0).astype(bool)

    # Sort by points
    scoreDf.sort_values(by=['Combined Score'], ascending=False, inplace=True)
    scoreDf.reset_index(drop=True, inplace=True)

    # Voting Guide
    displayCol, biasCol = st.columns([1, 1])
    displayCount = displayCol.slider('Display Candidates', min_value=5,
                                    max_value=12, step=1, value=9)
    incumbentBias = biasCol.slider('Incumbency Adjustment', value=0.9, step=0.05,
                                help='Multiply the Combined Score of Incumbents to prioritize non-incumbents for strategic voting. 1.0 is equivalent to ignoring incumbency.')

    scoreDf = scoreDf.iloc[:displayCount, :]


    # Adjusted Scoring

    adjScore = scoreDf['Combined Score'][scoreDf['Incumbent']] * incumbentBias

    scoreDf.insert(2, 'Adjusted Score',  scoreDf['Combined Score'])
    scoreDf.loc[adjScore.index, 'Adjusted Score'] = adjScore

    scoreDf.sort_values(by=['Adjusted Score'], ascending=False, inplace=True)
    scoreDf.reset_index(drop=True, inplace=True)
    scoreDf.index += 1

    cols = list(scoreDf)

    colsFront = ['First', 'Last', 'Incumbent', 'Adjusted Score', 'Combined Score']
    for col in reversed(colsFront):
        cols.insert(0, cols.pop(cols.index(col)))
    scoreDf = scoreDf.loc[:, cols]

    numCols = scoreDf.columns[3:]

    st.dataframe(scoreDf.style.format(subset=numCols, formatter="{:.2f}"), hide_index=True)

    '''
    Voting guide shows highest scoring candidates, with some bias for 
    non-incumbents. See "How this works" for detailed explaination. You should play with 
    the sliders because some of this data is pretty sparse (e.g. non-response of 
    questionaires, not all candidates wanting to get all endorsements they could get).
    The data used also misses a bunch of nuance in the candidates, which is where the 
    manual adjustments can compensate.
    '''
