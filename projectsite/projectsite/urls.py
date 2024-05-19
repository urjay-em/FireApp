from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity, fire_incidents_map, delete_location, IncidentList, IncidentCreateView, IncidentUpdateView, IncidentDeleteView
from fire import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('PieChart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('fire_incidents_map/', views.fire_incidents_map, name='fire_incidents_map'),
    path('database/', views.database_view, name='database'),
    path('delete/<int:location_id>/', delete_location, name='delete_location'),

    path('firestation_list', IncidentList.as_view(), name='firestation-list'),
    path('firestation_list/add', IncidentCreateView.as_view(), name='firestation-add'),
    path('firestation_list/<pk>', IncidentUpdateView.as_view(), name='firestation-update'),
    path('firestation_list/<pk>/delete', IncidentDeleteView.as_view(), name='firestation-delete'),

]