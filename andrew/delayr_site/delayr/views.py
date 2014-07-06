from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

import pandas as pd
import numpy as np
import re
import os
import glob
import cPickle as pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import ScalarFormatter
import pickle as pickle

from delayr.models import Airlinenames,FlightdelaysAprAfternoon,Airports
from delayr.forms import AirportForm,AirlineForm,DateTimeForm

import delayr_funcs as df

#Some plotting options I want to be consistent for all plots, so they're defined with a more global scope:
pd.options.display.mpl_style = 'default'
colorlist = ['#8da0cb','#66c2a5','#fc8d62','#e78ac3','#a6d854','#ffd92f','#e5c494','#b3b3b3']
titlesize = 24
axlabelsize = 20
ticklabelsize = 20
legendsize = 18
fontname = 'Times New Roman Bold'
figsize = (8,6.5)

#Can I preload all my pickled models here, and save runtime later?
def load_pickles(pickle_dict):
    projectdir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))#the main project directory
    pkl_directory = os.path.join(projectdir,'saved_models/')
    picklenames = glob.glob(pkl_directory+"*.pkl")
    for name in picklenames:
        f = open(name,'rb')
        pickle_dict[name] = pickle.load(f)
        f.close()
pickle_dict = {}
load_pickles(pickle_dict)
print pickle_dict[pickle_dict.keys()[0]]

