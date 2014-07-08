from django.conf.urls import url

from rate import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'predict', views.predict, name='predict')
]
