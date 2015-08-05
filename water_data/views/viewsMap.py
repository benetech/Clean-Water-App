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
    
    #need to get list of all forms, then request all data for each form
    #loop through submission_ids and store returned dictionaries
    #pass necessary information to map
    
    url = settings.FH_SERVER + "/api/v1/forms?owner=" + login_name 
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
    
    #batch will get all submissions for 1 form, not for all forms, that's so it can be re-used with the zip process
    #so, need to loop through all forms, and automatically get list of submissions
    
    questionDictTotal = {}
    
    
    #retrieve all questionDict for all forms
    if surveyData:
        #dataResult = [dataAnswers, dataQuestions]
        #iterate through all forms
        for x in range(0, len(surveyData)):
            #get formid to identify form
            formID = str(surveyData[x]['formid'])
            #request json data for that form
            #print "survey_id: " + survey_id
            
            jsonData = fetchJSON(login_name, formID)
            
            #return list of dictionaries of that form
            questionDictList = formatDataBatch(jsonData[0], jsonData[1])
            
            # questionDict['submission_id'] = submissionID
            # questionDict['latlng'] = geolocation
            # questionDict['form_name'] = formName
            
            
            #iterate through all questionDict
            for questionDict in questionDictList:
                questionDict['formid'] = formID
                print questionDict
                print " "
                questionDictTotal[questionDict['submission_id']] = questionDict

                
        #print "total dict list length: " + str(len(questionDictListTotal))
              
    # for key,value in questionDictTotal.iteritems():
    #       print key
    #       print questionDictTotal[key]  
          
    js_data = simplejson.dumps(questionDictTotal)                 
    context = {'surveysJs': js_data, 'geoDictionary': questionDictTotal}    
    return render(request, 'water_data/map.html', context)
                
                            
                
    return HttpResponse("hello world", mimetype='application/json')



def mapMarkers(request, login_name):
    
    #formhub AWS
    #url = settings.FH_SERVER + "/api/v1/forms/" + login_name
    
    #ONA
    url = settings.FH_SERVER + "/api/v1/forms?owner=" + login_name 
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}

    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)
    
    geoDict = {}
    questions = {} # map of survey id to questions
    
    if surveyData:
        for x in range(0, len(surveyData)):
            survey_id = str(surveyData[x]['formid'])
            
            
            # urlAnswers = settings.FH_SERVER + "/api/v1/data/" + login_name + "/" + survey_id

            #ONA
            urlAnswers = settings.FH_SERVER + "/api/v1/data/" + survey_id

            if not questions.get(survey_id):
                #urlQuestions = settings.FH_SERVER + "/api/v1/forms/" + login_name + "/" + survey_id + "/" + "form.json"
                
                #ONA
                urlQuestions = settings.FH_SERVER + "/api/v1/forms/" + survey_id + "/" + "form.json"
                
                result = requests.get(urlQuestions, headers=headers)
                dataQuestions = json.loads(result.content)
                questions[survey_id] = dataQuestions

            resultAnswers = requests.get(urlAnswers, headers=headers)
            surveyDataAnswers = json.loads(resultAnswers.content)
            currentQuestions = questions[survey_id]

            #add personalization and geo data into dictionary
            for y in range(0, len(surveyDataAnswers)):
                personalDict = {}
                personalDict['latlng'] = surveyDataAnswers[y]['_geolocation']
                personalDict['q_1'] = sanitize_question(currentQuestions['children'][2]['children'][0]['label'])
                personalDict['q_2'] = sanitize_question(currentQuestions['children'][2]['children'][1]['label'])
                personalDict['q_3'] = sanitize_question(currentQuestions['children'][2]['children'][2]['label'])
                personalDict['q_4'] = sanitize_question(currentQuestions['children'][2]['children'][3]['label'])
                personalDict['q_5'] = sanitize_question(currentQuestions['children'][2]['children'][4]['label'])
                personalDict['q_6'] = sanitize_question(currentQuestions['children'][2]['children'][5]['label'])
                personalDict['q_7'] = sanitize_question(currentQuestions['children'][2]['children'][6]['label'])

                personalDict['a_1'] = surveyDataAnswers[y]['personalization_group/personalization_question_1']
                personalDict['a_2'] = surveyDataAnswers[y]['personalization_group/personalization_question_2']
                personalDict['a_3'] = surveyDataAnswers[y]['personalization_group/personalization_question_3']
                personalDict['a_4'] = surveyDataAnswers[y]['personalization_group/personalization_question_4']
                personalDict['a_5'] = surveyDataAnswers[y]['personalization_group/personalization_question_5']
                personalDict['a_6'] = surveyDataAnswers[y]['personalization_group/personalization_question_6']
                personalDict['a_7'] = surveyDataAnswers[y]['personalization_group/personalization_question_7']

                personalDict['score'] = random.randint(0,100)
                personalDict['formid'] = str(surveyData[x]['formid'])
                personalDict['formName'] = surveyDataAnswers[y]['_xform_id_string']
                geoDict[surveyDataAnswers[y]['_id']] = personalDict
                
        for key,value in geoDict.iteritems():
              print key
              print geoDict[key]
    
    js_data = simplejson.dumps(geoDict)                 
    context = {'surveysJs': js_data, 'geoDictionary': geoDict}    
    return render(request, 'water_data/map.html', context)
    #return HttpResponse("hello world", mimetype='application/json')

def sanitize_question(rawQuestion):
    """Sanitize a question. A question looks like "A.1 Nombre", and we want "Nombre"
    """
    i = rawQuestion.find(' ')
    if i > 0:
        return rawQuestion[i + 1:]
    return rawQuestion
