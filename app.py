import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

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


st.title("Analyzing the contract values of NFL draft picks")
selected_pos = st.multiselect("select positions", 
                              options=pos_list,
                              default='QB'
                              )
st.subheader("year")
selected_years = st.slider("select a range of draft years to look at", 
              value=[min_year, max_year],
              min_value=min_year, 
              max_value=max_year, 
              step=1)



### year one contracts
select_df1 = filter_df(df1, selected_years, selected_pos)

year_one_plot = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y('gtd_norm_scaled', title='normalized contract value'),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm_scaled', format='.2f')]
)


### year 2 contracts
select_df2 = filter_df(df2, selected_years, selected_pos)

year_two_plot = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm_scaled', 
        title='normalized contract value', 
        scale=alt.Scale(domain=(0, 1))),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm_scaled', format='.2f')]
)

scatterplot = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y('contract_rank_scaled', scale=alt.Scale(reverse=True), title='relative contract value'),
    tooltip=['player', 'pos', alt.Tooltip('gtd_norm_scaled', format='.2f')]
)

### show

st.altair_chart(year_one_plot, use_container_width=True, theme='streamlit')
st.altair_chart(year_two_plot, use_container_width=True, theme='streamlit')
