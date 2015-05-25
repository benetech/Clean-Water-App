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

# Index displays the data on the first page
def index(request, login_name):
    
    if login_name == "adamb":
        FHLogin = "adamb"
        FHPass = "cleanwaterpass"
        FHServer = "http://54.86.146.199"
        headers = {'Authorization':'Token 16d24bfe6de3e4c2c35dd68f8dc4d45cb62c16f4'}
    elif login_name == "cleanwatercr":
        FHLogin = "cleanwatercr"
        FHPass = "cleanwaterpass"
        FHServer = "http://formhub.org"
        headers = {'Authorization':'Token b67eed4084407b53ad32e7277fbb68ecbcf31515'}
        
    url = FHServer + "/api/v1/forms/" + FHLogin
    
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
    
    surveyDict = {}
    
    if surveyData:
        print surveyData
        for x in range(0, len(surveyData)):
            dataDict = {}
            dataDict['url'] = surveyData[x]['url']
            dataDict['date_created'] = surveyData[x]['date_created']
            dataDict['formid'] = surveyData[x]['formid']
            dataDict['last_submission_time'] = surveyData[x]['last_submission_time']
            dataDict['num_of_submissions'] = surveyData[x]['num_of_submissions']
            dataDict['login_name'] = FHLogin
            
            surveyDict[surveyData[x]['title']] = dataDict
                     
    context = {'surveys': surveyDict}    
    return render(request, 'water_data/index.html', context)
    #return HttpResponse("hello world", mimetype='application/json')
    
  
def listSubmissions(request, survey_id, login_name, survey_title):  
    
    if login_name == "adamb":
        FHLogin = "adamb"
        FHPass = "cleanwaterpass"
        FHServer = "http://54.86.146.199"
        headers = {'Authorization':'Token 16d24bfe6de3e4c2c35dd68f8dc4d45cb62c16f4'}
        
    url = FHServer + "/api/v1/data/" + FHLogin + "/" + survey_id
    full_url = request.build_absolute_uri(None)
    
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
   
    surveyDict = {}
    
    if surveyData:
        for x in range(0, len(surveyData)):
            dataDict = {}
            dataDict['submission_time'] = surveyData[x]['_submission_time']     
            dataDict['submission_id'] = surveyData[x]['_id']       
            surveyDict[surveyData[x]['personalization_group/personalization_question_3']] = dataDict
      
    context = {'surveys': surveyDict, 'title': survey_title, 'url' : full_url}    
    return render(request, 'water_data/listSubmissions.html', context)     