from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import requests
import folium
import polyline
from .api_service import *

def base_map(request):
    # Make your map object
    # main_map = folium.Map(location=[43.45, -80.476], zoom_start = 12) # Create base map
    # main_map_html = main_map._repr_html_() # Get HTML for website

    # context = {
    #     "main_map":main_map_html
    # }
    return render(request, 'connected.html')

def connected_overview(request):
    api_service = API
    user = request.user
    activities_df = api_service.get_info(user)
    run_df, bike_df, swim_df = api_service.reduce_df(activities_df)

    #run info
    stats_idx = api_service.stats(run_df)

    #bike info
    stats_idx = api_service.stats(bike_df)

    #swim info
    stats_idx = api_service.stats(swim_df)

def connected_map(request):
    # Make your map object
    main_map = folium.Map(location=[43.45, -80.476], zoom_start = 12) # Create base map
    user = request.user # Pulls in the Strava User data
    api_service = API
    activities_df = api_service.get_info(user)
    activities_df = activities_df.dropna(subset=['map.summary_polyline'])
    activities_df['polylines'] = activities_df['map.summary_polyline'].apply(polyline.decode)

    # Plot Polylines onto Folium Map
    for pl in activities_df['polylines']:
        if len(pl) >= 1: 
            folium.PolyLine(locations=pl, color='red').add_to(main_map)

    # Return HTML version of map
    main_map_html = main_map._repr_html_() # Get HTML for website
    context = {
        "main_map":main_map_html
    }
    return render(request, 'index.html', context)