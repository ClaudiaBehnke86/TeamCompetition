'''

Create a mixed team compeition for TWG 2022 that allows the teams
to choose their categories and one random category is selected

'''
import random
import streamlit as st
import plotly.graph_objects as go

import requests
import json
from requests.auth import HTTPBasicAuth
import pandas as pd 
from pandas import json_normalize


def getdata(eventid, user, password):
    """
    get the athletes form sportdata
    """

    uri = 'https://www.sportdata.org/ju-jitsu/rest/event/members/'+str(eventid)+'/'

    response = requests.get(uri, auth=HTTPBasicAuth(user, password),)
    d = response.json()

    df_out = json_normalize(d)
    st.write(df_out)
    df = df_out[['id', 'first', 'last', 'sex', 'country_code', 'categories']]


    return df


def calc_overlap(teama, teamb):
    '''
    Function to calc the overlap categories between the teams
    '''
    in_first = set(teama)
    in_second = set(teamb)

    in_second_but_not_in_first = in_second - in_first

    result_out = teama + list(in_second_but_not_in_first)

    return result_out

def intersection(teama, teamb):
    '''
    Function to calc the intersection categories between the teams
    '''

    result_out_overlapp = [value for value in teama if value in teamb]

    return result_out_overlapp


#def sidebar():
#    ''' make the sidebar
#    '''


# some variables
teams = ['GER', 'FRA', 'NED', 'USA', 'UAE', 'ISR', 'THA', 'COL', 'MEX']

GER = ["1492", "14511", "14471", "14561", "14811"]
FRA = ["14511", "14471", "14531", "14561", "14761", "14811"]
NED = ["14511", "14471", "14531", "14561"]
THA = ["1492", "14531", "14531", "14561", "14811", "1484"]
USA = ["14761", "1477", "14811", "1484"]
ISR = ["14761", "1477", "14811", "1484"]
UAE = ["14761", "1477", "14811", "1484"]
COL = ["14511", "14531", "1477", "14811"]
MEX = ["14511", "14471", "1448", "1461"]

# map variables to strings
team_dict = {
    'GER': GER,
    'FRA': FRA,
    'NED': NED,
    'THA': THA,
    'USA': USA,
    'ISR': ISR,
    'UAE': UAE,
    'COL': COL,
    'MEX': MEX
}

# using the kers from sportsdata (might become handy at some point)
key_map = {
    # "1491": "Adults Duo Men",
    "1492": "Adults Duo Mixed",
    # "1490": "Adults Duo Women",
    # "1444": "Adults Fighting Men -56 kg",
    "14511": "Adults Fighting Men -62 kg & -69 kg",
    # "1451": "Adults Fighting Men -62 kg",
    # "1446": "Adults Fighting Men -69 kg",
    #"1447": "Adults Fighting Men -77 kg",
    #"1448": "Adults Fighting Men -85 kg",
    "14471": "Adults Fighting Men -77 kg & -85kg",
    # "1449": "Adults Fighting Men -94 kg",
    # "1450": "Adults Fighting Men +94 kg",
    # "1452": "Adults Fighting Women -45 kg",
    "14531": "Adults Fighting Women -48 kg & -57 kg",
    # "1454": "Adults Fighting Women -52 kg",
    #"1455": "Adults Fighting Women -57 kg",
    "14561": "Adults Fighting Women -63 kg & -70 kg",
    #"1457": "Adults Fighting Women -70 kg",
    # "1458": "Adults Fighting Women +70 kg",
    # "1473": "Adults Jiu-Jitsu Men -56 kg",
    # "1474": "Adults Jiu-Jitsu Men -62 kg",
    #"1475": "Adults Jiu-Jitsu Men -69 kg",
    #"1476": "Adults Jiu-Jitsu Men -77 kg",
    "14761": "Adults Jiu-Jitsu Men -69 kg & -77 kg",
    "1477": "Adults Jiu-Jitsu Men -85 kg",
    # "1478": "Adults Jiu-Jitsu Men -94 kg",
    # "1479": "Adults Jiu-Jitsu Men +94 kg",
    # "1480": "Adults Jiu-Jitsu Women -45 kg",
    #"1481": "Adults Jiu-Jitsu Women -48 kg",
    "14811": "Adults Jiu-Jitsu Women -48 & -57 kg",
    # "1482": "Adults Jiu-Jitsu Women -52 kg",
    #"1483": "Adults Jiu-Jitsu Women -57 kg",
    "1484": "Adults Jiu-Jitsu Women -63 kg",
    # "1485": "Adults Jiu-Jitsu Women -70 kg",
    # "1486": "Adults Jiu-Jitsu Women +70 kg",
    # "1494": "Adults Show Men",
    # "1495": "Adults Show Mixed",
    # "1493": "Adults Show Women"
    }


# def main_page():
# Main programm starts here

st.title('Team Competition TWG22')
st.write("Use left hand menue to select the teams")

st.sidebar.image("https://i0.wp.com/jjeu.eu/wp-content/uploads/2018/08/jjif-logo-170.png?fit=222%2C160&ssl=1",
                     use_column_width='always')

# select teams
teamA_name = st.sidebar.selectbox("1. Team Red",
                                  help="Choose the red team",
                                  options=teams)
# convert string to variable
teamA = team_dict[teamA_name]

# remove teamA_name from options list
teamB_name = st.sidebar.selectbox('2. Team Blue',
                                  help="Choose the blue team",
                                  options=[x for x in teams if x != teamA_name])
teamB = team_dict[teamB_name]

