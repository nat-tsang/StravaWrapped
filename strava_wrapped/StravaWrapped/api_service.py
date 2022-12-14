from social_django.models import UserSocialAuth 
import pandas as pd
from pandas.io.json import json_normalize
import polyline
import time
import requests

class API():
    def get_info(user):
        strava_login = user.social_auth.get(provider='strava') # Strava login
        access_token = strava_login.extra_data['access_token'] # Strava Access token
        activites_url = "https://www.strava.com/api/v3/athlete/activities"

        # Get activity data
        header = {'Authorization': 'Bearer ' + str(access_token)}
        activity_df_list = []
        for n in range(5):  # Change this to be higher if you have more than 1000 activities
            param = {'per_page': 200, 'page': n + 1}

            activities_json = requests.get(activites_url, headers=header, params=param).json()
            if not activities_json:
                break
            activity_df_list.append(pd.json_normalize(activities_json))
        activities_df = pd.concat(activity_df_list)
        return activities_df

    def reduce_df(activities_df):
        columns = ['name', 'distance', 'moving_time', 'elapsed_time', 'start_date_local', 'sport_type', 'location_city', 'kudos_count', 
        'achievement_count', 'gear_id', 'average_speed', 'max_speed', 'max_heartrate', 'map.summary_polyline']
        activities_df = activities_df[columns]
        
        activities_df = activities_df.dropna(subset=['map.summary_polyline'])
        activities_df['polylines'] = activities_df['map.summary_polyline'].apply(polyline.decode)

        activities_df['start_date_local'] = pd.to_datetime(activities_df['start_date_local'], format='%Y-%m-%d %H:%M:%S')
        activities_df['start_date_local'] = activities_df['start_date_local'].dt.date
        activities_df['year'] = pd.DatetimeIndex(activities_df['start_date_local']).year

        activities_df = activities_df[activities_df['year'] == 2022]

        activities_df['distance'] = activities_df['distance']/1000

        #convert time-distance to pace per km

        activities_df['avg_pace'] = activities_df['moving_time']/activities_df['distance']
        new_pace = []
        for i in activities_df['avg_pace']:
            new_pace.append(float(time.strftime('%M.%S', time.gmtime(i))))
        activities_df['avg_pace'] = new_pace

        run_df = activities_df[activities_df['sport_type'] == 'Run'].reset_index(drop=True)
        bike_df = activities_df[activities_df['sport_type'] == 'Ride'].reset_index(drop=True)
        swim_df = activities_df[activities_df['sport_type'] == 'Swim'].reset_index(drop=True)
        return run_df, bike_df, swim_df
    
    def create_stats(run_df,bike_df,swim_df, stats):
        runMin_idx = run_df[['avg_pace']].idxmin()
        runMax_idx = run_df[['distance','moving_time','kudos_count','achievement_count','max_speed']].idxmax()
        bikeMin_idx = bike_df[['average_speed']].idxmin()
        bikeMax_idx = bike_df[['distance','moving_time','kudos_count','achievement_count','max_speed']].idxmax()
        swimMin_idx = swim_df[['avg_pace']].idxmin()
        swimMax_idx = swim_df[['distance','moving_time','kudos_count','achievement_count','max_speed']].idxmax()

        stats['longest_run'] = run_df.iloc[runMax_idx['distance']].to_dict() 
        stats['longest_bike'] = bike_df.iloc[bikeMax_idx['distance']].to_dict()
        stats['longest_swim'] = swim_df.iloc[swimMax_idx['distance']].to_dict()

        stats['fastest_run'] = run_df.iloc[runMin_idx['avg_pace']].to_dict()
        stats['fastest_bike'] = bike_df.iloc[bikeMin_idx['average_speed']].to_dict()
        stats['fastest_swim'] = swim_df.iloc[swimMin_idx['avg_pace']].to_dict()

        stats['moving_runTime'] = run_df.iloc[runMax_idx['moving_time']].to_dict()
        stats['moving_bikeTime'] = bike_df.iloc[bikeMax_idx['moving_time']].to_dict()
        stats['moving_swimTime'] = swim_df.iloc[swimMax_idx['moving_time']].to_dict()

        return stats