from plotly.offline import plot
import plotly.graph_objs as go

import pandas as pd
import datetime as dt

class Plots():
    def distance_date(df):
        df['days'] = [(d - dt.date(2022,1,1)).days for d in df['start_date_local']]
        fig = go.Figure()
        scatter = go.Scatter(x=df['days'], y=df['distance'], mode='markers',
                     opacity=0.8, marker_color='green')
        fig.update_layout(
            autosize=False,
            width=500,
            height=300,
            xaxis_title="Date (days)",
            yaxis_title="Distance (km)")
        fig.add_trace(scatter)
        div = plot(fig, output_type='div')
        return div
        


