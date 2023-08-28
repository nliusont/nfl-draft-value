import pandas as pd
import streamlit as st
import altair as alt
import numpy as np

st.set_page_config(page_title="NFL Contract Data", layout="wide")
st.title("Analyzing the contract values of NFL draft picks")
st.write('If player contract values reflect player quality, do higher draft picks lead to better players?')
st.text('These charts look at the guaranteed money in contracts normalized to the salary cap in the year the contract was signed. Use the filters to the left to explore the data.')


### defs

def filter_df(df, year_selection, pos_selection):
    if pos_selection[0]=='All positions':
        pos_selection=positions
    criteria = (df['draft_year'] >= year_selection[0]) \
                    & (df['draft_year'] <= year_selection[1]) \
                    & (df['pos'].isin(pos_selection))
    new_df = df[criteria].copy()
    new_df['draft_year'] = new_df['draft_year'].astype(int).astype(str)
    return new_df

### imports
df1 = pd.read_pickle('data/all_1_contracts.pkl')
df2 = pd.read_pickle('data/all_2_contracts.pkl')
df = pd.read_pickle('data/grouped_by_player_2000-2023.pkl')

### set colors
color_scheme = 'darkblue'
custom_color_scale = alt.Scale(scheme=color_scheme)

## SIDEBAR

### selectors sidebar
min_year = df1['draft_year'].min()
max_year = df1['draft_year'].max()
positions = list(np.sort(df1['pos'].unique()))
pos_list = ['All positions'] + positions

with st.sidebar:
    selected_pos = st.multiselect("select positions:", 
                                options=pos_list,
                                default='QB'
                                )

    selected_years = st.slider("select draft years:", 
                value=[min_year, max_year],
                min_value=min_year, 
                max_value=max_year, 
                step=1)
    
    # num players
    # drop values that aren't whole numbers since it means different players were grouped together
    df = df[df['draft_year'] % 1 ==0] 
    df = df[df['pick'] % 1 ==0]
    select_df = filter_df(df, selected_years, selected_pos)
    num_players = len(select_df)
    st.write(f'{num_players} players selected')
    
    ## sidebar legend
    ### get colors from color scheme
    years = list(range(selected_years[0], selected_years[1]+1))
    num_colors = len(years)
    year_color_mapping = pd.DataFrame({
        'year': [str(x) for x in years],
        'count': [1 for x in years]  # Example colors
    })

    # Create a color scale based on the color scheme
    custom_color_scale = alt.Scale(scheme=color_scheme)

    # Create an Altair chart using the color encoding
    chart = alt.Chart(year_color_mapping).mark_bar().encode(
        y='year',  # 'year' is used as both nominal and ordinal (discrete) axis
        x=alt.X('count', axis=alt.Axis(title=None, labels=False)),  # Sample count for demonstration
        color=alt.Color('year', scale=custom_color_scale)  # Use the defined color encoding
    )
    chart = chart.configure_legend(disable=True).properties(width=95)
    st.write('')
    st.altair_chart(chart, use_container_width=False)

### select dfs
select_df1 = filter_df(df1, selected_years, selected_pos)
select_df2 = filter_df(df2, selected_years, selected_pos)
#select_df occurs in sidebar


### games by pick no
games_by_pick = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'g', 
        title='games played',
        scale=alt.Scale(domain=(0, select_df1['g'].max()))
        ),
    tooltip=['player', 'pick', 'pos', 'g'],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

games_by_pick = games_by_pick.configure_legend(disable=True)

### total earnings by pick no.
total_earnings = alt.Chart(select_df).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm', 
        title='guaranteed money (normalized)'
        ),
    tooltip=['player', 'pick', 'pos', 'g'],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

total_earnings = total_earnings.configure_legend(
    orient='left',
    disable=True
)

### year one contracts
year_one_plot = alt.Chart(select_df1).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm', 
        title='guaranteed money (normalized)',
        scale=alt.Scale(domain=(0, select_df2['gtd_norm'].max()))
        ),
    tooltip=['player', 'draft_year', 'pick', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

year_one_plot = year_one_plot.configure_legend(
    orient='left',
    disable=True
)

### year 2 contracts
year_two_plot = alt.Chart(select_df2).mark_circle(size=75).encode(
    x=alt.X('pick', title='draft pick number'),
    y=alt.Y(
        'gtd_norm', 
        title='guaranteed money (normalized)', 
        scale=alt.Scale(domain=(0, select_df2['gtd_norm'].max()))
        ),
    tooltip=['player', 'draft_year', 'pick', 'pos', alt.Tooltip('gtd_norm', format='.2f')],
    color=alt.Color('draft_year', scale=custom_color_scale)
)

year_two_plot = year_two_plot.configure_legend(disable=True)

scatterplot = alt.Chart(select_df2).mark_circle(size=75).encode(
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

li = 'https://www.linkedin.com/in/nliusont/'
st.write('This dataset and streamlit app were developed \
         by [Nick Liu-Sontag](%s), a data scientist :nerd_face: in Brooklyn, NY' % li)

pfr = 'https://www.pro-football-reference.com/draft/'
otc = 'https://overthecap.com/contract-history'
sptrc = 'https://www.spotrac.com/nfl/cba/'
st.write('Sources: ')
st.write('[Pro Football Reference](%s)' % pfr)
st.write('[Over The Cap](%s)' % otc)
st.write('[Spotrac](%s)' % sptrc)



