from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity, fire_incidents_map, delete_location, IncidentList, IncidentCreateView, IncidentUpdateView, IncidentDeleteView, IncidentRecords, IncidentListView, firelocationListView, stationListView, firefighterListView, firetruckListView, weatherListView
from fire import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('ChartJs', ChartView.as_view(), name='ChartJs'),
    path('PieChart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('fire_incidents_map/', views.fire_incidents_map, name='fire_incidents_map'),
    path('IncidentRecords/', IncidentListView.as_view(), name='Int-record'),
    path('firelocations/', firelocationListView.as_view(), name='fire-location'),
    path('firestation/', stationListView.as_view(), name='fire-station'),
    path('firefighters/', firefighterListView.as_view(), name='fire-fighters'),
    path('firetrucks/', firetruckListView.as_view(), name='fire-truck'),
    path('weathers/', weatherListView.as_view(), name='weather-condition'),
    


  
 

    

]