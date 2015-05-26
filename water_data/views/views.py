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
FHLogin = "adamb"
FHPass = "cleanwaterpass"
FHServer = "http://54.86.146.199"
headers = {'Authorization':'Token 16d24bfe6de3e4c2c35dd68f8dc4d45cb62c16f4'}

# Index displays the data on the first page
def index(request, login_name):
    
    if login_name == "adamb":
        url = FHServer + "/api/v1/forms/" + FHLogin
        result = requests.get(url, headers=headers)
        surveyData = json.loads(result.content)
    else:
        print "hello world"
        ##return some sort of error here 
    
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
            dataDict['login_name'] = FHLogin
            
            surveyDict[surveyData[x]['title']] = dataDict
                     
    context = {'surveys': surveyDict}    
    return render(request, 'water_data/index.html', context)
    #return HttpResponse("hello world", mimetype='application/json')
    
  
def listSubmissions(request, survey_id, login_name, survey_title):  
    
    if login_name == "adamb":        
        url = FHServer + "/api/v1/data/" + FHLogin + "/" + survey_id
        full_url = request.build_absolute_uri(None)
        result = requests.get(url, headers=headers)
        surveyData = json.loads(result.content)
    else:
        print "hello world"
   
    surveyDict = {}
    
    if surveyData:
        for x in range(0, len(surveyData)):
            dataDict = {}
            if(not surveyData[x]['_attachments']):
                dataDict['has_photos'] = False
            else:
                dataDict['has_photos'] = True         
            d = datetime.datetime.strptime(surveyData[x]['_submission_time'], '%Y-%m-%dT%H:%M:%S')
            dataDict['submission_time'] = d.strftime('%b %d, %Y %H:%M')    
            dataDict['submission_id'] = surveyData[x]['_id']       
            surveyDict[surveyData[x]['personalization_group/personalization_question_3']] = dataDict
      
    context = {'surveys': surveyDict, 'title': survey_title, 'url' : full_url}    
    return render(request, 'water_data/listSubmissions.html', context)     