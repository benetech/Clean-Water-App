#_*_ coding: utf-8
from django.conf import settings
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

from server_request import fetchJSON
from data_model import formatData
from data_model import formatDataBatch

# Index displays the data on the first page
def mapMarkersOna(request, login_name):
    
    url = settings.FH_SERVER + "/api/v1/forms?owner=" + login_name 
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
    
    
    questionDictTotal = {}
    
    
    #retrieve all questionDict for all forms
    if surveyData:
        #dataResult = [dataAnswers, dataQuestions]
        #iterate through all forms
        for x in range(0, len(surveyData)):
            #get formid to identify form
            formID = str(surveyData[x]['formid'])
            #request json data for that form
            jsonData = fetchJSON(login_name, formID)
            
            #return list of dictionaries of that form
            questionDictList = formatDataBatch(jsonData[0], jsonData[1])
            
            #iterate through all questionDict to create questionDictTotal
            for questionDict in questionDictList:
                #verify that latlng has data, otherwise don't report on map
                if (questionDict['latlng'][0] and questionDict['latlng'][1]) is not None:

                    questionDict['formid'] = formID                
                    #trim numbers of questions
                    for x in range(1, 8):
                        questionDict['personalization_question_' + str(x)]['question'] = questionDict['personalization_question_' + str(x)]['question'].split(' ', 1)[1]

                    questionDict['total_average'] = int(questionDict['total_average']*100)
                    questionDictTotal[questionDict['submission_id']] = questionDict
          
    js_data = simplejson.dumps(questionDictTotal)                 
    context = {'surveysJs': js_data, 'geoDictionary': questionDictTotal}    
    return render(request, 'water_data/map.html', context)
