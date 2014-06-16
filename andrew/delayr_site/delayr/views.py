from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from delayr.models import Airlinenames,FlightdelaysAprAfternoon

def index(request):
    context = RequestContext(request)

    #test = Airlinenames.objects.order_by('uniquecarrier')[:5]
    available_airlines = Airlinenames.objects.raw('''select distinct(airlinenames.uniquecarrier),airlinenames.fullname from airlinenames join flightdelays_apr_afternoon on flightdelays_apr_afternoon.uniquecarrier = airlinenames.uniquecarrier where year(flightdelays_apr_afternoon.flightdate) >= 2013''')
    available_airports = FlightdelaysAprAfternoon.objects.values('origin').distinct()
    context_dict = {'airlines':available_airlines,'airports':available_airports}
    
    return render_to_response('delayr/index.html',context_dict,context)

# Create your views here.
