from django.conf.urls import patterns, url
from water_data import views

#captions URLS

urlpatterns = patterns('',
    url(r'^(?P<login_name>\w+)/$', views.views.index, name='index'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/$', views.views.listSubmissions, name='listSubmissions'),
    url(r'^(?P<login_name>\w+)/map/$', views.viewsMap.mapMarkersOna, name='mapMarkersOna'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/xlsDownload/(?P<submission_id>\d+)/$', views.viewsXLS.xlsDownload, name='xlsDownload'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/photosDownload/(?P<submission_id>\d+)/$', views.viewsPhotos.photosDownload, name='photosDownload'),
    
)
