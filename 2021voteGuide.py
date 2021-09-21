# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 22:47:32 2021

@author: Scott
"""

import pandas as pd

endorsements = {
    'Cambridge Bike Safety':
        {'Bikes': True,
         'Housing': False,
         'Environment': True,
         'Equity': False,
         'Weight': 5},
    'DSA':
        {'Bikes': False,
         'Housing': False,
         'Environment': False,
         'Equity': True,
         'Weight': 2},
    'A Better Cambridge':
        {'Bikes': False,
         'Housing': True,
         'Environment': False,
         'Equity': False,
         'Weight': 3},


}


if __name__ == '__main__':
    endorseDf = pd.DataFrame.from_dict(endorsements).transpose()
    endorseDf['Bikes'].fillna(False, inplace=True)
    endorseDf['Housing'].fillna(False, inplace=True)
    endorseDf['Environment'].fillna(False, inplace=True)
    endorseDf['Equity'].fillna(False, inplace=True)

    endorseDf.to_pickle('endorsements.pkl')
