#_*_ coding: utf-8

import sys
import os
import requests
import json
from django.conf import settings

def fetchJSON(login_name, survey_id):
    
    #formhub AWS
    #urlAnswers = settings.FH_SERVER + "/api/v1/data/" + login_name + '/' + survey_id
    #urlQuestions = settings.FH_SERVER + "/api/v1/forms/" + login_name + '/' + survey_id + '/' + 'form.json'
    
    
    #ONA
    urlAnswers = settings.FH_SERVER + "/api/v1/data/" + survey_id
    urlQuestions = settings.FH_SERVER + "/api/v1/forms/" + survey_id + '/' + 'form.json'
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}

    result = requests.get(urlAnswers, headers=headers)
    dataAnswers = json.loads(result.content)
    result = requests.get(urlQuestions, headers=headers)
    dataQuestions = json.loads(result.content)
    
    dataResult = [dataAnswers, dataQuestions]
                                   
    return dataResult
                    
                    