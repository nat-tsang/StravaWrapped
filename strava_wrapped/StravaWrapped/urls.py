from django.urls import re_path, include
from .views import * 
urlpatterns = [
    re_path('', base_map, name='Base Map View'),
    re_path('connected/', connected_map, name='Connect Map View'),
    re_path(r'^oauth/', include('social_django.urls', namespace='social')),
]