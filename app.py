import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

st.set_page_config(page_title="NFL Contract Data", layout="wide")
st.title("Analyzing the contract values of NFL draft picks")
st.write('If player contract values reflect player quality, do higher draft picks lead to better players?')
st.write('These charts look at the guaranteed money in contracts normalized to the salary cap in the year the contract was signed. Use the filters to the left to explore the data.')


### defs
max_pick = 262

def filter_df(df, year_selection, filter_year_on, pos_selection, team_selection, filter_team_on, max_pick=max_pick):
    if ('All positions' in pos_selection) or len(pos_selection)==0:
        pos_selection=positions
    if ('All teams' in team_selection) or len(team_selection)==0:
        team_selection=teams
    criteria = (df[filter_year_on] >= year_selection[0]) \
                    & (df[filter_year_on] <= year_selection[1]) \
                    & (df['pos'].isin(pos_selection)) \
                    & (df[filter_team_on].isin(team_selection))
    new_df = df[criteria].copy()
    new_df = new_df[new_df['pick']<max_pick]
    new_df[filter_year_on] = new_df[filter_year_on].astype(int).astype(str)
    return new_df

### imports
df1 = pd.read_pickle('data/all_1_contracts.pkl')
df2 = pd.read_pickle('data/all_2_contracts.pkl')
df = pd.read_pickle('data/all_contracts_2000-2023.pkl')

### set colors
color_scheme = 'darkblue'
custom_color_scale = alt.Scale(scheme=color_scheme)

## SIDEBAR

### selectors sidebar
min_year = df1['draft_year'].min()
max_year = df1['draft_year'].max()
positions = list(np.sort(df['pos'].unique()))
pos_list = ['All positions'] + positions

teams = list(np.sort(df['signing_tm'].unique()))
team_list = ['All teams'] + teams

with st.sidebar:
    selected_pos = st.multiselect("select positions:", 
                                options=pos_list,
                                default='All positions'
                                )
    
    selected_tms = st.multiselect("select teams:", 
                                options=team_list,
                                default='All teams'
                                )

    selected_years = st.slider("select years:", 
                value=[min_year, max_year],
                min_value=min_year, 
                max_value=max_year, 
                step=1)

    # select df
    # drop values that aren't whole numbers since it means different players were grouped together
    df = df[df['draft_year'] % 1 ==0] 
    df = df[df['pick'] % 1 ==0]
    select_df = filter_df(df, selected_years, 'year_signed', selected_pos, selected_tms, 'signing_tm')
    select_df1 = filter_df(df1, selected_years, 'draft_year', selected_pos, selected_tms, 'tm')
    select_df2 = filter_df(df2, selected_years, 'year_signed', selected_pos, selected_tms, 'signing_tm')

    # num players
    num_players = len(set(select_df['player'].to_list()+select_df1['player'].to_list()+select_df2['player'].to_list()))
    st.write(f'{num_players} players selected')
    
    ## sidebar legend
    ### get colors from color scheme
    years = list(range(selected_years[0], selected_years[1]+1))
    num_colors = len(years)
    year_color_mapping = pd.DataFrame({
        'year': [str(x) for x in years],
        'count': [1 for x in years]
    })

    # Create a color scale based on the color scheme
    custom_color_scale = alt.Scale(scheme=color_scheme)

    # Create an Altair chart using the color encoding
    chart = alt.Chart(year_color_mapping).mark_bar().encode(
        y='year',
        x=alt.X('count', axis=alt.Axis(title=None, labels=False)),
        color=alt.Color('year', scale=custom_color_scale)
    )
    chart = chart.configure_legend(disable=True).properties(width=95)
    st.write('')
    st.altair_chart(chart, use_container_width=False)

# set max y axis for first contract and second contract charts so they are synced
max_gtd1 = select_df1['gtd_norm'].max()
max_gtd2 = select_df2['gtd_norm'].max()
max_gtd = np.max([max_gtd1, max_gtd2])

