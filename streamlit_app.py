import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import base64

# Load CSV file
@st.cache_data
def load_data():
    return pd.read_csv('Day_by_Day Ratings 2025.csv')

url = "https://remibounoua7.github.io/NBA-Championship-Corner/"

st.write("# Introduction")
st.write('''This app aims at finding out which teams are contenders for the title at a certain date. It encapsulates team's ratings in Offense and Defense, and maps them onto a grid.
The threshold for contender status and the methodology used to define it are to be found [here](%s)''' % url)
st.write("I would advise you to read that page and get familiar with the concept of the contender zone before playing with this app.")


st.write("Now that you are familiar with the concept, you can select a date in the 2024-25 season and see which teams were in the contender zone. You can play with the slider and notice slumps in performances, good weeks, players getting hurt, players coming back ... The floor is yours.")



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


selected_date = st.slider("Select a Date", min_value=datetime.datetime(yearmin,monthmin,daymin), max_value= datetime.datetime(yearmax,monthmax,daymax ), value=datetime.datetime(yearmax,monthmax,daymax ), scrollTo=False)

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
    #title=f"Contenders on {selected_date.date()}",
)

# Display plot
st.plotly_chart(fig,use_container_width=True,config={'displayModeBar': False})