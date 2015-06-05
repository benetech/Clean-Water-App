#_*_ coding: utf-8

import sys
import os
import requests
import json
import zipfile
import StringIO
import xlsxwriter

from datetime import datetime
from urllib2 import urlopen
from io import BytesIO

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import utc

#Constants
FHPass = "cleanwaterpass"
FHServer = "http://54.86.146.199"
headers = {'Authorization':'Token b4bbcc2be57b4ed1ed5ffbb4e71bafd85227a6dc'}

# Index displays the data on the first page
def index(request, login_name):
    url = FHServer + "/api/v1/forms/" + login_name
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)

    surveyDict = {}
    if surveyData:
      for item in surveyData:
        dataDict = {}
        dataDict['url'] = item['url']
        dateCreated = item.get('date_created')
        if dateCreated is not None:
          d = datetime.strptime(dateCreated, '%Y-%m-%dT%H:%M:%S.%fZ')
          dataDict['date_created'] = d.strftime('%b %d, %Y %H:%M')
        dataDict['formid'] = item['formid']
        lastSubmission = item.get('last_submission_time')
        if lastSubmission is not None:
          d = datetime.strptime(lastSubmission, '%Y-%m-%dT%H:%M:%S.%fZ')
          dataDict['last_submission_time'] = d.strftime('%b %d, %Y %H:%M')
        dataDict['num_of_submissions'] = item['num_of_submissions']
        dataDict['login_name'] = login_name
        surveyDict[item['title']] = dataDict

    context = {'surveys': surveyDict, 'FHServer': FHServer + '/' + login_name}
    return render(request, 'water_data/index.html', context)
    #return HttpResponse("hello world", mimetype='application/json')


def listSubmissions(request, survey_id, login_name, survey_title):
    url = FHServer + "/api/v1/data/" + login_name + "/" + survey_id
    full_url = request.build_absolute_uri(None)
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)

    surveyDict = {}
    if surveyData:
      for item in surveyData:
        dataDict = {}
        dataDict['has_photos'] = '_attachments' in item
        d = datetime.strptime(item['_submission_time'], '%Y-%m-%dT%H:%M:%S')
        dataDict['submission_time'] = d.strftime('%b %d, %Y %H:%M')
        dataDict['submission_id'] = item['_id']
        dataDict['ocsa_name'] = item['personalization_group/personalization_question_3']
        surveyDict[dataDict['submission_id']] = dataDict

    context = {'surveys': surveyDict, 'title': survey_title, 'url' : full_url}
    return render(request, 'water_data/listSubmissions.html', context)
