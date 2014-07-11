from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from rate import views
from static_pages import views as sp_views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rating_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index),
    url(r'^rate/', include('rate.urls')),
    url(r'^project/', sp_views.project),
    url(r'^about/', sp_views.about),
    url(r'^admin/', include(admin.site.urls)),
)
