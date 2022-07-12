'''

Create a mixed team compeition for TWG 2022 that allows the teams
to choose their categories and one random category is selected

'''
import random
import streamlit as st
import plotly.graph_objects as go


def calc_overlap(teama, teamb):
    '''
    Function to calc the overlap categories between the teams
    '''
    in_first = set(teama)
    in_second = set(teamb)

    in_second_but_not_in_first = in_second - in_first

    result_out = teama + list(in_second_but_not_in_first)

    return result_out


# some variables
teams = ['GER', 'FRA', 'NED', 'USA', 'UAE', 'ISR', 'THA', 'COL', 'MEX']

GER = ["1492", "14511", "1447", "1448", "1456", "1457", "1481"]
FRA = ["14511", "1447", "1453", "1456", "1457", "1475", "1483"]
NED = ["14511", "1447", "1448", "1455", "1456", "1457"]
THA = ["1492", "1453", "1455", "1456", "1481", "1484"]
USA = ["1475", "1476", "1477", "1483", "1484"]
ISR = ["1475", "1476", "1477", "1483", "1484"]
UAE = ["1475", "1476", "1477", "1481", "1484"]
COL = ["14511", "1453", "1477", "1453", "1483"]
MEX = ["14511", "1447", "1448", "1457"]

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
    "1447": "Adults Fighting Men -77 kg",
    "1448": "Adults Fighting Men -85 kg",
    # "1449": "Adults Fighting Men -94 kg",
    # "1450": "Adults Fighting Men +94 kg",
    # "1452": "Adults Fighting Women -45 kg",
    "1453": "Adults Fighting Women -48 kg",
    # "1454": "Adults Fighting Women -52 kg",
    "1455": "Adults Fighting Women -57 kg",
    "1456": "Adults Fighting Women -63 kg",
    "1457": "Adults Fighting Women -70 kg",
    # "1458": "Adults Fighting Women +70 kg",
    # "1473": "Adults Jiu-Jitsu Men -56 kg",
    # "1474": "Adults Jiu-Jitsu Men -62 kg",
    "1475": "Adults Jiu-Jitsu Men -69 kg",
    "1476": "Adults Jiu-Jitsu Men -77 kg",
    "1477": "Adults Jiu-Jitsu Men -85 kg",
    # "1478": "Adults Jiu-Jitsu Men -94 kg",
    # "1479": "Adults Jiu-Jitsu Men +94 kg",
    # "1480": "Adults Jiu-Jitsu Women -45 kg",
    "1481": "Adults Jiu-Jitsu Women -48 kg",
    # "1482": "Adults Jiu-Jitsu Women -52 kg",
    "1483": "Adults Jiu-Jitsu Women -57 kg",
    "1484": "Adults Jiu-Jitsu Women -63 kg",
    # "1485": "Adults Jiu-Jitsu Women -70 kg",
    # "1486": "Adults Jiu-Jitsu Women +70 kg",
    # "1494": "Adults Show Men",
    # "1495": "Adults Show Mixed",
    # "1493": "Adults Show Women"
    }

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
with st.expander("Shared categories"):
    st.write("These categories exist in at least one team")
    result_st = [key_map.get(item, item) for item in result]
    st.write(result_st)

# remove duo from selectable options for menue
exclude = ["Adults Duo Mixed"]

# choose the teams
tA_c1 = st.sidebar.selectbox('3. Team Red: Choice 1',
                             help="Choose the 1st category from the Red Team",
                             options=[x for x in result_st if x not in exclude])
# remove the choice from team one from selectable options
exclude.append(tA_c1)
tB_c1 = st.sidebar.selectbox('4. Team Blue: Choice 1',
                             help="Choose the 1st Category from the Blue Team",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tB_c1)
tA_c2 = st.sidebar.selectbox('3. Team Red: Choice 2',
                             help="Choose the 2nd category from the Red Team",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tA_c2)
tB_c2 = st.sidebar.selectbox('4. Team Blue: Choice 2',
                             help="Choose the 2nd category from the Blue Team",
                             options=[x for x in result_st if x not in exclude])
exclude.append(tB_c2)

# create some columns to display the choices

st.header("Selected categories")
st.write("Use left hand menue to select the categories per team")
sel1, sel2, sel3, sel4, sel5 = st.columns(5)
with sel1:
    st.markdown(f'<p style="background-color:#F31C2B;border-radius:2%;">{tA_c1}</p>', unsafe_allow_html=True)
with sel2:
    st.markdown(f'<p style="background-color:#F31C2B;border-radius:2%;">{tA_c2}</p>', unsafe_allow_html=True)
with sel4:
    st.markdown(f'<p style="background-color:#0090CE;border-radius:2%;">{tB_c1}</p>', unsafe_allow_html=True)
with sel5:
    st.markdown(f'<p style="background-color:#0090CE;border-radius:2%;">{tB_c2}</p>', unsafe_allow_html=True)

# now add the duo back in
exclude.remove("Adults Duo Mixed")

# variable with all remaining categoies
result_over = [x for x in result_st if x not in exclude]
with st.expander("Categories in random draw"):
    st.write("These categories exist in at least one team and were not selected")
    st.write(result_over)

# calculate probabilities
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


LINK = '[Click here for the source code](https://github.com/ClaudiaBehnke86/TeamCompetition)'
st.markdown(LINK, unsafe_allow_html=True)

if st.sidebar.button('Select Random Category',
                     help="press this button to choose random category"):
    # random choice from all leftover categories
    randcat = random.choice(result_over)
    with sel3:
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
