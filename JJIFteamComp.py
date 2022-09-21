'''

Create a mixed team competiton that allows the teams

There are team categories which consist of individual categories:
F.e. in Adults Fighting Men -85 kg athletes from Adults Fighting Men -77 kg 
and Adults Fighting Men -85 kg  could compete in the category 

'''
import random
import streamlit as st
import plotly.graph_objects as go

import requests
import json
import plotly.express as px
from requests.auth import HTTPBasicAuth
import pandas as pd 
pd.options.mode.chained_assignment = None  # default='warn'

from pandas import json_normalize

#  categories and short ids
#  from outlines https://cdn.sportdata.org/96eb874d-48f8-4ed3-b58a-145b53d43de4/
#  if you change something here make sure to also change it for TEAMCAT_TO_CATID dict!

TEAMCAT_NAME_DICT = { 
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
    "D": "Adults Duo"}

# mapping all sportdata category IDs to the team categories
# in this case (Adults & U21)
TEAMCAT_TO_CATID = {
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

#  since teams categories have no country I use this quick and dirty workaround
#  to map clubnames in sportdata api to country codes... 
CLUBNAME_COUNTRY_MAP = {"Belgian Ju-Jitsu Federation": 'BEL',
                        "Deutscher Ju-Jitsu Verband e.V.": 'GER',
                        "Federazione Ju Jitsu Italia": 'ITA',
                        "Romanian Martial Arts Federation": 'ROU'}


def get_athletes_cat(eventid, cat_id, user, password):
    """
    get the athletes form sportdata per category & export to a nice data frame

    Parameters
    ----------
    eventid
        sportdata event_id (from database) [int]
    cat_id
        sportdata category_id (from database) [int]
     user
        api user name
    password
        api user password    
    """

    #URI of the rest API
    uri = 'https://www.sportdata.org/ju-jitsu/rest/event/categories/'+str(eventid)+'/'+str(cat_id)+'/'

    response = requests.get(uri, auth=HTTPBasicAuth(user, password))
    d = response.json()
    df_out = json_normalize(d["members"])

    if not df_out.empty:
        #first idivdual categories
        if df_out['type'].str.contains('athlete').any():
            #  match to name format of Duo categories
            df_out['name'] = df_out['first'] + " " + df_out['last']
            df = df_out[['name' , 'country_code']]
            # add the origial category id
            df['cat_id'] = str(cat_id)
        else:
            # for an unclear reason teams to no have a country code...
            # convert club name to country using dict...
            df_out['country_code'] = df_out['club_name'].replace(CLUBNAME_COUNTRY_MAP)
            df = df_out[['name', 'country_code']]
            df['cat_id'] = str(cat_id)
    else:
        # just return empty datafram
        df =pd.DataFrame()
    return df


def calc_overlap(teama, teamb):
    '''
    Function to calc the overlap categories between the teams
    Returns list with overlapping categorries

    Parameters
    ----------
    teama
        list with teamcategoreis from team A
    teamb
        list with teamcategoreis from team B
    '''
    in_first = set(teama)
    in_second = set(teamb)

    in_second_but_not_in_first = in_second - in_first

    result_out = teama + list(in_second_but_not_in_first)

    return result_out


def intersection(teama, teamb):
    '''
    Function to calc the intersection categories between the teams
    Returns list with intersection categorries
    
    Parameters
    ----------
    teama
        list with teamcategoreis from team A
    teamb
        list with teamcategoreis from team B

    '''
    result_out_overlapp = [value for value in teama if value in teamb]

    return result_out_overlapp

def rev_look(val, dict):
    ''' revese lookup of key.
    Returns first matching key
    Parameters
    ----------
    val
        value to be looked up
    dict
        dict that contains the keys and value

    '''
    key = next(key for key, value in dict.items() if value == val)

    return key

st.title('Team Competition')
st.sidebar.image("https://i0.wp.com/jjeu.eu/wp-content/uploads/2018/08/jjif-logo-170.png?fit=222%2C160&ssl=1",
                 use_column_width='always')

page = st.sidebar.selectbox('Select mode',['Preparation','Matches']) 

if page == 'Preparation':        
    apidata = st.checkbox("Get registration from Sportdata API", 
                                  help="Check if the registration is still open",
                                  value=True)
    if apidata is True:
        sd_key = st.number_input("Enter the number of Sportdata event number",
                                         help='is the number behind vernr= in the URL', value=325)
        # create empty temporary list for catgories to merge into team categories
        list_df_new_total = []

        for x in TEAMCAT_TO_CATID:
            ids = TEAMCAT_TO_CATID.get(x)
            list_df_new = []
            for id_num in ids:
                athletes_cat = get_athletes_cat(str(sd_key),
                                                str(id_num),
                                                st.secrets['user'],
                                                st.secrets['password'])
                list_df_new.append(athletes_cat)
                df_new = pd.concat(list_df_new)
                df_new['team_id'] = str(x)
            list_df_new_total.append(df_new)
    df_total = pd.concat(list_df_new_total)
    df_teams = df_total[['team_id','name', 'country_code']].groupby(['team_id', 'country_code']).count().reset_index()


    # remove small teams (small = less than 5 team cat present)
    # add frequency column for counting the number of categories
    df_teams['cat_count'] = df_teams['country_code'].map(df_teams['country_code'].value_counts())
    # only enter teams with at least X categories present
    team_size = st.number_input("Minimum number of members in a team",
                                help='define the minimum number', value=5)
    df_teams = df_teams[df_teams['cat_count'] > team_size]
    del df_teams['cat_count']

    # selection of teams in menue
    allcountry = df_teams.country_code.unique()
    teams = st.multiselect('Select all countries that want to particpate', allcountry, allcountry)
    df_total = df_total[df_total['country_code'].isin(teams)]

    file = df_total.to_csv(index=False)
    btn = st.download_button(
        label="Download data from event",
        data=file,
        file_name="Data",
        mime="csv")

else:
        
    # Main programm starts here
    
    st.write("Use left hand menue to select the teams")

    uploaded_file = st.sidebar.file_uploader("Choose a file",
                                     help="Make sure to have a CSV with the right input")

    if uploaded_file is not None:
        df_total = pd.read_csv(uploaded_file)
    
        df_teams = df_total[['team_id','name', 'country_code']].groupby(['team_id', 'country_code']).count().reset_index()

        teams = df_teams.country_code.unique()

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

        # display the teams in list
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<p style="color:#F31C2B;font-size:42px;border-radius:2%;">{teamA_name}</p>', unsafe_allow_html=True)
            with st.expander("Categories Team Red"):
                for i in teamA:
                    st.write(TEAMCAT_NAME_DICT[i])
        with col2:
            st.markdown(f'<p style="color:#0090CE;font-size:42px;border-radius:2%;">{teamB_name}</p>', unsafe_allow_html=True)
            with st.expander("Categories Team Blue"):
                for i in teamB:
                    st.write(TEAMCAT_NAME_DICT[i])

        # calc and display overlap between red and blue
        result = calc_overlap(teamA, teamB)
        intersection_teams = intersection(teamA, teamB)

        with st.expander("Intersection"):
            st.write("These categories exist in both teams")
            intersection_teams_str = [TEAMCAT_NAME_DICT.get(item, item) for item in intersection_teams]
            st.write(intersection_teams_str)

        with st.expander("Selectable categories"):
            st.write("These categories exist in only one of the teams")
            result_st = [TEAMCAT_NAME_DICT.get(item, item) for item in result]
            result_st_sel = [x for x in result_st if x not in intersection_teams_str]
            st.write(result_st_sel)

        #list to add categories that are already selected
        exclude = []
        # list for selected categories
        selected = []
        # amount of categories that will fight:
        MATCHES = 7


        #3 cases:   
        if len(intersection_teams) == MATCHES:
            # excat the same number
            # just display the the category and let team select the atlhtes

            st.sidebar.header("Selected categories")
            st.sidebar.write('- Exact the same categories')
            st.sidebar.write('Nothing to do')
            selected = intersection_teams
            for i in selected:
                st.sidebar.write(TEAMCAT_NAME_DICT[i])

        elif len(intersection_teams) > MATCHES:
            # more options than MATCHES
            # remove options

            # remove till even or uneven each team removes same amount of categories
            # if leftover: random choice
            st.sidebar.write('- More options than MATCHES')
            st.sidebar.write('Remove categories')
            selected = intersection_teams

            #check how many cats are to much:
            overheadd_cat = len(intersection_teams) - MATCHES

            # remove always 2 categories
            while overheadd_cat > 2:

                tA = st.sidebar.selectbox('Choice Red',
                                          help="Choose category to remove",
                                          options=[TEAMCAT_NAME_DICT[x] for x in selected])
                # revese lookup of key
                selected.remove(rev_look(tA, TEAMCAT_NAME_DICT))
                exclude.append(tA)

                tB = st.sidebar.selectbox('Choice Blue',
                                          help="Choose category to remove",
                                          options=[TEAMCAT_NAME_DICT[x] for x in selected])
                selected.remove(rev_look(tB, TEAMCAT_NAME_DICT))
                exclude.append(tB)

                overheadd_cat = overheadd_cat - 2

            if (overheadd_cat % 2) == 0:
                # The remaining number is even
                st.write("both teams need to choose")

                tA = st.sidebar.selectbox('Choice Red',
                                          help="Choose category to remove",
                                          options=[TEAMCAT_NAME_DICT[x] for x in selected])
                # revese lookup of key

                selected.remove(rev_look(tA, TEAMCAT_NAME_DICT))
                exclude.append(tA)

                tB = st.sidebar.selectbox('Choice Blue',
                                          help="Choose category to remove",
                                          options=[TEAMCAT_NAME_DICT[x] for x in selected])
                selected.remove(rev_look(tB, TEAMCAT_NAME_DICT))
                exclude.append(tB)

            else:
                # the number is odd
                if st.sidebar.button('Select Random Category to remove',
                                      help="press this button to choose random category to remove"):
                    # random choice from all leftover categories
                    result_over = [x for x in selected]
                    randcat = random.choice(result_over)
                    # display random cat
                    st.sidebar.markdown(f'<p style="background-color:#000000;border-radius:4%;">{TEAMCAT_NAME_DICT[randcat]}</p>', unsafe_allow_html=True)
                    selected.remove(randcat)

            #for i in selected:

            #    st.sidebar.write(TEAMCAT_NAME_DICT[i])

        elif len(intersection_teams_str) < MATCHES:
            # less options than MATCHES
            # add teams teams
            st.sidebar.write('Less options than MATCHES')
            st.sidebar.write('Add categrories')
            selected = intersection_teams
            #for i in selected:
            #    st.sidebar.write(TEAMCAT_NAME_DICT[i])

            # add the selected teams to the excluded list
            # (they can't be selected twice)
            exclude.append(intersection_teams_str)

            # check how many teams are missing:
            miss_cat = MATCHES - len(intersection_teams_str)

            # add always 2 categories
            while miss_cat > 2:

                tA = st.sidebar.selectbox('Choice Red',
                                          help="Choose category",
                                          options=[x for x in result_st_sel if x not in exclude])
                # revese lookup of key
                selected.append(rev_look(tA, TEAMCAT_NAME_DICT))
                exclude.append(tA)

                tB = st.sidebar.selectbox('Choice Blue',
                                         help="Choose category",
                                         options=[x for x in result_st_sel if x not in exclude])
                selected.append(rev_look(tB, TEAMCAT_NAME_DICT))
                exclude.append(tB)

                miss_cat = miss_cat - 2

            if (miss_cat % 2) == 0:
                # The remaining number is even
                st.write("both teams need to choose")

                tA = st.sidebar.selectbox('Choice Red',
                                             help="Choose category",
                                             options=[x for x in result_st_sel if x not in exclude])
                # revese lookup of key
                selected.append(rev_look(tA, TEAMCAT_NAME_DICT))
                exclude.append(tA)

                tB = st.sidebar.selectbox('Choice Blue',
                                         help="Choose category",
                                         options=[x for x in result_st_sel if x not in exclude])
                selected.append(rev_look(tB, TEAMCAT_NAME_DICT))
                exclude.append(tB)
            else:
                # the number is odd
                if st.sidebar.button('Select Random Category',
                                      help="press this button to choose random category"):
                    # random choice from all leftover categories
                    result_over = [x for x in result_st_sel if x not in exclude]
                    randcat = random.choice(result_over)
                    # display random cat
                    st.sidebar.markdown(f'<p style="background-color:#000000;border-radius:4%;">{randcat}</p>', unsafe_allow_html=True)
                    # revese lookup of key
                    key = next(key for key, value in TEAMCAT_NAME_DICT.items() if value == randcat)
                    selected.append(key)


        if(len(selected) == MATCHES):
            st.sidebar.header("Selected categories")
            for i in selected:
                st.sidebar.write(TEAMCAT_NAME_DICT[i])

            st.header("Selected categories - choose athletes")

            col1a, col2a = st.columns(2)
            with col1a:

                for i, j in enumerate(selected):
                    st.write(TEAMCAT_NAME_DICT[j])
                    st.write(df_total['name'][(df_total['country_code'] == teamA_name) & (df_total['team_id'] == str(j))])

            with col2a:
                for i, j in enumerate(selected):
                    st.write(TEAMCAT_NAME_DICT[j])
                    st.write(df_total['name'][(df_total['country_code'] == teamB_name) & (df_total['team_id'] == str(j))])



# with sel1:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tA}</p>', unsafe_allow_html=True)
# with sel2:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c1}</p>', unsafe_allow_html=True)
# with sel3:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB}</p>', unsafe_allow_html=True)
# with sel4:
#     st.markdown(f'<p style="background-color:#000000;border-radius:2%;">{tB_c2}</p>', unsafe_allow_html=True)

# # variable with all remaining categoies
# result_over = [x for x in result_st if x not in exclude]
# with st.expander("Categories in random draw"):
#     st.write("These categories exist in at least one team and were not selected")
#     st.write(result_over)

# # calculate probabilities

# try:
#     random = intersection_teams_str[4]
#     st.sidebar.write(random)
# except IndexError:
# # create some columns to display the choices
#     if(len(result_over)>1 and len(result_over)<3):
#         random = st.sidebar.selectbox('Choice 5',
#                                  help="Choose category",
#                                  options=[x for x in result_st if x not in exclude])
#         st.write(random)
#         st.write("Selection")
#         st.markdown("""---""")

#     elif(len(result_over)>0):

#         good_teamA = (len([x for x in teamA_str if x not in exclude])/len(result_over))*100
#         good_teamB = (len([x for x in teamB_str if x not in exclude])/len(result_over))*100


#          # display probabilties for teams
#         with st.expander("Display probabilties for teams"):
#             teams_sel = [teamB_name, teamA_name]
#             values = [good_teamB, good_teamA]
#             fig1 = go.Figure(go.Bar(
#                          x=[good_teamA, good_teamB],
#                          y=[teamA_name, teamB_name],
#                          text=[teamA_str, teamB_str],
#                          marker_color=['#F31C2B', '#0090CE'],
#                          orientation='h'))
#             fig1.update_xaxes(title_text='Chances for "good" category [%]', range=(0, 100))
#             fig1.update_yaxes(title_text='Teams')
#             st.plotly_chart(fig1)

#         if st.sidebar.button('Select Random Category',
#                               help="press this button to choose random category"):
#              # random choice from all leftover categories
#             randcat = random.choice(result_over)
        
#             # display random cat
#             st.write(randcat)
#             st.write("Selection")
#             st.markdown("""---""")


#             # show some messages if the category is in
#             with col1:
#                 if randcat in teamA_str:
#                     st.success(str(randcat) + ' is in ' + teamA_name)
#                 else:
#                     st.error(str(randcat) + ' is NOT in ' + teamA_name)
#             with col2:
#                 if randcat in teamB_str:
#                     st.success(str(randcat) + ' is in ' + teamB_name)
#                 else:
#                     st.error(str(randcat) + ' is NOT in ' + teamB_name)


st.sidebar.markdown('<a href="mailto:sportdirector@jjif.org">Contact for problems</a>', unsafe_allow_html=True)

LINK = '[Click here for the source code](https://github.com/ClaudiaBehnke86/TeamCompetition)'
st.markdown(LINK, unsafe_allow_html=True)