# get the categories as strings
teamA_str = [key_map[item] for item in teamA]
teamB_str = [key_map[item] for item in teamB]

# display the teams in app
col1, col2 = st.columns(2)
with col1:
    st.markdown(f'<p style="color:#F31C2B;font-size:42px;border-radius:2%;">{teamA_name}</p>', unsafe_allow_html=True)
    with st.expander("Categories Team Red"):
        for i in teamA:
            st.write(key_map[i])
with col2:
    st.markdown(f'<p style="color:#0090CE;font-size:42px;border-radius:2%;">{teamB_name}</p>', unsafe_allow_html=True)
    with st.expander("Categories Team Blue"):
        for i in teamB:
            st.write(key_map[i])

# calc and display overlap between red and blue
result = calc_overlap(teamA, teamB)
intersection_teams = intersection(teamA, teamB)
with st.expander("Shared categories"):
    st.write("These categories exist in at least one of the teams")
    result_st = [key_map.get(item, item) for item in result]
    st.write(result_st)

with st.expander("Intersection"):
    st.write("These categories exist in both teams")
    intersection_teams_st = [key_map.get(item, item) for item in intersection_teams]
    st.write(intersection_teams_st)

exclude = []

# add overlapping categories in categories list
try:
    tA_c1 = intersection_teams_st[0]
    st.sidebar.write(tA_c1)
except IndexError:
    tA_c1 = st.sidebar.selectbox('Choice',
                             help="Choose category",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tA_c1)

try:
    tB_c1 = intersection_teams_st[1]
    st.sidebar.write(tB_c1)
except IndexError:
    tB_c1 = st.sidebar.selectbox('Choice 2',
                             help="Choose category",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tB_c1)

try:
    tA_c2 = intersection_teams_st[2]
    st.sidebar.write(tA_c2)
except IndexError:
    tA_c2 = st.sidebar.selectbox('Choice 3',
                             help="Choose category",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tA_c2)

try:
    tB_c2 = intersection_teams_st[3]
    st.sidebar.write(tB_c2)
except IndexError:
    tB_c2 = st.sidebar.selectbox('Choice 4',
                             help="Choose category",
                             options=[x for x in result_st if x not in exclude])

exclude.append(tB_c2)

# create some columns to display the choices

st.header("Selected categories")
st.write("Use left hand menue to select the categories per team")
sel1, sel2, sel3, sel4, sel5 = st.columns(5)
with sel1:
    st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tA_c1}</p>', unsafe_allow_html=True)
with sel2:
    st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c1}</p>', unsafe_allow_html=True)
with sel3:
    st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tA_c2}</p>', unsafe_allow_html=True)
with sel4:
    st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c2}</p>', unsafe_allow_html=True)


# variable with all remaining categoies
result_over = [x for x in result_st if x not in exclude]
with st.expander("Categories in random draw"):
    st.write("These categories exist in at least one team and were not selected")
    st.write(result_over)

# calculate probabilities

if(len(result_over)>0):
    good_teamA = (len([x for x in teamA_str if x not in exclude])/len(result_over))*100
    good_teamB = (len([x for x in teamB_str if x not in exclude])/len(result_over))*100

    # display probabilties for teams
    teams_sel = [teamB_name, teamA_name]
    values = [good_teamB, good_teamA]
    fig1 = go.Figure(go.Bar(
                x=[good_teamA, good_teamB],
                y=[teamA_name, teamB_name],
                text=[teamA_str, teamB_str],
                marker_color=['#F31C2B', '#0090CE'],
                orientation='h'))
    fig1.update_xaxes(title_text='Chances for "good" category [%]', range=(0, 100))
    fig1.update_yaxes(title_text='Teams')
    st.plotly_chart(fig1)

    if st.sidebar.button('Select Random Category',
                         help="press this button to choose random category"):
        # random choice from all leftover categories
        randcat = random.choice(result_over)
        with sel5:
            # display random cat
            st.write(randcat)

        # show some messages if the category is in
        with col1:
            if randcat in teamA_str:
                st.success(str(randcat) + ' is in ' + teamA_name)
            else:
                st.error(str(randcat) + ' is NOT in ' + teamA_name)
        with col2:
            if randcat in teamB_str:
                st.success(str(randcat) + ' is in ' + teamB_name)
            else:
                st.error(str(randcat) + ' is NOT in ' + teamB_name)

st.sidebar.markdown('<a href="mailto:sportdirector@jjif.org">Contact for problems</a>', unsafe_allow_html=True)

LINK = '[Click here for the source code](https://github.com/ClaudiaBehnke86/TeamCompetition)'
st.markdown(LINK, unsafe_allow_html=True)


# ugly but works (166 is TWG ID)
#df = getdata(str(166), st.secrets['user'], st.secrets['password'])

#df_red = df[df['country_code'] == str(teamA_name)]
#df_blue = df[df['country_code'] == str(teamB_name)]

#with col1:
#    with st.expander("Athletes Team Red"):
#        st.write(df_red)
#with col2:
#    with st.expander("Categories Team Blue"):
#        st.write(df_blue)

    # number_of_participants
    #num_par_dic = newdict['number_of_participants']
    #num_par_dict_exp = {}

    #for key, value in num_par_dic.items():
    #    if str(key) in key_map.keys():
    #        num_par_dict_exp[key_map[str(key)]] = value
    #    else:
    #        print("no mapping found for key ", key)

# page_names_to_funcs = {
#     "Calculate Chances": main_page,
#     "Select Althletes": page2,
# }

# selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
# page_names_to_funcs[selected_page]()
