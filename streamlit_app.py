import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import base64
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams

def normalize_ratings(c1,defensive):
    
    #Takes a list, normalizes it and returns the normalized list
    
    
    Max_c1 = max(c1)
    Min_c1 = min(c1)

    n_c1 = []
    for i in c1:
                
        normalized_c1 = (i-Min_c1) / (Max_c1-Min_c1) if Max_c1!=Min_c1 else 0
        
        #If we are normalizing defensive winrate, reverse the values (so that best defenses get 1 instead of 0)
        if defensive:
            n_c1.append(1-normalized_c1)
        else:
            n_c1.append(normalized_c1)
    
    return n_c1

url = "https://remibounoua7.github.io/NBA-Championship-Corner/"

st.write("# Contender Detector")
st.write('''The idea behind this app is to get a glimpse at which teams are well setup today to win the title. 
Below is a graph where teams are ranked based on their relative Offense and Defense. The more a team is to the right(/top), the best it is on offense(/defense). 
The golden quadrant is the zone in which teams should be if they want to win the title. Details on the methodology are to be found [here](%s).''' % url)

# Helper function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

TEAMS = teams.get_teams()
team_names= sorted([list(teams.get_teams()[i].values())[1] for i in range(len(TEAMS))])
st.write(team_names)
# Map point IDs to image paths
image_folder = "NBA Team Logos/"  # Replace with your folder path
image_mapping = {
    team: f"data:image/png;base64,{encode_image_to_base64(f'{image_folder}{team}.png')}"
    for team in team_names
}


# Date slider
year=2025
today = datetime.date.today()
start_of_the_season = '2024-10-24'


yearmax = today.year
monthmax = today.month
daymax = today.day


selected_date = st.slider("Select a time interval and visualize how teams did in that span", min_value=datetime.datetime(2024,10,24), max_value= datetime.datetime(yearmax,monthmax,daymax ), value=(datetime.datetime(2024,10,24),datetime.datetime(yearmax,monthmax,daymax )))


team_names = leaguedashteamstats.LeagueDashTeamStats(season=f"{year-1}-{str(year)[-2:]}").get_data_frames()[0]['TEAM_NAME']

# Fetch advanced stats for the year
team_advanced_stats = leaguedashteamstats.LeagueDashTeamStats(
season=f"{year-1}-{str(year)[-2:]}",
season_type_all_star="Regular Season",
measure_type_detailed_defense='Advanced',
date_from_nullable=selected_date[0],
date_to_nullable=selected_date[1]
).get_data_frames()[0]


normalized_off_rating = normalize_ratings(list(team_advanced_stats['OFF_RATING']),False)
normalized_def_rating = normalize_ratings(list(team_advanced_stats['DEF_RATING']),True)

Day_df = pd.DataFrame({
    "Date":today,
    "Team":team_names,
    "Normalized Offensive Rating": normalized_off_rating,
    "Normalized Defensive Rating": normalized_def_rating
})




# Filter data for selected date
filtered_data = Day_df






# Create figure
fig = go.Figure()

# Add custom images for each point
for _, row in filtered_data.iterrows():
    st.image(image_mapping[row['Team']])
    fig.add_layout_image(
        dict(
            source=image_mapping[row['Team']],
            
            x=row['Normalized Offensive Rating'],  # N-ORTG
            y=row['Normalized Defensive Rating'],  # N-DRTG
            xref="x",
            yref="y",
            sizex=.11,
            sizey=.11,
            sizing="contain",
            xanchor="center",
            yanchor="middle",
            layer="above"
        )
    )

fig.add_shape(type="circle",
    xref="x", yref="y",
    fillcolor="Gold",
    x0=.48, y0=.48, x1=1.52, y1=1.52, opacity=.7,
    line_color="Orange",
    layer="below",
)

# Update axes and layout
fig.update_layout(
    xaxis=dict(title="Normalized Offensive Rating",range=[-0.05, 1.05], showgrid=False, zeroline=False),
    yaxis=dict(title="Normalized Defensive Rating",range=[-0.05, 1.05], showgrid=False, zeroline=False),
    width=500,
    height=600,
    title=f"Contenders from {selected_date[0]} to {selected_date[1]}",
)

# Display plot
st.plotly_chart(fig)

st.write("If you want to know more about the golden zone, the methodology is [right here](%s)" % url)
#Prevent scroling to the top of the page. Deprecated method but nothing else works
st.experimental_set_query_params(slider=selected_date[0])