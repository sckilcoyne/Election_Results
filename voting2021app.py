# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:23:23 2021

@author: Scott
"""
import streamlit as st

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

# %% Candidate Scores and Voting Guide

# %% Incumbency
