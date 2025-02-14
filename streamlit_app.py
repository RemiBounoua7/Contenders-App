import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import base64
from  streamlit_vertical_slider import vertical_slider

# Load CSV file
@st.cache_data
def load_data():
    return pd.read_csv('Day_by_Day Ratings 2025.csv')

url = "https://remibounoua7.github.io/NBA-Championship-Corner/"

st.write("# Introduction")
st.write('''The NBA is a very competitive industry in which 30 teams give their all out on the court all year, with only one champion. At the start of each season, every team has a different objective, depending on their roster's strength. But how many can realistically target the Larry O'Brien trophy ?

We'll try and define a threshold beyong which teams have little to no chance of winning the title, based on previous NBA seasons, 1997 and onwards. Is it always the best regular season team that wins it all ? How 'bad' can you be and still have hope based on what happened in the past ? Also, what does it say about this year's teams ? Who are the *real* contenders ?

That's what we are trying to find out. You'll see, it's gonna be fun.''')


st.write("# Contender Detector")
st.write('''The idea behind this app is to get a glimpse at which teams are well setup today to win the title. 
Below is a graph where teams are ranked based on their relative Offense and Defense. The more a team is to the right(/top), the best it is on offense(/defense). 
The golden quadrant is the zone in which teams should be if they want to win the title. Details on the methodology are to be found [here](%s).''' % url)



data = load_data()
# Helper function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
# Map point IDs to image paths
image_folder = "NBA Team Logos/"  # Replace with your folder path
image_mapping = {
    team: f"data:image/png;base64,{encode_image_to_base64(f'{image_folder}{team}.png')}"
    for team in data['Team'].unique()
}
# Date slider
dates = pd.to_datetime(data['Date'].unique())

yearmin = dates.min().year
monthmin = dates.min().month
daymin = dates.min().day

yearmax = dates.max().year
monthmax = dates.max().month
daymax = dates.max().day


selected_date = st.slider("Select a Date", min_value=datetime.datetime(yearmin,monthmin,daymin), max_value= datetime.datetime(yearmax,monthmax,daymax ), value=datetime.datetime(yearmax,monthmax,daymax ))
vertical_slider(
    label = "% of the season",  #Optional
    key = "vert_01" ,
    height = 300, #Optional - Defaults to 300
    thumb_shape = "square", #Optional - Defaults to "circle"
    step = 1, #Optional - Defaults to 1
    default_value=5 ,#Optional - Defaults to 0
    min_value= 0, # Defaults to 0
    max_value= 100, # Defaults to 10
    value_always_visible = True ,#Optional - Defaults to False
)
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
