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

from datetime import datetime
from datetime import timedelta

from pandas import json_normalize
from fpdf import FPDF
from fpdf import Template

import base64

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

class PDF(FPDF):
    def header(self):
        # Logo
        self.image('Logo_real.png', 8, 8, 30)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(70)
        # Title
        self.cell(30, 10, 'Mixed Team Competition','C')
        # Line break
        self.ln(20)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Printed ' + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ' Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')



#  categories and short ids
#  from outlines https://cdn.sportdata.org/96eb874d-48f8-4ed3-b58a-145b53d43de4/
#  if you change something here make sure to also change it for TEAMCAT_TO_CATID dict!
TEAMCAT_NAME_DICT = { 
    "FM1": "Adults Fighting Men -69 kg",
    "FM2": "Adults Fighting Men -85 kg",
    "FM3": "Adults Fighting Men +85 kg",
    "FW1": "Adults Fighting Women -52 kg",
    "FW2": "Adults Fighting Women -63 kg",
    "FW3": "Adults Fighting Women +63 kg",
    "JM1": "Adults Jiu-Jitsu Men -69 kg",
    "JM2": "Adults Jiu-Jitsu Men -85 kg",
    "JM3": "Adults Jiu-Jitsu Men +85 kg",
    "JW1": "Adults Jiu-Jitsu Women -52 kg",
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

TEAMCAT_ALLOWED = {
    "FM1": ["JM1"],
    "FM2": ["FM1","JM1","JM2"],
    "FM3": ["FM2","JM2","JM3"],
    "FW1": ["JW1"],
    "FW2": ["FW1","JW1", "JW2"],
    "FW3": ["FW2","JW2","JW3"],
    "JM1": ["FM1"],
    "JM2": ["JM1","FM1","FM2"],
    "JM3": ["JM2","FM2","FM3"],
    "JW1": ["JF1"],
    "JW2": ["JW1","FW1","FW2"],
    "JW3": ["JW2","FW2","FW3"],
    "D":[]
}

ID_TO_NAME = {
    "1466": "U21 Jiu-Jitsu Women -45 kg",
    "1467": "U21 Jiu-Jitsu Women -48 kg",
    "1468": "U21 Jiu-Jitsu Women -52 kg",
    "1469": "U21 Jiu-Jitsu Women -57 kg",
    "1470": "U21 Jiu-Jitsu Women -63 kg",
    "1471": "U21 Jiu-Jitsu Women -70 kg",
    "1472": "U21 Jiu-Jitsu Women +70 kg",
    "1459": "U21 Jiu-Jitsu Men -56 kg",
    "1460": "U21 Jiu-Jitsu Men -62 kg",
    "1461": "U21 Jiu-Jitsu Men -69 kg",
    "1462": "U21 Jiu-Jitsu Men -77 kg",
    "1463": "U21 Jiu-Jitsu Men -85 kg",
    "1464": "U21 Jiu-Jitsu Men -94 kg",
    "1465": "U21 Jiu-Jitsu Men +94 kg",
    "1488": "U21 Duo Men",
    "1487": "U21 Duo Mixed",
    "1489": "U21 Duo Women",
    "1436": "U21 Fighting Women -45 kg",
    "1437": "U21 Fighting Women -48 kg",
    "1438": "U21 Fighting Women -52 kg",
    "1439": "U21 Fighting Women -57 kg",
    "1441": "U21 Fighting Women -63 kg",
    "1442": "U21 Fighting Women -70 kg",
    "1443": "U21 Fighting Women +70 kg",
    "1429": "U21 Fighting Men -56 kg",
    "1430": "U21 Fighting Men -62 kg",
    "1431": "U21 Fighting Men -69 kg",
    "1432": "U21 Fighting Men -77 kg",
    "1433": "U21 Fighting Men -85 kg",
    "1434": "U21 Fighting Men -94 kg",
    "1435": "U21 Fighting Men +94 kg",
    "1497": "U21 Show Men",
    "1498": "U21 Show Mixed",
    "1496": "U21 Show Women",
    "1491": "Adults Duo Men",
    "1492": "Adults Duo Mixed",
    "1490": "Adults Duo Women",
    "1444": "Adults Fighting Men -56 kg",
    "1451": "Adults Fighting Men -62 kg",
    "1446": "Adults Fighting Men -69 kg",
    "1447": "Adults Fighting Men -77 kg",
    "1448": "Adults Fighting Men -85 kg",
    "1449": "Adults Fighting Men -94 kg",
    "1450": "Adults Fighting Men +94 kg",
    "1452": "Adults Fighting Women -45 kg",
    "1453": "Adults Fighting Women -48 kg",
    "1454": "Adults Fighting Women -52 kg",
    "1455": "Adults Fighting Women -57 kg",
    "1456": "Adults Fighting Women -63 kg",
    "1457": "Adults Fighting Women -70 kg",
    "1458": "Adults Fighting Women +70 kg",
    "1473": "Adults Jiu-Jitsu Men -56 kg",
    "1474": "Adults Jiu-Jitsu Men -62 kg",
    "1475": "Adults Jiu-Jitsu Men -69 kg",
    "1476": "Adults Jiu-Jitsu Men -77 kg",
    "1477": "Adults Jiu-Jitsu Men -85 kg",
    "1478": "Adults Jiu-Jitsu Men -94 kg",
    "1479": "Adults Jiu-Jitsu Men +94 kg",
    "1480": "Adults Jiu-Jitsu Women -45 kg",
    "1481": "Adults Jiu-Jitsu Women -48 kg",
    "1482": "Adults Jiu-Jitsu Women -52 kg",
    "1483": "Adults Jiu-Jitsu Women -57 kg",
    "1484": "Adults Jiu-Jitsu Women -63 kg",
    "1485": "Adults Jiu-Jitsu Women -70 kg",
    "1486": "Adults Jiu-Jitsu Women +70 kg",
    "1494": "Adults Show Men",
    "1495": "Adults Show Mixed",
    "1493": "Adults Show Women"
    }


#  since teams categories have no country I use this quick and dirty workaround
#  to map clubnames in sportdata api to country codes... 
CLUBNAME_COUNTRY_MAP = {"Belgian Ju-Jitsu Federation": 'BEL',
                        "Deutscher Ju-Jitsu Verband e.V.": 'GER',
                        "Federazione Ju Jitsu Italia": 'ITA',
                        "Romanian Martial Arts Federation": 'ROU',
                        "Österreichischer Jiu Jitsu Verband": "AUT",
                        "Taiwan Ju Jitsu Federation": "TPE"
                        }


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
            df['cat_id'] = cat_id
            df['cat_name'] = df['cat_id'].replace(ID_TO_NAME)
        else:
            # for an unclear reason teams to no have a country code...
            # convert club name to country using dict...
            # and fix nameing in duo
            df_out['country_code'] = df_out['club_name'].replace(CLUBNAME_COUNTRY_MAP)
            df_out['name'] = df_out['name'].str.split('(').str[1]
            df_out['name'] = df_out['name'].str.split(')').str[0]
            df_out['name'].replace(",", " /", regex=True, inplace=True)
            df_out['name'].replace("_", " /", regex=False, inplace=True)
            df = df_out[['name', 'country_code']]
            df['cat_id'] = cat_id
            df['cat_name'] = df['cat_id'].replace(ID_TO_NAME)
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

def draw_as_table(df):

    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    df["select"] = " "
    fig = go.Figure(data=[go.Table(
                    columnwidth = [10,50,40],
                    header=dict(values=["Select", "Name", "Original Category"], # values=list(df.columns),
                    fill_color=headerColor,
                    font = dict(family= "Arial", color = 'white', size = 12),
                    align='left'),
                    cells=dict(values=[df.select, df.name, df.cat_name],
                        line_color='darkslategray',
                        # 2-D list of colors for alternating rows
                        fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
                        align = ['left', 'left'],
                        font = dict(family= "Arial", color = 'black', size = 10)
                        ))
                    ])

    numb_row = len(df.index)

    fig.update_layout(
        autosize=False,
        width=550,
        height=(numb_row+1) *25,
        margin=dict(
            l=20,
            r=50,
            b=0,
            t=0,
            pad=4
            ),
        )

    return fig

def draw_as_table_teamID(df):

    headerColor = 'grey'
    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    df["select"] = " "
    fig = go.Figure(data=[go.Table(
                    columnwidth = [10,60,40],
                    header=dict(values=["Select", "Team Categories"],
                    fill_color=headerColor,
                    font = dict(family= "Arial", color = 'white', size = 12),
                    align='left'),
                    cells=dict(values=[df.select, df.team_cats],
                        line_color='darkslategray',
                        # 2-D list of colors for alternating rows
                        fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
                        align = ['left', 'left'],
                        font = dict(family= "Arial", color = 'black', size = 10)
                        ))
                    ])

    numb_row = len(df.index)

    fig.update_layout(
        autosize=False,
        width=600,
        height=(numb_row+1) *25,
        margin=dict(
            l=20,
            r=50,
            b=0,
            t=0,
            pad=4
            ),
        )

    return fig

def confirm_text(team, give_time):
    confirm_txt = "Please return this sheet latest at " + str((datetime.now() + timedelta(minutes = give_time)).strftime('%Y-%m-%d %H:%M')) +"\n \
I hereby declare that the team selection is final and can not be changed anymore. \n \
                                                                                                \n \
                                                                                                \n \
_______________________                             _________________________ \n \
Confirmation Team  "+ str(team) +"                                     Confirmation OC "

    return confirm_txt          

st.title('Team Competition')
st.sidebar.image("https://i0.wp.com/jjeu.eu/wp-content/uploads/2018/08/jjif-logo-170.png?fit=222%2C160&ssl=1",
                 use_column_width='always')

page = st.sidebar.selectbox('Select mode',['Preparation','Selection & Match Phase']) 

if page == 'Preparation':        
    apidata = st.checkbox("Get registration from Sportdata API", 
                                  help="Check if the registration is still open",
                                  value=True)
    if apidata is True:
        sd_key = st.number_input("Enter the number of Sportdata event number",
                                         help='is the number behind vernr= in the URL', value=325)
        # create empty temporary list for catgories to merge into team categories
        list_df_new_total = []

        my_bar = st.progress(0)
        with st.spinner('Read in data'):
            for i,x in enumerate(TEAMCAT_TO_CATID):
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
                my_bar.progress((i+1)/len(TEAMCAT_TO_CATID))

    df_total = pd.concat(list_df_new_total)
    df_teams = df_total[['team_id','name', 'country_code']].groupby(['team_id', 'country_code']).count().reset_index()


    # remove small teams (small = less than 5 team cat present)
    # add frequency column for counting the number of categories
    df_teams['cat_count'] = df_teams['country_code'].map(df_teams['country_code'].value_counts())
    # only enter teams with at least X categories present
    team_size = st.number_input("Minimum number of members in a team",
                                help='define the minimum number', value=5, min_value = 1, max_value = len(TEAMCAT_NAME_DICT))

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
        file_name="Data.csv",
        mime="csv")

    pdf_sel = PDF()

    for k in teams:

        pdf_sel.add_page()
        pdf_sel.set_font("Arial", size = 25)
        pdf_sel.cell(200, 20, txt = "Registration Team " + k,
              ln = 1, align = 'C')
        pdf_sel.alias_nb_pages()
        pdf_sel.set_font("Arial", size = 15)
        pdf_sel.cell(200, 10, txt = "Please select up to two athlets per category",
              ln = 1, align = 'L')

        for i in TEAMCAT_NAME_DICT:
            names_sel = df_total[['name','cat_name']][(df_total['country_code'] == k) & (df_total['team_id'] == str(i))]
            pdf_sel.cell(200, 10, txt = TEAMCAT_NAME_DICT[i],
                  ln = 2, align = 'C')

            if(len(names_sel)>0):
                fig = draw_as_table(names_sel)
                png_name = str(TEAMCAT_NAME_DICT[i]) + str(k) + "sel.png"
                fig.write_image(png_name)
                pdf_sel.image(png_name) 


        pdf_sel.alias_nb_pages()
        pdf_sel.set_font("Arial", size = 12)        
        
        pdf_sel.cell(200, 6, txt = "You can add up to two athlets. A Duo team counts as one athlete",
              ln = 1, align = 'L')
        pdf_sel.cell(200, 15, txt = "_____________   ______________________________      _________________________",
              ln = 1, align = 'L')
        pdf_sel.cell(200, 6, txt = "Team Category     Name, First Name                                   Original Category",
              ln = 1, align = 'L')
        pdf_sel.cell(200, 15, txt = "_____________   ______________________________      _________________________",
              ln = 1, align = 'L')
        pdf_sel.cell(200, 6, txt = "Team Category     Name, First Name                                   Original Category",
              ln = 1, align = 'L')
        pdf_sel.multi_cell(200, 6, txt = confirm_text(str(k),120), align = 'L')


    pdf_sel.output("dummy2.pdf")  
    with open("dummy2.pdf", "rb") as pdf_file:
        PDFbyte2 = pdf_file.read()

    st.download_button(label="Download Team  Registration lists",
                       data=PDFbyte2,
                       file_name='Download Teams Registration.pdf')        

