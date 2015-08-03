#_*_ coding: utf-8

import sys
import os
import requests
import json
import zipfile
import StringIO
import xlsxwriter

from datetime import datetime
from collections import OrderedDict
from urllib2 import urlopen
from io import BytesIO
import datetime

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import utc

    
def fetchJSON(login_name, survey_id):
    
    urlAnswers = settings.FH_SERVER + "/api/v1/data/" + login_name + '/' + survey_id
    urlQuestions = settings.FH_SERVER + "/api/v1/forms/" + login_name + '/' + survey_id + '/' + 'form.json'
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}

    result = requests.get(urlAnswers, headers=headers)
    dataAnswers = json.loads(result.content)
    result = requests.get(urlQuestions, headers=headers)
    dataQuestions = json.loads(result.content)
    
    dataResult = [dataAnswers, dataQuestions]
                                   
    return dataResult
                    
                    