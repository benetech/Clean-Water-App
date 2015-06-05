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
    geoDict = {}
    
    if surveyData:
        for x in range(0, len(surveyData)):    
            urlAnswers = FHServer + "/api/v1/data/" + login_name + "/" + str(surveyData[x]['formid'])
            resultAnswers = requests.get(urlAnswers, headers=headers)
            surveyDataAnswers = json.loads(resultAnswers.content)
            for y in range(0, len(surveyDataAnswers)):
                geoDict[surveyDataAnswers[y]['personalization_group/personalization_question_3']] = surveyDataAnswers[y]['_geolocation']

                     
    context = {'geoDictionary': geoDict}    
    return render(request, 'water_data/map.html', context)
    #return HttpResponse("hello world", mimetype='application/json')
      