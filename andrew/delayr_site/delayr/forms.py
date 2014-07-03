from django import forms
from delayr.models import Airports,Airlinenames
from functools import partial
import datetime

def getcurrtime():
    curr = datetime.datetime.now()
    return curr.strftime('%I:%M %p')

def getcurrdate():
    curr = datetime.datetime.now()
    return curr.strftime('%m/%d/%Y')

class AirportForm(forms.Form):
    airport_qset = Airports.objects.raw('''select distinct(airports.origin),airports.airportname from airports join flightdelays_apr_afternoon on flightdelays_apr_afternoon.origin = airports.origin where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airports.airportname''')
    airport_choice_tup = [(entry.origin,entry.airportname) for entry in airport_qset]
    origin = forms.ChoiceField(choices = airport_choice_tup,help_text="Origin Airport:",initial='LGA')
    dest = forms.ChoiceField(choices = airport_choice_tup,help_text="Destination Airport:",initial='ORD')
    # class Meta:
    #     model = Airports
    #     fields = ('airportname',)

class AirlineForm(forms.Form):
    airline_qset = Airlinenames.objects.raw('''select distinct(airlinenames.uniquecarrier),airlinenames.fullname from airlinenames join flightdelays_apr_afternoon on flightdelays_apr_afternoon.uniquecarrier = airlinenames.uniquecarrier where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airlinenames.fullname''')
    airline_choice_tup = [(entry.uniquecarrier,entry.fullname) for entry in airline_qset]
    uniquecarrier = forms.ChoiceField(choices = airline_choice_tup,help_text="Airline:",initial='UA')
    # class Meta:
    #     model = Airlinenames
    #     fields = ('airlinename',)

class DateTimeForm(forms.Form):
    DateInput = partial(forms.DateInput, {'class':'datepicker'})
    TimeInput = partial(forms.TimeInput, {'class':'timepicker'})
    valid_times = ['%I:%M %p']
    valid_dates = ['%m/%d/%Y']
    date = forms.DateField(widget=DateInput(),help_text='Flight Date:',input_formats=valid_dates,initial=getcurrdate)
    time = forms.TimeField(widget=TimeInput(),help_text='Departure Time:',input_formats=valid_times,initial=getcurrtime)
    #date = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}),help_text="Flight Date:")

