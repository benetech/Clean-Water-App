from django.conf.urls import patterns, url
from water_data import views

#captions URLS

urlpatterns = patterns('',
    url(r'^(?P<login_name>\w+)/$', views.views.index, name='index'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/$', views.views.listSubmissions, name='listSubmissions'),
    url(r'^(?P<login_name>\w+)/map/$', views.viewsMap.mapMarkers, name='mapMarkers'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/xlsDownload/(?P<submission_id>\d+)/$', views.viewsXLS.xlsDownload, name='xlsDownload'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/(?P<survey_title>\w+)/photosStart/(?P<submission_id>\d+)/$', views.viewsPhotos.photosStart, name='photosStart'),
    url(r'^(?P<login_name>\w+)/photosCheck/(?P<task_id>\w+)/$', views.viewsPhotos.photosCheck, name='photosCheck'),
    url(r'^(?P<login_name>\w+)/(?P<survey_id>\d+)/photosFinish/(?P<task_id>\w+)/$', views.viewsPhotos.photosFinish, name='photosFinish'),
    
)
