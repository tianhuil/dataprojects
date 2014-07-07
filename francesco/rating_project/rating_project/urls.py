from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from static_pages import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rating_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index),
    url(r'project/', include('static_pages.urls')),
    url(r'^rate', include('rate.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
