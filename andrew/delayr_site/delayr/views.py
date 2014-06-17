from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from delayr.models import Airlinenames,FlightdelaysAprAfternoon,Airports
from delayr.forms import AirportForm,AirlineForm,DateTimeForm

def test(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('delayr/test.html',context_dict,context)

def index(request):
    context = RequestContext(request)
    context_dict = {}

    if request.method == 'POST':
        submittedform = AirportForm(request.POST)
        if submittedform.is_valid():
            print dict(submittedform.data)
            request.method = 'GET'
            return index(request)
        else:
            print submittedform.errors
    else:
        airportform = AirportForm()
        airlineform = AirlineForm()
        datetimeform = DateTimeForm()
        context_dict = {'airportform':airportform,'airlineform':airlineform,'datetimeform':datetimeform}
    
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
        
