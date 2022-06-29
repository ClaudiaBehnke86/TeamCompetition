'''
Create a mixed team compeition 
'''

import json
import requests
import datetime as dt
#from requests.auth import HTTPBasicAuth
import pandas as pd 
from pandas import json_normalize
import plotly.express as px
import streamlit as st 
import plotly.graph_objects as go
#import pycountry_convert as pc

import plotly.graph_objs as pg
import numpy as np
import os
import random


def calc_overlap(teama, teamb):

    in_first = set(teama)
    in_second = set(teamb)

    in_second_but_not_in_first = in_second - in_first

    result = teama + list(in_second_but_not_in_first)

    return result

# teams
teams = ['GER', 'FRA', 'NED', 'USA', 'UAE', 'ISR', 'THA', 'COL']

GER = ["1492", "14511", "1447", "1448", "1456", "1457", "1481"]
FRA = ["14511", "1447", "1453", "1456", "1457", "1475", "1483"]
NED = ["14511", "1447", "1448", "1456", "1456", "1457"]
THA = ["1492", "1453", "1455", "1456", "1481", "1484"]
USA = ["1475", "1476", "1477", "1483", "1484"]
ISR = ["1475", "1476", "1477", "1483", "1484"]
UAE = ["1475", "1476", "1477", "1484"]
COL = ["14511", "1453", "1477", "1483"]

team_dict = {
    'GER' : GER,
    'FRA' : FRA,
    'NED' : NED,
    'THA' : THA,
    'USA' : USA,
    'ISR' : ISR,
    'UAE' : UAE,
    'COL' : COL
}

key_map = {
    #"1491": "Adults Duo Men",
    "1492": "Adults Duo Mixed",
    #"1490": "Adults Duo Women",
    #"1444": "Adults Fighting Men -56 kg",
    "14511": "Adults Fighting Men -62 kg & -69 kg",
    #"1451": "Adults Fighting Men -62 kg",
    #"1446": "Adults Fighting Men -69 kg",
    "1447": "Adults Fighting Men -77 kg",
    "1448": "Adults Fighting Men -85 kg",
    #"1449": "Adults Fighting Men -94 kg",
    #"1450": "Adults Fighting Men +94 kg",
    #"1452": "Adults Fighting Women -45 kg",
    "1453": "Adults Fighting Women -48 kg",
    #"1454": "Adults Fighting Women -52 kg",
    "1455": "Adults Fighting Women -57 kg",
    "1456": "Adults Fighting Women -63 kg",
    "1457": "Adults Fighting Women -70 kg",
    #"1458": "Adults Fighting Women +70 kg",
    #"1473": "Adults Jiu-Jitsu Men -56 kg",
    #"1474": "Adults Jiu-Jitsu Men -62 kg",
    "1475": "Adults Jiu-Jitsu Men -69 kg",
    "1476": "Adults Jiu-Jitsu Men -77 kg",
    "1477": "Adults Jiu-Jitsu Men -85 kg",
    #"1478": "Adults Jiu-Jitsu Men -94 kg",
    #"1479": "Adults Jiu-Jitsu Men +94 kg",
    #"1480": "Adults Jiu-Jitsu Women -45 kg",
    "1481": "Adults Jiu-Jitsu Women -48 kg",
    #"1482": "Adults Jiu-Jitsu Women -52 kg",
    "1483": "Adults Jiu-Jitsu Women -57 kg",
    "1484": "Adults Jiu-Jitsu Women -63 kg",
    #"1485": "Adults Jiu-Jitsu Women -70 kg",
    #"1486": "Adults Jiu-Jitsu Women +70 kg",
    #"1494": "Adults Show Men",
    #"1495": "Adults Show Mixed",
    #"1493": "Adults Show Women"
    }


# Main programm starts here

st.title('Team Competition TWG22') 
teamA_name = st.sidebar.selectbox('Team A', teams)
teamA = team_dict[teamA_name]

#teams_new = teams.remove(str(teamA))
teamB_name = st.sidebar.selectbox('Team B', teams)
teamB = team_dict[teamB_name]
col1, col2 = st.columns(2)

result = calc_overlap(teamA, teamB)

name_list = [key_map.get(item,item) for item in result]

teamA_choice1 = st.sidebar.selectbox('Team A Choice 1', name_list)
teamB_choice1 = st.sidebar.selectbox('Team B Choice 1', name_list)
teamA_choice2 = st.sidebar.selectbox('Team A Choice 2', name_list)
teamB_choice2 = st.sidebar.selectbox('Team B Choice 2', name_list)

good_teamA = len(teamA)/len(result)
good_teamB = len(teamB)/len(result)

#Data Set
teams_sel = [teamB_name, teamA_name]
 
values = [good_teamB, good_teamA]

fig1 = go.Figure(go.Bar(
            x=[good_teamA, good_teamB],
            y=[teamA_name, teamB_name],
            marker_color=['red', 'blue'],
            orientation='h'))


fig1.update_xaxes(title_text='Chances for good category', range=(0, 1.0))
fig1.update_yaxes(title_text='Teams')
st.plotly_chart(fig1)

with col1:
    st.header(teamA_name)
    for i in teamA:
        st.write(key_map[i]) 

with col2:
    st.header(teamB_name)
    for i in teamB:
        st.write(key_map[i]) 

with st.expander("Shared categories"):
    for i in result:
        st.write(key_map[i]) 


if st.button('Random Category'):
    randcat = random.choice(result)
    st.write(key_map[randcat])

    with col1:
        if (randcat in teamA):
            st.success(str(key_map[randcat]) + ' is in ' + teamA_name)
        else:
            st.error(str(key_map[randcat]) + ' is NOT in ' + teamA_name)
    with col2:
        if (randcat in teamB):
            st.success(str(key_map[randcat]) + ' is in ' + teamB_name)
        else:
            st.error(str(key_map[randcat]) + ' is NOT in ' + teamB_name)
