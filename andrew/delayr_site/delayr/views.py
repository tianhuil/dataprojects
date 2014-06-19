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
                prediction_dict = df.make_predictions(valuedict)
                if 'user_prediction' in prediction_dict.keys():
                    prediction_df = prediction_dict['user_prediction']
                    prediction_bins = list(prediction_df.columns)
                    prediction_values = list(prediction_df.irow(0))
                    prediction = zip(prediction_bins,prediction_values)
                    #context_dict['prediction'] = prediction
                    context_dict['string_prediction'] = repr(prediction)
                if 'all_time_prediction' in prediction_dict.keys():
                    context_dict['all_time_prediction'] = repr(prediction_dict['all_time_prediction'].to_json())
                if 'all_date_prediction' in prediction_dict.keys():
                    context_dict['all_date_prediction'] = repr(prediction_dict['all_date_prediction'].to_json())
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

# def model_output(request):
#     context = RequestContext(request)
#     if request.method == 'POST':
#         submittedform = AirportForm(request.POST)
#         if submittedform.is_valid():
#             #print dict(submittedform.data)
#             df.make_prediction(dict(submittedform.data))
#             return render_to_response('delayr/model_output.html',{},context)
#     request.method == 'GET'
#     return index(request)
#     context = RequestContext(request)

def show_all_date_prediction(request,prediction):
    print "zero"
    context = RequestContext(request)
    prediction_df = df.prep_passed_df(prediction,row_order_column='order',column_order_row='col_order')
    print "one"
    column_names = prediction_df.columns.values[1:]#Only plotting delays and cancellations
    print "two"
    row_names = prediction_df.index.values
    x_vals = np.arange(len(row_names))
    print "three"
    fig = plt.figure()
    fig.set_facecolor('none')
    ax = fig.add_subplot(111)
    print "four"
    colorlist = ['black','red','blue','green','orange','cyan','purple']
    colorcount = 0
    for i in range(len(column_names)):
        ax.plot(x_vals,prediction_df[column_names[i]]*100.,ls='-',marker='o',ms=5,color=colorlist[colorcount],mec=colorlist[colorcount],mfc=colorlist[colorcount],alpha=0.5,label=column_names[i],lw=3)
        colorcount += 1
        if colorcount == len(colorlist):
            colorcount = 0
    #fig.autofmt_xdate()
    ax.set_title("Delays on Nearby Days")
    ax.set_ylabel("Delay Probability (%)")
    ax.set_xlabel("Date")
    ax.set_xticks(x_vals)
    ax.set_xticklabels(row_names)
    ax.set_xlim(x_vals.min(),x_vals.max())
    ax.legend(loc='best',prop={'size':10})
    print "hello"

    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(fig)
    return response

def show_all_time_prediction(request,prediction):
    context = RequestContext(request)
    prediction_df = df.prep_passed_df(prediction,row_order_column='order',column_order_row='col_order')
    # prediction_df = pd.read_json(eval(prediction))
    # prediction_df = prediction_df.sort(columns='order')
    # prediction_df = prediction_df.T.sort(columns='col_order').T
    # column_names = prediction_df.columns.values[1:-1]#Only plotting delays and cancellations
    # prediction_df = prediction_df[:-1]#Remove col_order row
    column_names = prediction_df.columns.values[1:]#Only plotting delays and cancellations
    row_names = prediction_df.index.values
    x_vals = np.arange(len(row_names))
    # print column_names
    # print row_names
    # print prediction_df
    fig = plt.figure()
    fig.set_facecolor('none')
    ax = fig.add_subplot(111)
    colorlist = ['black','red','blue','green','orange','cyan','purple']
    colorcount = 0
    for i in range(len(column_names)):
        ax.plot(x_vals,prediction_df[column_names[i]]*100.,ls='-',marker='o',ms=5,color=colorlist[colorcount],mec=colorlist[colorcount],mfc=colorlist[colorcount],alpha=0.5,label=column_names[i],lw=3)
        colorcount += 1
        if colorcount == len(colorlist):
            colorcount = 0
    ax.set_title("Delays During the Day")
    ax.set_ylabel("Delay Probability (%)")
    ax.set_xlabel("Time of Day")
    ax.set_xticks(x_vals)
    ax.set_xticklabels(row_names)
    ax.set_xlim(x_vals.min(),x_vals.max())
    ax.legend(loc='best',prop={'size':10})

    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response,bbox_inches='tight')
    plt.close(fig)
    return response

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
    logbool = False
    if logbool:
        ax.set_yscale("log")
        ax.bar(x_pos,delay_likelihood*100.,width,color='red',alpha=0.5,log=True)
    else:
        ax.bar(x_pos,delay_likelihood*100.,width,color='red',alpha=0.5)
    ax.set_ylim(ax.get_ylim()[0],100)
    ax.set_title("Predicted Delay for Selected Itinerary")
    ax.set_ylabel("Probability (%)")
    ax.set_xlabel("Delay (minutes)")
    ax.set_xticks(x_pos+width/2.)
    ax.set_xticklabels(delay_bins)
    ax.yaxis.set_major_formatter(ScalarFormatter())
    
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response,bbox_inches='tight')
    plt.close(f)
    return response
