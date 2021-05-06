from config import *
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

# Style
st.markdown("""
<style>
.small-font {
    font-size:9px;
}
</style>
""", unsafe_allow_html=True)



st.title('NBA Fantasy Statistics')

st.markdown("""
This web application executes webscraping of NBA player statistics and 
transforms the data for easy viewing, analysis, and fantasy needs!\n
**Try it out below!**
""")

st.sidebar.header('Display Filters')
year = st.sidebar.selectbox('Year', list(reversed(range(2000,2022))))
fantasy = False
filtered_teams = False
scoring = False

cats = []
cats_weights = []

def truncate(x):
    end = str(int(x) % 100)
    if (int (x) > 1000):
        return (int(x) / 100)
    elif (int(x) > 100):
        return str(int(x) / 100)
    return '0.' + end

def truncy(x):
    x *= 1000
    if(x > 1000) :
        x = str(x)
        return float((x[:1]) + '.' + x[-2:])
    if(x > 100) :
        return x
        x = str(x)
        return float((x[0]) + '.' + x[-2:])
    x = str(x)
    return float((x[0]) + '.' + x[1:])

@st.cache
def load_teams():
    url = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations"
    html = pd.read_html(url, header = 0)
    data = html[0]['Abbreviation/Acronym'].tolist()
    data[1] = 'BRK'
    return data

filtered_positions = st.sidebar.multiselect('Positions', positions, default_pos)
filter_teams = st.sidebar.checkbox('Filter Teams?')
if(filter_teams) :
    filtered_teams = st.sidebar.multiselect('Teams', load_teams())

if(year >= 2020):
    fantasy = st.sidebar.checkbox('Fantasy')

st.sidebar.markdown('<p class="small-font">*Fantasy stats only available for the last 2 years</p>', unsafe_allow_html=True)


if(fantasy):
    scoring = st.sidebar.selectbox('Scoring Format', formats)
    cats = st.sidebar.multiselect('Categories', categories, default_fantasy)
    i = 0
    if(scoring == 'H2H') :
        for i in range(len(cats)):
            cats_weights.append(st.sidebar.number_input(cats[i] + ' point',None,None,0.0,.5,'%f'))
            if not cats_weights[i]:
                st.write("Please indicate the weight of the categories")
                st.stop()


@st.cache(allow_output_mutation=True)
def load_scrapped_data(year, fantasy, cats, positions, teams):
    url = "https://www.basketball-reference.com/leagues/NBA_" + str(year) + "_per_game.html"
    html = pd.read_html(url, header = 0)
    
    data = html[0]
    data = data.drop(data[data.Rk == 'Rk'].index).fillna(0)
    data = data.drop_duplicates(subset=['Player']).drop(['Rk'], axis=1)


    num_stat_start = data.columns.get_loc("G")
    for i in range(num_stat_start, len(data.columns)) :
        data.iloc[:,i] = data.iloc[:,i].apply(float)


    if (teams):
        data = data[data.Tm.isin(teams)]
    data = data[data.Pos.isin(positions)]

    if(fantasy[0]) :
        data = data.filter(['Player', 'Pos', 'Age', 'Tm'] + cats[0])
        if(fantasy[1] == 'H2H') :
            total = 0
            for i in range(len(cats[0])):
                total += (data[cats[0][i]].apply(float) * cats[1][i])
                data[cats[0][i]] = (data[cats[0][i]].map(float) * cats[1][i])
            data['FT_PTS'] = total
            data = data.sort_values(by = ['FT_PTS'], ascending = False, ignore_index=True)
        style_format = {cats[0][i]: '{:.2f}' for i in range(len(cats[0]))}
        return pd.DataFrame(data).style.format(style_format)
    
    data = data.reset_index(drop=True)
    return pd.DataFrame(data).style.format(categories_style_dict)

nbastats = load_scrapped_data(year, [fantasy, scoring], [cats, cats_weights], filtered_positions, filtered_teams)



st.write(nbastats)
