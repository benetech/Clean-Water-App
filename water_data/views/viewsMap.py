#_*_ coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
import requests
import json
import zipfile
from io import BytesIO
import StringIO
import xlsxwriter
import datetime
from urllib2 import urlopen

#Constants
FHPass = "cleanwaterpass"
FHServer = "http://54.86.146.199"
headers = {'Authorization':'Token b4bbcc2be57b4ed1ed5ffbb4e71bafd85227a6dc'}

# Index displays the data on the first page
def mapMarkers(request, login_name):
    
    url = FHServer + "/api/v1/forms/" + login_name
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
    
    surveyDict = {}
    
    if surveyData:
        for x in range(0, len(surveyData)):
            dataDict = {}
            dataDict['url'] = surveyData[x]['url']
            dateCreated = surveyData[x]['date_created']
            if(dateCreated):
                d = datetime.datetime.strptime(dateCreated, '%Y-%m-%dT%H:%M:%S.%fZ')
                dataDict['date_created'] = d.strftime('%b %d, %Y %H:%M')
            dataDict['formid'] = surveyData[x]['formid']
            lastSubmission = surveyData[x]['last_submission_time']
            if(lastSubmission):
                d = datetime.datetime.strptime(lastSubmission, '%Y-%m-%dT%H:%M:%S.%fZ')
                dataDict['last_submission_time'] = d.strftime('%b %d, %Y %H:%M')
            dataDict['num_of_submissions'] = surveyData[x]['num_of_submissions']
            dataDict['login_name'] = login_name
            
            surveyDict[surveyData[x]['title']] = dataDict
                     
    context = {'surveys': surveyDict, 'FHServer': FHServer + '/' + login_name}    
    return render(request, 'water_data/map.html', context)
    #return HttpResponse("hello world", mimetype='application/json')
      