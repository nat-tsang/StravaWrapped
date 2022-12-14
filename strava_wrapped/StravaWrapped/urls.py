from django.urls import path, include
from .views import * 
urlpatterns = [
    path('', base_map, name='Base Map View'),
    path('connected/', dashboard_view, name='Connect Map View'),
    path('oauth/', include('social_django.urls', namespace='social')),
]