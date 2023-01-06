import plotly
import plotly.express as px

import pandas as pd
import datetime as dt

class Plots():
    def distance_date(df):
        activity_df = df
        distance_date = pd.DataFrame()
        distance_date['distance'] = activity_df['distance']
        distance_date['days'] = [(d - dt.date(2022,1,1)).days for d in activity_df['start_date_local']]
        fig = px.scatter(distance_date, x='days', y='distance', labels={
                     "days": "Day of Year",
                     "distance": "Distance (km)"
                 }, title='Distance Ran vs Date')
        div = plotly.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return div
        


