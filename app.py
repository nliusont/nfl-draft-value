import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

st.set_page_config(page_title="Analyzing the contract values of NFL draft picks", layout="wide")
st.title("Analyzing the contract values of NFL draft picks")
st.subheader('if player contract values reflect player quality, do higher draft picks leader to better players?')
st.text('Data scraped from the following sources:')
st.write('[Pro Football Reference](%s)' % https://www.pro-football-reference.com/draft/)
st.write('[Over The Cap](%s)' % https://overthecap.com/contract-history)
st.write('[Spotrac](%s)' % https://www.spotrac.com/nfl/cba/)

### defs

def filter_df(df, year_selection, pos_selection):
    if pos_selection[0]=='All positions':
        pos_selection=positions
    criteria = (df['draft_year'] >= year_selection[0]) \
                    & (df['draft_year'] <= year_selection[1]) \
                    & (df['pos'].isin(pos_selection))
    new_df = df[criteria].copy()
    return new_df

### imports
df1 = pd.read_pickle('data/all_1_contracts.pkl')
df2 = pd.read_pickle('data/all_2_contracts.pkl')

### selectors
min_year = df1['draft_year'].min()
max_year = df1['draft_year'].max()
positions = list(np.sort(df1['pos'].unique()))
pos_list = ['All positions'] + positions



selected_pos = st.multiselect("select positions", 
                              options=pos_list,
                              default='QB'
                              )

selected_years = st.slider("select a range of draft years to look at", 
              value=[min_year, max_year],
              min_value=min_year, 
              max_value=max_year, 
              step=1)

### select dfs
select_df1 = filter_df(df1, selected_years, selected_pos)
select_df2 = filter_df(df2, selected_years, selected_pos)

### games by pick no
games_by_pick = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'g', 
        title='games played',
        scale=alt.Scale(domain=(0, select_df1['g'].max()))
        ),
    tooltip=['player', 'pos', 'g'],
    color=alt.Color('draft_year', scale=alt.Scale(scheme='darkblue'))
)

games_by_pick = games_by_pick.configure_legend(
    orient='left'
)

### games by second contract
games_by_second = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('gtd_norm', title='nornalized contract value'),
    y=alt.Y(
        'g', 
        title='games_played', 
        scale=alt.Scale(domain=(0, select_df2['g'].max()))
        ),
    tooltip=['player', 'pos', 'g'],
    color=alt.Color('draft_year', scale=alt.Scale(scheme='darkblue'))
)

### year one contracts
year_one_plot = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm', 
        title='normalized contract value',
        scale=alt.Scale(domain=(0, select_df2['gtd_norm'].max()))
        ),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=alt.Scale(scheme='darkblue'))
)

year_one_plot = year_one_plot.configure_legend(
    orient='left'
)

### year 2 contracts
year_two_plot = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm', 
        title='normalized contract value', 
        scale=alt.Scale(domain=(0, select_df2['gtd_norm'].max()))
        ),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=alt.Scale(scheme='darkblue'))
)



scatterplot = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y('contract_rank_scaled', scale=alt.Scale(reverse=True), title='relative contract value'),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm_scaled', format='.2f')]
)

### show
col1, col2= st.columns(2)

col1.subheader('games played by pick no.')
col1.altair_chart(games_by_pick, use_container_width=True, theme='streamlit')
col1.subheader('rookie contracts by pick no.')
col1.altair_chart(year_one_plot, use_container_width=True, theme='streamlit')
col2.subheader('games played by second contract value')
col2.altair_chart(games_by_second, use_container_width=True, theme='streamlit')
col2.subheader('second contracts by pick no.')
col2.altair_chart(year_two_plot, use_container_width=True, theme='streamlit')
