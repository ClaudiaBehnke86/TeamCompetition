'''

Create a mixed team compeition for TWG 2022 that allows the teams
to choose their categories and one random category is selected

'''
import random
import streamlit as st
import plotly.graph_objects as go

import requests
import json
import plotly.express as px
from requests.auth import HTTPBasicAuth
import pandas as pd 
from pandas import json_normalize


CLUBNAME_COUNTRY_MAP = {"Belgian Ju-Jitsu Federation": 'BEL',
                        "Deutscher Ju-Jitsu Verband e.V.": 'GER',
                        "Federazione Ju Jitsu Italia": 'ITA',
                        "Romanian Martial Arts Federation": 'ROU'}

def get_athletes_cat(eventid, cat_id, user, password):
    """
    get the athletes form sportdata
    """

    uri = 'https://www.sportdata.org/ju-jitsu/rest/event/categories/'+str(eventid)+'/'+str(cat_id)+'/'

    response = requests.get(uri, auth=HTTPBasicAuth(user, password),)
    d = response.json()

    df_out = json_normalize(d["members"])

    if not df_out.empty:
        if df_out['type'].str.contains('athlete').any():
            #match to name format of Duo cats
            df_out['name'] = df_out['first'] + " " + df_out['last']
            df = df_out[['name','country_code']]
            df['cat_id'] = str(cat_id)
        else:
            # for an unclear reason teams to no have a coutnry code... sigh.. 
            # i will write a function to convert club name to country... 
            df_out['country_code'] = df_out['club_name'].replace(CLUBNAME_COUNTRY_MAP)
            df = df_out[['name', 'country_code']]
            df['cat_id'] = str(cat_id)
    else:
        df =pd.DataFrame()
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


#  team categories
#  taken from outlines https://cdn.sportdata.org/96eb874d-48f8-4ed3-b58a-145b53d43de4/ 
key_map = { 
    "FM1": "Adults Fighting Men -69 kg",
    "FM2": "Adults Fighting Men -85kg",
    "FM3": "Adults Fighting Men +85kg",
    "FW1": "Adults Fighting Women -52 kg",
    "FW2": "Adults Fighting Women -63 kg",
    "FW3": "Adults Fighting Women +63 kg",
    "JM1": "Adults Jiu-Jitsu Men -69 kg",
    "JM2": "Adults Jiu-Jitsu Men -85 kg",
    "JM3": "Adults Jiu-Jitsu Men +85 kg",
    "JW1": "Adults Jiu-Jitsu Women -52",
    "JW2": "Adults Jiu-Jitsu Women -63 kg",
    "JW3": "Adults Jiu-Jitsu Women +63 kg",
    "D": "Adults Duo",
    }

# mapping all sportdata cat IDs to that are allowed in event (Adults & U21)
cat_to_ids = {
    "FM1": [1444, 1451, 1446, 1429, 1430, 1431],
    "FM2": [1447, 1448, 1432, 1433],
    "FM3": [1449, 1450, 1434, 1435],
    "FW1": [1452, 1453, 1454, 1436, 1437, 1438],
    "FW2": [1455, 1456, 1439, 1441],
    "FW3": [1457, 1458, 1442, 1443],
    "JM1": [1473, 1474, 1475, 1459, 1460, 1461],
    "JM2": [1476, 1477, 1462, 1463],
    "JM3": [1478, 1479, 1464, 1465],
    "JW1": [1480, 1481, 1482, 1466, 1467, 1468],
    "JW2": [1483, 1484, 1469, 1470],
    "JW3": [1485, 1486, 1471, 1472],
    "D": [1491, 1492, 1493, 1487, 1488, 1489],
}

# Main programm starts here
st.title('Team Competition')
st.write("Use left hand menue to select the teams")


st.sidebar.image("https://i0.wp.com/jjeu.eu/wp-content/uploads/2018/08/jjif-logo-170.png?fit=222%2C160&ssl=1",
                 use_column_width='always')


apidata = st.sidebar.checkbox("Get registration from Sportdata API", 
                              help="Check if the registration is still open",
                              value=True)
