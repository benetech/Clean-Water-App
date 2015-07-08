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

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.timezone import utc

# Index displays the data on the first page
def index(request, login_name):
    if not (hasattr(settings, 'FH_API_TOKENS') and hasattr(settings, 'FH_SERVER')):
        raise Exception('A fully configured local_settings.py is needed, start with local_settings.py.sample.')

    if not login_name in settings.FH_API_TOKENS or not settings.FH_API_TOKENS[login_name]:
        raise Exception('No API Token found for: ' + login_name + ', add it to local_settings.py')

    url = settings.FH_SERVER + "/api/v1/forms/" + login_name
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)

    surveyDict = {}
    if surveyData:
      for item in surveyData:
        dataDict = {}
        dataDict['url'] = item['url']
        dateCreated = item.get('date_created')
        if dateCreated is not None:
          d = datetime.strptime(dateCreated, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=utc)
          dataDict['date_created'] = d.strftime('%b %d, %Y %H:%M%Z')
        dataDict['formid'] = item['formid']
        lastSubmission = item.get('last_submission_time')
        if lastSubmission is not None:
          d = datetime.strptime(lastSubmission, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=utc)
          dataDict['last_submission_time'] = d.strftime('%b %d, %Y %H:%M%Z')
        dataDict['num_of_submissions'] = item['num_of_submissions']
        dataDict['login_name'] = login_name
        surveyDict[item['title']] = dataDict

    context = {'surveys': surveyDict, 'FHServer': settings.FH_SERVER + '/' + login_name, 'loginName': login_name}
    return render(request, 'water_data/index.html', context)
    #return HttpResponse("hello world", mimetype='application/json')


def getEpochTime(dt):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
    delta = dt - epoch
    return delta.total_seconds()


def listSubmissions(request, survey_id, login_name, survey_title):
    url = settings.FH_SERVER + "/api/v1/data/" + login_name + "/" + survey_id
    full_url = request.build_absolute_uri(None)
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}
    result = requests.get(url, headers=headers)
    surveyData = json.loads(result.content)

    surveyDict = {}
    if surveyData:
      for item in surveyData:
        dataDict = {}
        dataDict['has_photos'] = '_attachments' in item
        d = datetime.strptime(item['_submission_time'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc)
        dataDict['epoch_time'] = getEpochTime(d)
        dataDict['submission_time'] = d.strftime('%b %d, %Y %H:%M%Z')
        dataDict['submission_id'] = item['_id']
        dataDict['ocsa_name'] = item['personalization_group/personalization_question_3']
        surveyDict[dataDict['submission_id']] = dataDict

    sortedSurveyDict = OrderedDict(sorted(surveyDict.items(), key=lambda t: t[1]['epoch_time'], reverse=True))
    context = {'surveys': sortedSurveyDict, 'title': survey_title, 'url' : full_url}
    return render(request, 'water_data/listSubmissions.html', context)
