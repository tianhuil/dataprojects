from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import ScalarFormatter
import pickle as pickle

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
                context_dict['string_prediction'] = repr(prediction)
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


def show_user_prediction(request,string_prediction):
    context = RequestContext(request)
    prediction = eval(string_prediction)
    unzipped_prediction = zip(*prediction)
    delay_bins = unzipped_prediction[0]
    delay_likelihood = np.array(unzipped_prediction[1])
    x_pos = np.arange(len(delay_bins))
    f = plt.figure()
    f.set_facecolor('none')
    ax = f.add_subplot(111)
    width = 1.0
    #ax.plot(delay_likelihood*100,delay_likelihood*100,ls='.',marker='o',mec='red',mfc='red',alpha=0.5)
    #print x_pos,delay_likelihood*100
    logbool = False
    if logbool:
        ax.set_yscale("log")
        ax.bar(x_pos,delay_likelihood*100.,width,color='red',alpha=0.5,log=True)
    else:
        ax.bar(x_pos,delay_likelihood*100.,width,color='red',alpha=0.5)
    ax.set_ylim(ax.get_ylim()[0],100)
    ax.set_title("Predicted Delay for Selected Itinerary")
    ax.set_ylabel("% Probability")
    ax.set_xlabel("Delay (minutes)")
    ax.set_xticks(x_pos+width/2.)
    ax.set_xticklabels(delay_bins)
    ax.yaxis.set_major_formatter(ScalarFormatter())
    
    # x = np.random.normal(loc=0,scale=1.0,size=100)
    # y = np.random.normal(loc=0,scale=1.0,size=100)
    # ax.plot(x,y,ls=".",marker="o",ms=2,mec='red',mfc='red',alpha=0.5)
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response,bbox_inches='tight')
    plt.close(f)
    return response
