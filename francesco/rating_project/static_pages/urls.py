from django.conf.urls import url

from static_pages import views

urlpatterns = [
    url("^$", views.project, name='project'),
    url("^about$", views.about, name='about')
]