# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Airports(models.Model):
    origin = models.CharField(primary_key=True, max_length=3)
    airportname = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'airports'

class Airlinenames(models.Model):
    uniquecarrier = models.CharField(primary_key=True, max_length=7)
    fullname = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'airlinenames'

class Flightdelays(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays'

class FlightdelaysAprAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_apr_afternoon'

class FlightdelaysAprEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_apr_early'

class FlightdelaysAprEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_apr_evening'

class FlightdelaysAprMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_apr_morning'

class FlightdelaysAprNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_apr_night'

class FlightdelaysAugAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_aug_afternoon'

class FlightdelaysAugEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_aug_early'

class FlightdelaysAugEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_aug_evening'

class FlightdelaysAugMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_aug_morning'

class FlightdelaysAugNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_aug_night'

class FlightdelaysDecAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_dec_afternoon'

class FlightdelaysDecEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_dec_early'

class FlightdelaysDecEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_dec_evening'

class FlightdelaysDecMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_dec_morning'

class FlightdelaysDecNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_dec_night'

class FlightdelaysFebAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_feb_afternoon'

class FlightdelaysFebEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_feb_early'

class FlightdelaysFebEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_feb_evening'

class FlightdelaysFebMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_feb_morning'

class FlightdelaysFebNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_feb_night'

class FlightdelaysJanAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jan_afternoon'

class FlightdelaysJanEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jan_early'

class FlightdelaysJanEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jan_evening'

class FlightdelaysJanMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jan_morning'

class FlightdelaysJanNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jan_night'

class FlightdelaysJulAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jul_afternoon'

class FlightdelaysJulEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jul_early'

class FlightdelaysJulEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jul_evening'

class FlightdelaysJulMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jul_morning'

class FlightdelaysJulNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jul_night'

class FlightdelaysJunAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jun_afternoon'

class FlightdelaysJunEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jun_early'

class FlightdelaysJunEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jun_evening'

class FlightdelaysJunMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jun_morning'

class FlightdelaysJunNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_jun_night'

class FlightdelaysMarAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_mar_afternoon'

class FlightdelaysMarEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_mar_early'

class FlightdelaysMarEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_mar_evening'

class FlightdelaysMarMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_mar_morning'

class FlightdelaysMarNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_mar_night'

class FlightdelaysMayAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_may_afternoon'

class FlightdelaysMayEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_may_early'

class FlightdelaysMayEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_may_evening'

class FlightdelaysMayMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_may_morning'

class FlightdelaysMayNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_may_night'

class FlightdelaysNovAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_nov_afternoon'

class FlightdelaysNovEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_nov_early'

class FlightdelaysNovEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_nov_evening'

class FlightdelaysNovMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_nov_morning'

class FlightdelaysNovNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_nov_night'

class FlightdelaysOctAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_oct_afternoon'

class FlightdelaysOctEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_oct_early'

class FlightdelaysOctEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_oct_evening'

class FlightdelaysOctMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_oct_morning'

class FlightdelaysOctNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_oct_night'

class FlightdelaysSepAfternoon(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_sep_afternoon'

class FlightdelaysSepEarly(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_sep_early'

class FlightdelaysSepEvening(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_sep_evening'

class FlightdelaysSepMorning(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_sep_morning'

class FlightdelaysSepNight(models.Model):
    fid = models.IntegerField(primary_key=True)
    flightdate = models.DateField()
    uniquecarrier = models.CharField(max_length=7)
    tailnum = models.CharField(max_length=6)
    origincitymarketid = models.IntegerField()
    origin = models.CharField(max_length=3)
    originstate = models.CharField(max_length=2)
    destcitymarketid = models.IntegerField()
    dest = models.CharField(max_length=3)
    deststate = models.CharField(max_length=2)
    crsdeptime = models.CharField(max_length=4)
    depdelay = models.FloatField()
    crsarrtime = models.CharField(max_length=4)
    arrdelay = models.FloatField()
    cancelled = models.FloatField()
    diverted = models.FloatField()
    distance = models.FloatField()
    class Meta:
        managed = False
        db_table = 'flightdelays_sep_night'

