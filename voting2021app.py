# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:23:23 2021

@author: Scott
"""
import streamlit as st
import os
import requests
import pandas as pd

# %% Prep Things
temp = '/tmp/'
os.makedirs(temp, exist_ok=True)  # Make temp directory if needed

# %% Layout
st.title('Cambridge 2021 Election Voting Guide')

# %% Preferences
st.sidebar.header('Preferences')
st.sidebar.write('Set weights of category preferences.')

bike = st.sidebar.slider('Bikes', min_value=0, max_value=5, value=5)
housing = st.sidebar.slider('Housing', min_value=0, max_value=5, value=5)
environment = st.sidebar.slider(
    'Environment', min_value=0, max_value=5, value=5)
equity = st.sidebar.slider('Social Equity', min_value=0, max_value=5, value=5)

# %% Questions

# %% Endorsements
st.header('Endorsements')

endorseGitHub = 'https://github.com/sckilcoyne/Election_Results/blob/main/endorsements.pkl?raw=true'

r = requests.get(endorseGitHub, allow_redirects=True)
tempFile = os.path.join(temp, 'endorsements.pkl')
open(tempFile, 'wb').write(r.content)
endorseDf = pd.read_pickle(endorseGitHub)

# %% Candidate Scores and Voting Guide

# %% Incumbency
