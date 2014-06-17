from django import forms
from delayr.models import Airports,Airlinenames

class AirportForm(forms.ModelForm):
    airport_qset = Airports.objects.raw('''select distinct(airports.origin),airports.airportname from airports join flightdelays_apr_afternoon on flightdelays_apr_afternoon.origin = airports.origin where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airports.airportname''')
    airport_choice_tup = [(entry.origin,entry.airportname) for entry in airport_qset]
    airportname = forms.ChoiceField(choices = airport_choice_tup,help_text="Select an Airport:")
    #airportname = forms.ModelChoiceField(queryset=airport_qset,empty_label=None,to_field_name='origin')
    #airportname = forms.CharField(max_length=128,help_text="Airport")
    class Meta:
        model = Airports
        fields = ('airportname',)

class AirlineForm(forms.ModelForm):
    airline_qset = Airlinenames.objects.raw('''select distinct(airlinenames.uniquecarrier),airlinenames.fullname from airlinenames join flightdelays_apr_afternoon on flightdelays_apr_afternoon.uniquecarrier = airlinenames.uniquecarrier where year(flightdelays_apr_afternoon.flightdate) >= 2013 order by airlinenames.fullname''')
    airline_choice_tup = [(entry.uniquecarrier,entry.fullname) for entry in airline_qset]
    airlinename = forms.ChoiceField(choices = airline_choice_tup,help_text="Select an Airline:")
    class Meta:
        model = Airlinenames
        fields = ('airlinename',)

class DateTimeForm(forms.Form):
    pass
