import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import base64

# Load CSV file
@st.cache_data
def load_todays_data():
    return pd.read_csv('Day_by_Day Ratings 2025.csv')
def load_historical_data():
    return pd.read_csv('1996-2024 team ratings.csv')

# Helper function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

url = "https://public.tableau.com/app/profile/r.mi.bounoua4636/viz/GoldenChampionshipZone/Dashboard2"

st.write("# Introduction")
st.write('''The NBA is a very competitive industry in which 30 teams give their all out on the court all year, with only one champion. At the start of each season, every team has a different objective, depending on their roster's strength. But how many can realistically target the Larry O'Brien trophy ?

We'll try and define a threshold beyong which teams have little to no chance of winning the title, based on previous NBA seasons, 1997 and onwards. Is it always the best regular season team that wins it all ? How 'bad' can you be and still have hope based on what happened in the past ? Also, what does it say about this year's teams ? Who are the *real* contenders ?

That's what we are trying to find out. You'll see, it's gonna be fun.''')

st.write("# Choosing measures and normalization process")
st.write('''To determine the strength of NBA teams during the regular season, we will take Offensive and Defensive ratings. Those are simple measures encapsulating how good/bad teams are on offense and defense, pretty straightforward. However, for year to year comparison stakes, we have to normalize our data, so here's a little explanation on the process and why we do it.
If you are already familiar with the concept, feel free to skip to the next section.

Offensive (Defensive) Ratings measure how much points a team scores (concedes) per 100 possessions.
What we want to get out of this is the relative strengths of teams, not the absolute number. It doesn't help you to know that the 1997 Bulls had a 112.4 Offensive Rating, you want to know whether it was good or not in 1997 ! What matters is this number in relation to every other teams' rating.

You might also be familiar with the fact that offensive ratings have skyrocketted in the last decade, due to multiple factors including but not limited to the 3 Point revolution. This fact alone prevents us from comparing eras on ratings, because a good defense in the 2020's would look like the worst defense in the 1990's numberwise.

That's where our normalization process comes in, to solve both problems at once. We want to transform all those ratings into a value, that helps us see which team was a good offense/defense in it's time. What we do is we take the year's ratings for all teams, and make them fit into a 0-1 range. The best offense will get a 1, the worst will get 0. Same for defense.
That way we can compare teams between eras on their relative dominance, and not raw numbers.''')

data = load_todays_data()
# Map point IDs to image paths
image_folder = "NBA Team Logos/"  # Replace with your folder path
image_mapping = {
    team: f"data:image/png;base64,{encode_image_to_base64(f'{image_folder}{team}.png')}"
    for team in data['Team'].unique()
}


fig1 = go.Figure()
# Add custom images for each point
for _, row in data[:-30].iterrows():
    #st.image(image_mapping[row['Team']])
    fig1.add_layout_image(
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


# Update axes and layout
fig1.update_layout(
    xaxis=dict(title="Normalized Offensive Rating",range=[-0.05, 1.05], showgrid=False, zeroline=False),
    yaxis=dict(title="Normalized Defensive Rating",range=[-0.05, 1.05], showgrid=False, zeroline=False),
    #width=250,
    height=700,
)


st.plotly_chart(fig1)

st.write("""There you have the 2024-25 teams ranked based on these principles. You can observe everything we talk about : how OKC is the best defense and Cleveland the best offense. How bad are the Wizards relative to everyone else.
The exact numbers aren't that important, it's the position in the graph and the relative gap between teams that matter. And just like we hypothesized, the best team are in the top right quadrant, with good defense and offense. """)
    

# Date slider
dates = pd.to_datetime(data['Date'].unique())

yearmin = dates.min().year
monthmin = dates.min().month
daymin = dates.min().day

yearmax = dates.max().year
monthmax = dates.max().month
daymax = dates.max().day


selected_date = st.slider("Select a Date", min_value=datetime.datetime(yearmin,monthmin,daymin), max_value= datetime.datetime(yearmax,monthmax,daymax ), value=datetime.datetime(yearmax,monthmax,daymax ))

# Filter data for selected date
filtered_data = data[pd.to_datetime(data['Date']) == selected_date]

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
    #width=250,
    height=700,
    title=f"Contenders on {selected_date.date()}",
)

# Display plot
st.plotly_chart(fig)
