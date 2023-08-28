import pandas as pd
import streamlit as st
import altair as alt

df = pd.read_pickle('data/all_2_contracts.pkl')
min_year = df['draft_year'].min()
max_year = df['draft_year'].max()

st.title("NFL player second contract value by draft pick number")
st.subheader("year")
selected_years = st.slider("select a range of draft years to look at", 
              value=[min_year, max_year],
              min_value=min_year, 
              max_value=max_year, 
              step=1)

year_criteria = (df['draft_year'] >= selected_years[0]) & (df['draft_year'] <= selected_years[1])
select_df = df[year_criteria].copy()

scatterplot = alt.Chart(select_df).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y('contract_rank_scaled', scale=alt.Scale(reverse=True), title='relative contract value'),
    tooltip=['player', 'pos', 'gtd_norm']
)

st.altair_chart(scatterplot, use_container_width=True, theme='streamlit')
