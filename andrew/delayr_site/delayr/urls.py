from django.conf.urls import patterns,url
from delayr import views

urlpatterns = patterns('',
                       url(r'^$',views.index,name='index'),
                       url(r'^index$',views.index,name='index'),
                       url(r'^about$',views.about,name='about'),
                       #url(r'^model_output$',views.model_output,name='model_output'),
                       url(r'^test$',views.test,name='test'),
                       url(r'^nitty_gritty$',views.nitty_gritty,name='nitty_gritty'),
                       url(r'^user_prediction_(?P<string_prediction>.+).jpg$',views.show_user_prediction),
                       url(r'^all_time_prediction_(?P<prediction>.+).jpg$',views.show_all_time_prediction),
                       url(r'^all_date_prediction_(?P<prediction>.+).jpg$',views.show_all_date_prediction),
                       )