else:
        
    # Main programm starts here
    st.write("Use left hand menue to select the teams")

    uploaded_file = st.sidebar.file_uploader("Choose a file",
                                     help="Make sure to have a CSV with the right input")

    # amount of categories that will fight:
    MATCHES = st.sidebar.number_input("Number of fight between teams",
                                help='Define the number', value=7,  min_value = 1, max_value = len(TEAMCAT_NAME_DICT))


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

        team_sel = [teamA_name,teamB_name]
        # calc and display overlap between red and blue

        result = calc_overlap(teamA, teamB)
        intersection_teams = intersection(teamA, teamB)

        st.write("There are " + str(len(intersection_teams)) +" overlapping categories in this team match") 
        with st.expander("Show Overlapping Categories"):
            st.write("These categories exist in both teams")
            intersection_teams_str = [TEAMCAT_NAME_DICT.get(item, item) for item in intersection_teams]
            st.write(intersection_teams_str)

        #make a new df for drawing 
        df_inters = pd.DataFrame(intersection_teams_str, columns =['team_cats'])

        # which categories exist in at least one team
        result_st = [TEAMCAT_NAME_DICT.get(item, item) for item in result]
        result_st_selectable = [x for x in result_st if x not in intersection_teams_str]

        #make a new df for drawing 
        df_selectable = pd.DataFrame(result_st_selectable, columns =['team_cats'])

        #list to add categories that are already selected
        exclude = []
        # list for selected categories
        selected = []

        # for confirm button (to avoid direct display of matches)
        confirm = False

        # text to be printed on the pdfs
        text_match = "Match: "+ str(team_sel[0]) +" against " + str(team_sel[1]) +". Printed at " + str(datetime.now().strftime('%Y-%m-%d %H:%M'))

        #3 cases:   
        if len(intersection_teams) == MATCHES:
            # excat the same number
            # just display the the category and let team select the atlhtes

            st.write('- Exact the same categories')
            st.write('Nothing to do')
            selected = intersection_teams
            confirm = True

        elif len(intersection_teams) > MATCHES:
            # more options than MATCHES
            # remove categories
            st.write('More overlapping categories than individual fights')
            #check how many cats are to much:
            overhead_cat = len(intersection_teams) - MATCHES
            st.write('Remove ' +str(overhead_cat)+ ' categories')

            selected = intersection_teams
            
            if(overhead_cat // 2) != 0:

                text_remove = "- Please choose "+ str(overhead_cat // 2)+" categories to remove"
                st.write(text_remove)

                pdf_remove = PDF()
            
                for k, l in enumerate(team_sel): 
                    pdf_remove.add_page()
                    pdf_remove.alias_nb_pages()
                    pdf_remove.set_font("Arial", size = 15)
                    pdf_remove.cell(200, 10, txt = str(l), ln = 1, align = 'C')
                    pdf_remove.set_font("Arial", size = 12)
                    pdf_remove.cell(200, 6, txt = text_match, ln = 1, align = 'L')                                                 
                    pdf_remove.cell(200, 6, txt = text_remove, ln = 1, align = 'L')

                    pdf_remove.cell(200, 6, txt = "Enter 1,2,3,.. under selection", ln = 1, align = 'L')

                    fig_remove = draw_as_table_teamID(df_inters)
                    png_name = "remove.png"
                    fig_remove.write_image(png_name)
                    pdf_remove.image(png_name) 
                    pdf_remove.multi_cell(200, 6, txt = confirm_text(str(l),15), align = 'L')

                # save the pdf with name .pdf
                pdf_remove.output("dummy3.pdf")  
                with open("dummy3.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()    

                st.download_button(label="Download Remove lists",
                data=PDFbyte,
                file_name='Download Remove lists.pdf')    

            if(overhead_cat % 2) != 0: 
                st.write("- There will be a random choice between the categories")

            # remove always 2 categories
            while overhead_cat >= 2:
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

                overhead_cat = overhead_cat - 2

            if (overhead_cat % 2) != 0:
                # the number is odd
                if st.sidebar.button('Select Random Category to remove',
                                      help="press this button to choose random category to remove"):
                    # random choice from all leftover categories
                    result_over = [x for x in selected]
                    randcat = random.choice(result_over)
                    # display random cat
                    st.sidebar.markdown(f'<p style="background-color:#000000;border-radius:4%;">{TEAMCAT_NAME_DICT[randcat]}</p>', unsafe_allow_html=True)
                    selected.remove(randcat)
                    confirm = True
            else:
                # button to avoid immediate display of categories
                confirm = st.sidebar.button('Confirm Selection') 
                    
        elif len(intersection_teams_str) < MATCHES:
            # less options than MATCHES
            st.write('Less overlapping categories than individual fights')
            
            # check how many teams are missing:
            miss_cat = MATCHES - len(intersection_teams_str)            
            st.write('Add '+str(miss_cat)  +' categories')

            #add the overlapp to seleciton
            selected = intersection_teams

            # add the selected teams to the excluded list
            # (they can't be selected twice)
            exclude.append(intersection_teams_str)

            # add always 2 categories
            with st.expander("Selectable categories"):
                st.write("These categories exist in only one of the teams")
                st.write(result_st_selectable)

            if(miss_cat > len(result_st_selectable)):
                miss_cat = len(result_st_selectable) 
                st.error("There are not enough categories to choose from! Selectable categories are reduceed  to " + str(miss_cat), icon="🚨") 
                
            if(miss_cat // 2) != 0:
 
                text_add = "- Each team can choose "+ str(miss_cat // 2)+" categories to add"
                st.write(text_add)
                pdf_add = PDF()
            
                for k, l in enumerate(team_sel): 
                    pdf_add.add_page()
                    pdf_add.alias_nb_pages()
                    pdf_add.set_font("Arial", size = 15)
                    pdf_add.cell(200, 10, txt = str(l), ln = 1, align = 'C')
                    pdf_add.set_font("Arial", size = 12)
                    pdf_add.cell(200, 6, txt = text_match, ln = 1, align = 'L')
                    pdf_add.cell(200, 6, txt = "Those categories will happen", ln = 1, align = 'C')
                    fig_add_sel = draw_as_table_teamID(df_inters)
                    png_name = "add_sel.png"
                    fig_add_sel.write_image(png_name)
                    pdf_add.image(png_name) 
                    pdf_add.cell(200, 6, txt = "Please choose the categories to add", ln = 1, align = 'C')
                    pdf_add.cell(200, 6, txt = text_add, ln = 1, align = 'L')
                    pdf_add.cell(200, 6, txt = " ", ln = 1, align = 'L')
                    fig_add = draw_as_table_teamID(df_selectable)
                    png_name = "remove.png"
                    fig_add.write_image(png_name)
                    pdf_add.image(png_name) 
                    pdf_add.multi_cell(200, 6, txt = confirm_text(str(l),15), align = 'L')
                    if(miss_cat % 2) != 0: 
                        pdf_add.cell(200, 10, txt = "There will be a random choice between the categories", ln = 1, align = 'L')

                # save the pdf with name .pdf
                pdf_add.output("dummy4.pdf")  
                with open("dummy4.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()    

                st.download_button(label="Download Adding lists",
                data=PDFbyte,
                file_name='Download Adding lists.pdf')       



            if(miss_cat % 2) != 0: 
                st.write("- There will be a random choice between the categories")
            while miss_cat >= 2:
                
                tA = st.sidebar.selectbox('Choice Red',
                                          help="Choose category",
                                          options=[x for x in result_st_selectable if x not in exclude])
                # revese lookup of key
                selected.append(rev_look(tA, TEAMCAT_NAME_DICT))
                exclude.append(tA)

                tB = st.sidebar.selectbox('Choice Blue',
                                         help="Choose category",
                                         options=[x for x in result_st_selectable if x not in exclude])
                selected.append(rev_look(tB, TEAMCAT_NAME_DICT))
                exclude.append(tB)

                miss_cat = miss_cat - 2
                

            if (miss_cat % 2) != 0:
                # The remaining number is odd
                if st.sidebar.button('Select Random Category',
                                      help="press this button to choose random category"):
                    # random choice from all leftover categories
                    result_over = [x for x in result_st_selectable if x not in exclude]
                    randcat = random.choice(result_over)
                    # display random cat
                    st.sidebar.markdown(f'<p style="background-color:#000000;border-radius:4%;">{randcat}</p>', unsafe_allow_html=True)
                    # revese lookup of key
                    key = next(key for key, value in TEAMCAT_NAME_DICT.items() if value == randcat)
                    selected.append(key) 
                    confirm = True
            else:
                # button to avoid immediate display of categories
                confirm = st.sidebar.button('Confirm Selection')      
        else:
            st.error("You should never ever see this...", icon="🚨") 
                
        if((len(selected) == MATCHES) & (confirm == True)):
            st.header("Selected categories")
            for i in selected:
                st.write(TEAMCAT_NAME_DICT[i])

            pdf = PDF()
            for k, l in enumerate(team_sel): 
                pdf.add_page()
                pdf.alias_nb_pages()
                pdf.set_font("Arial", size = 15)
                pdf.cell(200, 10, txt = "Athlete selection " + str(l), ln = 1, align = 'C')
                pdf.set_font("Arial", size = 12)
                pdf.cell(200, 10, txt = text_match, ln = 1, align = 'L')
                                                 
                for i, j in enumerate(selected):
                    names = df_total[['name','cat_name']][(df_total['country_code'] == l) & (df_total['team_id'] == j)]
                    names2 = df_total[['name','cat_name']][(df_total['country_code'] == l) & (df_total['team_id'].isin(TEAMCAT_ALLOWED[j]))]

                    pdf.cell(200, 10, txt = TEAMCAT_NAME_DICT[j], ln = 2, align = 'C')

                    if(len(names)>0):
                        fig = draw_as_table(names)
                        png_name = str(TEAMCAT_NAME_DICT[j]) + str(l) + ".png"
                        fig.write_image(png_name)
                        pdf.image(png_name) 
                    if(len(names2)>0):
                        fig = draw_as_table(names2)
                        png_name = str(TEAMCAT_NAME_DICT[j]) + str(l) + "2.png"
                        fig.write_image(png_name)
                        pdf.image(png_name) 
                
                pdf.multi_cell(200, 6, txt = confirm_text(str(k),15), align = 'L')

            # save the pdf with name .pdf
            pdf.output("dummy.pdf")  
            with open("dummy.pdf", "rb") as pdf_file:
                PDFbyte = pdf_file.read()

            st.download_button(label="Download Team lists",
                            data=PDFbyte,
                            file_name='Download Teams.pdf')

st.sidebar.markdown('<a href="mailto:sportdirector@jjif.org">Contact for problems</a>', unsafe_allow_html=True)

LINK = '[Click here for the source code](https://github.com/ClaudiaBehnke86/TeamCompetition)'
st.markdown(LINK, unsafe_allow_html=True)

