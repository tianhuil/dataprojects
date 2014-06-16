from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from delayr.models import Airlinenames,FlightdelaysAprAfternoon,Airports
from delayr.forms import AirportForm,AirlineForm

def index(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        airportform = AirportForm(request.POST)
        airlineform = AirlineForm(request.POST)
        if airportform.is_valid() and airlineform.is_valid():
            #print "SUCCESS"
            request.method = 'GET'
            return index(request)
        else:
            print airportform.errors
            print airlineform.errors
    else:
        airportform = AirportForm()
        airlineform = AirlineForm()
        #available_airlines = Airlinenames.objects.raw('''select distinct(airlinenames.uniquecarrier),airlinenames.fullname from airlinenames join flightdelays_apr_afternoon on flightdelays_apr_afternoon.uniquecarrier = airlinenames.uniquecarrier where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airlinenames.fullname''')
        #available_airports = Airports.objects.raw('''select distinct(airports.origin),airports.airportname from airports join flightdelays_apr_afternoon on flightdelays_apr_afternoon.origin = airports.origin where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airports.airportname''')
        #airportform.fields['airportname'].queryset = Airports.objects.all()
        context_dict = {'airportform':airportform,'airlineform':airlineform}
    
    return render_to_response('delayr/index.html',context_dict,context)

# def predict_model(request):
#     context = RequestContext(request)

#     if request.method == 'POST':
#         form = AirportForm(request.POST)
#         if form.is_valid():
#             return index(request)
#         else:
#             print form.errors
#     else:
#         form = AirportForm()

#     return render_to_response('delayr/predicted_delay.html',{'form':form},context)
        
