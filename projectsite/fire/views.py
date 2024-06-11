from django.forms import CharField
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation, Firefighters, FireTruck, WeatherConditions

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fire.forms import IncidentForm, FireStationForm, LocationsForm, FirefightersForm

from django.urls import reverse_lazy

from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime
from django.core.paginator import Paginator

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


def delete_location(request, location_id):
    # Fetch the location object
    location = get_object_or_404(Locations, id=location_id)
    
    if request.method == 'POST':
        # If form is submitted, delete the location
        location.delete()
        return redirect('database')  # Redirect to database page after deletion
    
    return render(request, 'del_location.html', {'location': location})


class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass


def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level;
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def LineCountbyMonth(request):

    current_year = datetime.now().year

    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)

    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)


def map_station(request):
     fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

     for fs in fireStations:
         fs['latitude'] = float(fs['latitude'])
         fs['longitude'] = float(fs['longitude'])

     fireStations_list = list(fireStations)

     context = {
         'fireStations': fireStations_list,
     }

     return render(request, 'map_station.html', context)


def fire_incidents_map(request):
    locations_with_incidents = Locations.objects.annotate(
        num_incidents=Count('incident')
    ).values(
        'id', 'name', 'latitude', 'longitude', 'city', 'num_incidents'
    )

    # Convert latitude and longitude to float
    for location in locations_with_incidents:
        location['latitude'] = float(location['latitude'])
        location['longitude'] = float(location['longitude'])

    context = {
        'locations': list(locations_with_incidents),
    }

    return render(request, 'fire_incidents_map.html', context)


def database_view(request):
    # Querying all locations and incidents from the database
    locations = Locations.objects.all()
    incidents = Incident.objects.all()
    
    # Passing data to the template for rendering
    context = {
        'locations': locations,
        'incidents': incidents,
    }
    return render(request, 'IncidentRecords.html', context)

def IncidentRecords(request):
    # Fetch all incidents from the database
    incidents = Incident.objects.all()

    # Pass the incidents to the template
    context = {
        'incidents': incidents
    }

    return render(request, 'IncidentRecords.html', context)

class IncidentListView(ListView):
    model = Incident
    template_name = 'IncidentRecords.html'  # Update with your template path
    context_object_name = 'incidents'  # Specify the context variable name to use in the template
    paginate_by = 10


class IncidentList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = 'firestation/firestation_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(IncidentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
                        Q (address__icontains=query) |
                        Q (city__icontains=query) |
                        Q (country__icontains=query))
        return qs


class IncidentCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_add.html'
    success_url = reverse_lazy('firestation-list')


class IncidentUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_edit.html'
    success_url = reverse_lazy('firestation-list')


class IncidentDeleteView(DeleteView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_del.html'
    success_url = reverse_lazy('firestation-list')
    
class firelocationListView(ListView):
    model = Locations
    form_class = LocationsForm
    template_name = 'firelocation.html'
    success_url = reverse_lazy('fire-location')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        locations = context['object_list']  # Paginated queryset
        context['locations'] = locations
        print(locations)  # Print paginated queryset to console
        return context
    
class stationListView(ListView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'station_record.html'
    context_object_name = 'firestations'
    success_url = reverse_lazy('fire-station')
    paginate_by = 10
    
    def get_queryset(self):
        # Customize queryset if needed, e.g., ordering
        queryset = FireStation.objects.all().order_by('name')  # Example: ordering by name
        return queryset
    
class firefighterListView(ListView):
    model = Firefighters
    template_name = 'fire_fighter.html'
    context_object_name = 'firefighters'
    success_url = reverse_lazy('fire-fighters')
    paginate_by = 10
    
    
class firetruckListView(ListView):
    model = FireTruck
    template_name = 'fire_truck.html'
    context_object_name = 'FireTrucks'
    success_url = reverse_lazy('fire-trucks')
    paginate_by = 10
    
class weatherListView(ListView):
    model = WeatherConditions
    template_name = 'wheather_condition.html'
    context_object_name = 'weathers'
    success_url = reverse_lazy('weather-condition')
    paginate_by = 10
