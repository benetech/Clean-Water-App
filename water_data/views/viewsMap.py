#_*_ coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import simplejson
import sys
import os
import requests
import json
import zipfile
from io import BytesIO
import StringIO
import xlsxwriter
import datetime
import random
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
            
            #add personalization and geo data into dictionary
            for y in range(0, len(surveyDataAnswers)):
                personalDict = {}
                personalDict['latlng'] = surveyDataAnswers[y]['_geolocation']
                personalDict['q_1'] = surveyDataAnswers[y]['personalization_group/personalization_question_1']
                personalDict['q_2'] = surveyDataAnswers[y]['personalization_group/personalization_question_2']
                personalDict['q_3'] = surveyDataAnswers[y]['personalization_group/personalization_question_3']
                personalDict['q_4'] = surveyDataAnswers[y]['personalization_group/personalization_question_4']
                personalDict['q_5'] = surveyDataAnswers[y]['personalization_group/personalization_question_5']
                personalDict['q_6'] = surveyDataAnswers[y]['personalization_group/personalization_question_6']
                personalDict['q_7'] = surveyDataAnswers[y]['personalization_group/personalization_question_7']
                personalDict['score'] = random.randint(0,100)
                personalDict['formid'] = str(surveyData[x]['formid'])
                geoDict[surveyDataAnswers[y]['_id']] = personalDict
                
        # for key,value in geoDict.iteritems():
        #     print key
        #     print geoDict[key]
    
    js_data = simplejson.dumps(geoDict)                 
    context = {'surveysJs': js_data, 'geoDictionary': geoDict}    
    return render(request, 'water_data/map.html', context)
    #return HttpResponse("hello world", mimetype='application/json')