#Simple test view, for trying out new things:
def test(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('delayr/test.html',context_dict,context)

def nitty_gritty(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('delayr/nitty_gritty.html',context_dict,context)

#The about page:
def about(request):
    context = RequestContext(request)
    context_dict = {}
    return render_to_response('delayr/about.html',context_dict,context)

#The index is both the homepage of Delayr and also where results are posted to, so it's naturally a lot more complex than the above functions:
def index(request):
    context = RequestContext(request)
    context_dict = {}
    #Initialize the forms
    airportform = AirportForm()
    airlineform = AirlineForm()
    datetimeform = DateTimeForm()

    #If the user submitted a search, do stuff:
    if request.method == 'POST':
        #return model_output(request)
        submittedform = AirportForm(request.POST)
        if submittedform.is_valid():
            #Get the data, validate the date field (since somehow the widget I'm using isn't doing that part):
            valuedict = dict(submittedform.data)
            date_regexp = re.compile(r'^\d\d/\d\d/\d\d\d\d$')
            if valuedict['origin'][0] == valuedict['dest'][0]:
                context_dict['welcome_message'] = "Welcome to Delayr!"
                context_dict['errmessage'] = "Choose two different airports"
            elif date_regexp.search(valuedict['date'][0]) == None:
                context_dict['welcome_message'] = "Welcome to Delayr!"
                context_dict['errmessage'] = "Incorrect date format"
            else:
                #Display the prediction results:
                prediction_dict = df.make_predictions(valuedict)
                #prepare values relating to the requested prediction
                if 'user_prediction' in prediction_dict.keys():
                    prediction_df = prediction_dict['user_prediction']
                    prediction_bins = list(prediction_df.columns)
                    prediction_values = list(prediction_df.irow(0))
                    prediction = zip(prediction_bins,prediction_values)
                    context_dict['string_prediction'] = repr(prediction)
                #prepare values relating to other times of that day:
                if 'all_time_prediction' in prediction_dict.keys():
                    context_dict['all_time_prediction'] = repr(prediction_dict['all_time_prediction'].to_json())
                #prepare values relating to nearby days:
                if 'all_date_prediction' in prediction_dict.keys():
                    context_dict['all_date_prediction'] = repr(prediction_dict['all_date_prediction'].to_json())
                #Prepare other similar itineraries
                if 'other_option_prediction' in prediction_dict.keys():
                    context_dict['other_option_prediction'] = prediction_dict['other_option_prediction']
                    context_dict['other_option_colorname'] = prediction_dict['other_option_colorname']
            #Set the form fields to contain the searched-for values, for easier searches of similar itineraries:
            airlineform.fields['uniquecarrier'].initial = valuedict['uniquecarrier'][0]
            airportform.fields['origin'].initial = valuedict['origin'][0]
            airportform.fields['dest'].initial = valuedict['dest'][0]
            datetimeform.fields['date'].initial = valuedict['date'][0]
            datetimeform.fields['time'].initial = valuedict['time'][0]
        else:
            print submittedform.errors
            context_dict['errmessage'] = "You've somehow made an error entering your flight info. Please try again"
    else:
        context_dict['welcome_message'] = "Welcome to Delayr!"
    
    context_dict['airportform'] = airportform
    context_dict['airlineform'] = airlineform
    context_dict['datetimeform'] = datetimeform

    return render_to_response('delayr/index.html',context_dict,context)

#This function returns a matplotlib png image displaying the predictions as a function of nearby days:
#There's a fair amount of overlap on the plotting functions, which could probably be pulled into its own function to remove repetition in a world with eternal time.
def show_all_date_prediction(request,prediction):
    context = RequestContext(request)
    prediction_df = df.prep_passed_df(prediction,row_order_column='order',column_order_row='col_order')
    column_names = prediction_df.columns.values[1:]#Only plotting delays and cancellations
    row_names = prediction_df.index.values
    x_vals = np.arange(len(row_names))
    fig = plt.figure(figsize=figsize)
    fig.set_facecolor('none')
    ax = fig.add_subplot(111)
    ax.tick_params(axis='both',which='major',labelsize=ticklabelsize)
    colorcount = 1
    #Actually do the plotting:
    for i in range(len(column_names)):
        ax.plot(x_vals,prediction_df[column_names[i]]*100.,ls='-',marker='o',ms=7,color=colorlist[colorcount],mec=colorlist[colorcount],mfc=colorlist[colorcount],alpha=0.95,label=column_names[i],lw=4)
        colorcount += 1
        if colorcount == len(colorlist):
            colorcount = 0
    #Labels, titles, etc:
    ax.set_title("Delays on Nearby Days",fontsize=titlesize,fontname=fontname)
    ax.set_ylabel("Delay Probability (%)",fontsize=axlabelsize,fontname=fontname)
    ax.set_xlabel("Date",fontsize=axlabelsize,fontname=fontname)
    ax.set_xticks(x_vals)
    ax.set_xticklabels(row_names)
    ax.set_xlim(x_vals.min(),x_vals.max())
    ax.set_ylim(ax.get_ylim()[0],ax.get_ylim()[1]-0.01)
    ax.legend(loc='best',prop={'size':legendsize},numpoints=1)

    #Actually rendering the image:
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(fig)
    return response

#Visualize the prediction at different times of day:
def show_all_time_prediction(request,prediction):
    context = RequestContext(request)
    prediction_df = df.prep_passed_df(prediction,row_order_column='order',column_order_row='col_order')
    column_names = prediction_df.columns.values[1:]#Only plotting delays and cancellations
    row_names = prediction_df.index.values
    x_vals = np.arange(len(row_names))
    fig = plt.figure(figsize=figsize)
    fig.set_facecolor('none')
    ax = fig.add_subplot(111)
    ax.tick_params(axis='both',which='major',labelsize=ticklabelsize)
    colorcount = 1
    #Make the plot:
    for i in range(len(column_names)):
        ax.plot(x_vals,prediction_df[column_names[i]]*100.,ls='-',marker='o',ms=7,color=colorlist[colorcount],mec=colorlist[colorcount],mfc=colorlist[colorcount],alpha=0.95,label=column_names[i],lw=4)
        #ax.plot(x_vals,prediction_df[column_names[i]]*100.,ls='-',marker='o',ms=5,label=column_names[i],lw=3)
        colorcount += 1
        if colorcount == len(colorlist):
            colorcount = 0
    #Labeling frippery:
    ax.set_title("Delays During the Day",fontsize=titlesize,fontname=fontname)
    ax.set_ylabel("Delay Probability (%)",fontsize=axlabelsize,fontname=fontname)
    ax.set_xlabel("Time of Day",fontsize=axlabelsize,fontname=fontname)
    ax.set_xticks(x_vals)
    ax.set_xticklabels(row_names)
    ax.set_xlim(x_vals.min(),x_vals.max())
    ax.set_ylim(ax.get_ylim()[0],ax.get_ylim()[1]-0.01)
    ax.legend(loc='best',prop={'size':legendsize},numpoints=1)

    #Render the thing:
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response,bbox_inches='tight')
    plt.close(fig)
    return response

#Actually plot what the user asked for:
def show_user_prediction(request,string_prediction):
    #This works slightly differently than the other plotting functions, because I hadn't hit upon the pandas->json trick yet when I wrote this, and haven't yet gotten around to standardizing everything.
    context = RequestContext(request)
    prediction = eval(string_prediction)
    unzipped_prediction = zip(*prediction)
    delay_bins = unzipped_prediction[0]
    delay_likelihood = np.array(unzipped_prediction[1])
    x_pos = np.arange(len(delay_bins))
    f = plt.figure(figsize=figsize)
    f.set_facecolor('none')
    ax = f.add_subplot(111)
    ax.tick_params(axis='both',which='major',labelsize=ticklabelsize)
    width = 1.0
    #I toyed with plotting this on a logarithmic y-axis, but decided against it. I left the functionality in the code, though, just in case I change my mind:
    logbool = False
    if logbool:
        ax.set_yscale("log")
        ax.bar(x_pos,delay_likelihood*100.,width,color='red',alpha=0.5,log=True)
    else:
        barlist = ax.bar(x_pos,delay_likelihood*100.,width)
        for i,bar in enumerate(barlist):
            bar.set_color(colorlist[i])

    #Same type of stuff as for other plotting functions:
    ax.set_ylim(ax.get_ylim()[0],100)
    ax.set_title("Predicted Delay for Selected Itinerary",fontsize=titlesize,fontname=fontname)
    ax.set_ylabel("Probability (%)",fontsize=axlabelsize,fontname=fontname)
    ax.set_xlabel("Delay (minutes)",fontsize=axlabelsize,fontname=fontname)
    ax.set_xticks(x_pos+width/2.)
    ax.set_xticklabels(delay_bins)
    ax.yaxis.set_major_formatter(ScalarFormatter())
    
    canvas = FigureCanvasAgg(f)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.close(f)
    return response
