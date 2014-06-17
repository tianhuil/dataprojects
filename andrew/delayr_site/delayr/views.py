from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import pandas as pd

from delayr.models import Airlinenames,FlightdelaysAprAfternoon,Airports
from delayr.forms import AirportForm,AirlineForm,DateTimeForm

import delayr_funcs as df

def test(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('delayr/test.html',context_dict,context)

def index(request):
    context = RequestContext(request)
    context_dict = {}
    airportform = AirportForm()
    airlineform = AirlineForm()
    datetimeform = DateTimeForm()
    
    if request.method == 'POST':
        #return model_output(request)
        submittedform = AirportForm(request.POST)
        if submittedform.is_valid():
            valuedict = dict(submittedform.data)
            if valuedict['origin'][0] == valuedict['dest'][0]:
                context_dict['welcome_message'] = "Welcome to Delayr!"
                context_dict['errmessage'] = "Choose two different airports"
            else:
                prediction_dict = df.make_prediction(valuedict)
                prediction_df = prediction_dict['user_prediction']
                prediction_bins = list(prediction_df.columns)
                prediction_values = list(prediction_df.irow(0))
                prediction = zip(prediction_bins,prediction_values)
                context_dict['prediction'] = prediction
            #airlineform = AirlineForm(initial={'uniquecarrier':valuedict['uniquecarrier']})
            #print 'test',airlineform.fields['uniquecarrier'].initial
            print valuedict['uniquecarrier']
            airlineform.fields['uniquecarrier'].initial = valuedict['uniquecarrier'][0]
            airportform.fields['origin'].initial = valuedict['origin'][0]
            airportform.fields['dest'].initial = valuedict['dest'][0]
            datetimeform.fields['date'].initial = valuedict['date'][0]
            datetimeform.fields['time'].initial = valuedict['time'][0]
            #print 'test',airlineform.fields['uniquecarrier'].initial
        else:
            print submittedform.errors
            context_dict['errmessage'] = "You've somehow made an error entering your flight info. Please try again"
    else:
        context_dict['welcome_message'] = "Welcome to Delayr!"
    
    context_dict['airportform'] = airportform
    context_dict['airlineform'] = airlineform
    context_dict['datetimeform'] = datetimeform
    
    return render_to_response('delayr/index.html',context_dict,context)

def model_output(request):
    context = RequestContext(request)
    if request.method == 'POST':
        submittedform = AirportForm(request.POST)
        if submittedform.is_valid():
            #print dict(submittedform.data)
            df.make_prediction(dict(submittedform.data))
            return render_to_response('delayr/model_output.html',{},context)
    request.method == 'GET'
    return index(request)
    context = RequestContext(request)

