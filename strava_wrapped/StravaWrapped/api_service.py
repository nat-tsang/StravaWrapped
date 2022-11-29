from social_django.models import UserSocialAuth
import requests
import pandas as pd
from pandas.io.json import json_normalize
import polyline
import time

class API():
    def get_info():
        user = requests.user # Pulls in the Strava User data
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

        activities_df['start_date_local'] = pd.to_datetime(activities_df['start_date_local'])
        activities_df['start_date_local'] = activities_df['start_date_local'].dt.date
        activities_df['year'] = activities_df['start_date_local'].dt.year

        activities_df = activities_df[activities_df['year'] == '2022']

        activities_df['distance'] = activities_df['distance']/1000

        #convert time-distance to pace per km

        activities_df['avg_pace'] = activities_df['moving_time']/activities_df['distance']
        activities_df['avg_pace'] = time.strftime('%M:%S', time.gmtime(activities_df['avg_pace']))

        run_df = activities_df[activities_df['sport_type'] == 'Run']
        bike_df = activities_df[activities_df['sport_type'] == 'Ride']
        swim_df = activities_df[activities_df['sport_type'] == 'Swim']
        return run_df, bike_df, swim_df
    
    def stats(activities_df):
        stats_idx = pd.DataFrame(columns=['Longest Distance', 'Fastest Pace', 'Longest Moving Time', 'Most Kudos', 'Most Achievements'])
        stats_idx['Longest Distance'] = activities_df.index[max(activities_df['distance'])]
        stats_idx['Fastest Pace'] = activities_df.index[min(activities_df['avg_pace'])]
        stats_idx['Longest Moving Time'] = activities_df.index[max(activities_df['moving_time'])]
        stats_idx['Most Kudos'] = activities_df.index[max(activities_df['kudos_count'])]
        stats_idx['Most Achievements'] = activities_df.index[max(activities_df['achievement_count'])]

        return stats_idx