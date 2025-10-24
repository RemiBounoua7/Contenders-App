import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import base64
from nba_api.stats.endpoints import leaguedashteamstats
from nba_api.stats.static import teams

headers = {
    "Host": "stats.nba.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.nba.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

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

st.title("Contender Detector")
st.write('''Get a glimpse at which teams are well setup today to win the title. 
Below is a graph where teams are ranked based on their relative Offense and Defense. The more a team is to the right(/top), the best it is on offense(/defense). 
The golden quadrant is the zone in which teams should be if they want to win the title. Details on the methodology are to be found [here](%s).''' % url)

# Helper function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

TEAMS = teams.get_teams()
team_names= sorted([list(teams.get_teams()[i].values())[1] for i in range(len(TEAMS))])

# Map point IDs to image paths
image_folder = "NBA Team Logos/"  # Replace with your folder path
image_mapping = {
    team: f"data:image/png;base64,{encode_image_to_base64(f'{image_folder}{team}.png')}"
    for team in team_names
}


year=2026

selected_date = st.slider("Select a time interval and visualize how teams did in that span", 
                          min_value=datetime.datetime(2025,10,21), 
                          max_value= datetime.datetime(2026,4,15), 
                          value=(datetime.datetime(2025,10,21),
                                 datetime.datetime.today()))

# Fetch advanced stats for the year
try:
    team_advanced_stats = leaguedashteamstats.LeagueDashTeamStats(
    season=f"{year-1}-{str(year)[-2:]}",
    season_type_all_star="Regular Season",
    measure_type_detailed_defense='Advanced',
    date_from_nullable=selected_date[0].strftime("%m/%d/%Y"),
    date_to_nullable=selected_date[1].strftime("%m/%d/%Y"),
    league_id_nullable="00",
    timeout=30).get_data_frames()[0]
except Exception as e:
    st.error(f"Failed to fetch NBA data: {e}")
    st.stop()

normalized_off_rating = normalize_ratings(list(team_advanced_stats['OFF_RATING']),False)
normalized_def_rating = normalize_ratings(list(team_advanced_stats['DEF_RATING']),True)

Day_df = pd.DataFrame({
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
    #st.image(image_mapping[row['Team']])
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
    height=750,
    title=f"Contenders from {selected_date[0].day}/{selected_date[0].month}/{selected_date[0].year} to {selected_date[1].day}/{selected_date[1].month}/{selected_date[1].year}",
)
fig.add_annotation(x=.99, y=-0.035,
            text="@ZieseI",
            showarrow=False,
            yshift=10,
            font=dict(
                family="sans serif",
                size=15,
                color="#D3D5D7",
                )
            )
# Display plot
st.plotly_chart(fig)

twitter_url = "https://x.com/ZieseI"
st.write("Follow me on Twitter for more visualizations like this one. Link [here](%s)" % twitter_url)

#Prevent scroling to the top of the page. Deprecated method but nothing else works

st.experimental_set_query_params(slider=selected_date[0])