if apidata is True:
    sd_key = st.sidebar.number_input("Enter the number of Sportdata event number",
                                     help='is the number behind vernr= in the URL', value=325)
    # create empty temporary list for catgories to merge into team categories
    list_df_new_total = []

    for x in cat_to_ids.keys(): 
        ids = cat_to_ids.get(x)
        list_df_new = []
        for id_num in ids:
            athletes_cat = get_athletes_cat(str(sd_key), str(id_num), st.secrets['user'], st.secrets['password'])        
            list_df_new.append(athletes_cat)
            df_new = pd.concat(list_df_new)
            df_new['team_id'] = str(x)
        list_df_new_total.append(df_new)

df_total = pd.concat(list_df_new_total)

df_teams = df_total[['team_id','name', 'country_code']].groupby(['team_id', 'country_code']).count().reset_index()


# add frequency column for counting the number of categories
df_teams['cat_count'] = df_teams['country_code'].map(df_teams['country_code'].value_counts())
# only enter teams with at least X categories present
df_teams = df_teams[df_teams['cat_count'] > 5]
del df_teams['cat_count']

# allow the selection of teams
allcountry = df_teams.country_code.unique()
teams = st.sidebar.multiselect('Select all countries that want to particpate', allcountry, allcountry)
df_teams = df_teams[df_teams['country_code'].isin(teams)]

# select teams
teamA_name = st.sidebar.selectbox("1. Team Red",
                                  help="Choose the red team",
                                  options=teams)


# remove teamA_name from options list
teamB_name = st.sidebar.selectbox('2. Team Blue',
                                  help="Choose the blue team",
                                  options=[x for x in teams if x != teamA_name])


# get the categories per team as list
teamA = df_teams['team_id'][df_teams['country_code'] == teamA_name].tolist()
teamB = df_teams['team_id'][df_teams['country_code'] == teamB_name].tolist()

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

with st.expander("Intersection"):
    st.write("These categories exist in both teams")
    intersection_teams_st = [key_map.get(item, item) for item in intersection_teams]
    st.write(intersection_teams_st)

with st.expander("Selectable categories"):
    st.write("These categories exist in only one of the teams")
    result_st = [key_map.get(item, item) for item in result]
    result_st_sel = [x for x in result_st if x not in intersection_teams_st]
    st.write(result_st_sel)

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

st.header("Selected categories")

st.write(tA_c1)
st.write("Selection")
st.markdown("""---""")

st.write(tB_c1)
st.write("Selection")
st.markdown("""---""")


st.write(tA_c2)
st.write("Selection")
st.markdown("""---""")

st.write(tB_c2)
st.write("Selection")
st.markdown("""---""")


# with sel1:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tA_c1}</p>', unsafe_allow_html=True)
# with sel2:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c1}</p>', unsafe_allow_html=True)
# with sel3:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tA_c2}</p>', unsafe_allow_html=True)
# with sel4:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c2}</p>', unsafe_allow_html=True)

# variable with all remaining categoies
result_over = [x for x in result_st if x not in exclude]
with st.expander("Categories in random draw"):
    st.write("These categories exist in at least one team and were not selected")
    st.write(result_over)

# calculate probabilities

try:
    random = intersection_teams_st[4]
    st.sidebar.write(random)
except IndexError:
# create some columns to display the choices
    if(len(result_over)>1 and len(result_over)<3):
        random = st.sidebar.selectbox('Choice 5',
                                 help="Choose category",
                                 options=[x for x in result_st if x not in exclude])
        st.write(random)
        st.write("Selection")
        st.markdown("""---""")

    elif(len(result_over)>0):

        good_teamA = (len([x for x in teamA_str if x not in exclude])/len(result_over))*100
        good_teamB = (len([x for x in teamB_str if x not in exclude])/len(result_over))*100


         # display probabilties for teams
        with st.expander("Display probabilties for teams"):
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
        
            # display random cat
            st.write(randcat)
            st.write("Selection")
            st.markdown("""---""")


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