### games by pick no
games_by_pick = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', 
            title='draft pick number',
            scale=alt.Scale(domain=(0, max_pick))
        ),
    y=alt.Y(
        'g', 
        title='games played'
        ),
    tooltip=['player', 'draft_year', 'pick', 'pos', 'g'],
    color=alt.Color('draft_year', scale=custom_color_scale)
)
games_by_pick = games_by_pick.configure_legend(disable=True)
games_by_pick = games_by_pick.configure_axisY(orient='right')

### total earnings by pick no.
total_earnings = alt.Chart(select_df).mark_circle(size=100).encode(
    x=alt.X('pick', 
            title='draft pick number',
            scale=alt.Scale(domain=(0, max_pick))
        ),
    y=alt.Y(
        'gtd_norm_sum', 
        title='guaranteed money (normalized)'
        ),
    tooltip=['player', 'draft_year', 'pick', 'pos', 'g'],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

total_earnings = total_earnings.configure_legend(
    orient='left',
    disable=True
)

### year one contracts
year_one_plot = alt.Chart(select_df1).mark_circle(size=100).encode(
    x=alt.X('pick', 
            title='draft pick number',
            scale=alt.Scale(domain=(0, max_pick))
        ),
    y=alt.Y(
        'gtd_norm', 
        title='guaranteed money (normalized)',
        scale=alt.Scale(domain=(0, max_gtd))
        ),
    tooltip=['player', 'tm', 'draft_year', 'pick', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

year_one_plot = year_one_plot.configure_legend(
    orient='left',
    disable=True
)

### year 2 contracts
year_two_plot = alt.Chart(select_df2).mark_circle(size=100).encode(
    x=alt.X('pick', 
            title='draft pick number',
            scale=alt.Scale(domain=(0, max_pick))
            ),
    y=alt.Y(
        'gtd_norm', 
        title='guaranteed money (normalized)', 
        scale=alt.Scale(domain=(0, max_gtd))
        ),
    tooltip=['player', 'signing_tm', 'year_signed', 'pick', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=custom_color_scale)
)
year_two_plot = year_two_plot.configure_legend(disable=True)
year_two_plot = year_two_plot.configure_axisY(orient='right')

scatterplot = alt.Chart(select_df2).mark_circle(size=100).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y('contract_rank_scaled', scale=alt.Scale(reverse=True), title='relative contract value'),
    tooltip=['player', 'draft_year', 'pos', alt.Tooltip('gtd_norm_scaled', format='.2f')]
)

### show
col1, col2= st.columns(2)

col1.markdown("<h4 style='text-align: center;'>rookie contracts</h4>", unsafe_allow_html=True)
col1.altair_chart(year_one_plot, use_container_width=True, theme='streamlit')
col1.markdown("<h4 style='text-align: center;'>total guaranteed money</h4>", unsafe_allow_html=True)
col1.altair_chart(total_earnings, use_container_width=True, theme='streamlit')
col2.markdown("<h4 style='text-align: center;'>second contracts</h4>", unsafe_allow_html=True)
col2.altair_chart(year_two_plot, use_container_width=True, theme='streamlit')
col2.markdown("<h4 style='text-align: center;'>games played</h4>", unsafe_allow_html=True)
col2.altair_chart(games_by_pick, use_container_width=True, theme='streamlit')

# footer
kg = 'https://www.kaggle.com/datasets/nicholasliusontag/nfl-contract-and-draft-data'
st.write('This dataset is available on [kaggle](%s)' % kg)

li = 'https://www.nls.website'
st.write('This dataset and streamlit app were developed \
         by [Nick Liu-Sontag](%s), a data scientist :nerd_face: in Brooklyn, NY' % li)

pfr = 'https://www.pro-football-reference.com/draft/'
otc = 'https://overthecap.com/contract-history'
sptrc = 'https://www.spotrac.com/nfl/cba/'
st.write('Sources: ')
st.write('[Pro Football Reference](%s)' % pfr)
st.write('[Over The Cap](%s)' % otc)
st.write('[Spotrac](%s)' % sptrc)



