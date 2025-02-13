import datetime
from datetime import timedelta
from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
import time
from nba_api.stats.endpoints import leaguegamefinder
import os
from git import Repo


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

def daily_dates(start_date: str, end_date: str):
    #Prints all dates from start_date to end_date day by day.
    
    # Convert strings to datetime objects
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    # Initialize current date to start date and list
    current_date = start + timedelta(days=1)
    List=[]
    
    
    # Iterate over dates in bimonthly intervals
    while current_date <= end:
        List.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    # Print the overstepping date if it exists
    if current_date > end:
        List.append(current_date.strftime("%Y-%m-%d"))
    
    #Return the list
    return(List)

def get_regular_season_dates(year: int):
    
    # Query games from the given season
    gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=f"{year-1}-{str(year )[-2:]}", season_type_nullable="Regular Season")
    games = gamefinder.get_data_frames()[0]  # Get the data as a DataFrame
    
    # Extract game dates and convert to datetime
    game_dates = games['GAME_DATE'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
    
    # Find the earliest and latest dates
    start_date = game_dates.min()
    end_date = game_dates.max()
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')



year=2025

start_date, end_date = get_regular_season_dates(year)
Days = daily_dates(start_date, end_date)
team_names = leaguedashteamstats.LeagueDashTeamStats(season=f"{year-1}-{str(year)[-2:]}").get_data_frames()[0]['TEAM_NAME']

Final_df = pd.DataFrame({
"Date": [start_date],
"Team": None,   
"Normalized Offensive Rating":None,
"Normalized Defensive Rating": None
})
    
for i in range(1,len(Days)):
    day = Days[i]  

    # Fetch advanced stats for the year
    team_advanced_stats = leaguedashteamstats.LeagueDashTeamStats(
    date_from_nullable=start_date,
    date_to_nullable=day,
    season=f"{year-1}-{str(year)[-2:]}",
    season_type_all_star="Regular Season",
    measure_type_detailed_defense='Advanced'
    ).get_data_frames()[0]

    time.sleep(.5)       

    normalized_off_rating = normalize_ratings(list(team_advanced_stats['OFF_RATING']),False)
    normalized_def_rating = normalize_ratings(list(team_advanced_stats['DEF_RATING']),True)
    
    Day_df = pd.DataFrame({
        "Date":day,
        "Team":team_names,
        "Normalized Offensive Rating": normalized_off_rating,
        "Normalized Defensive Rating": normalized_def_rating
    })
    
    Final_df = pd.concat([Final_df,Day_df], ignore_index=True)

Final_df = Final_df.drop(0)
Final_df.to_csv("Day_by_Day Ratings 2025.csv")


# Path to your local repository
repo_path = ''
file_path = os.path.join(repo_path, 'Day_by_Day Ratings 2025.csv')
commit_message = 'Daily CSV update'

# Update the CSV file (already handled by your script)
# repo_path should point to the cloned repo directory
repo = Repo(repo_path)
repo.git.add(file_path)
repo.index.commit(commit_message)
origin = repo.remote(name='origin')
origin.push()