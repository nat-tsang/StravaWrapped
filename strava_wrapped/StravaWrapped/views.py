from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import pandas as pd
from json import dumps
import requests
import folium
import polyline
from .api_service import *
from .plots import *
from django.views.generic import TemplateView

def base_map(request):
    dict = [{"distance":18.0295,"days":364},{"distance":6.4684,"days":362}]
    plot_service = Plots
    plot_data = plot_service.distance_date(dict)
    context = {'plot_data':plot_data}
    return render(request, 'connected.html', context)

def connected_overview(request):
    api_service = API
    user = request.user
    activities_df = api_service.get_info(user)
    run_df, bike_df, swim_df = api_service.reduce_df(activities_df)
    stats = { }

    #run info
    stats_dict = api_service.create_stats(run_df,bike_df,swim_df,stats)
    context = stats_dict
    return stats_dict

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
    context2 = {
        "main_map":main_map_html
    }
    return main_map_html

def connected_plot(request):
    api_service = API
    user = request.user
    activities_df = api_service.get_info(user)
    run_df, bike_df, swim_df = api_service.reduce_df(activities_df)
    plot_service = Plots
    plot_data = plot_service.distance_date(run_df)
    return plot_data

def dashboard_view(request):
    dump1 = connected_overview(request)  
    dump2 = connected_map(request)  
    dump3 = connected_plot(request)
    context = {'stats': dump1, 'main_map': dump2, 'plot_view': dump3}
    return render(request, 'index.html', context)