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

    
def formatData(submission_id, dataQuestions, dataAnswers):

    
    #list of all the groups to be analyzed in dashboard
    groups = ['personalization', 'community', 'administration', 'operation', 'sanitation', 'education_sanitation', 'GIRH', 'GIRS', 'communication']
    questionDict = {}

    #format: communication_question_1, {question:“question”, answer:“answer”}
    
    #generate questionsDict
    for x in range (2, 11):
        for data in dataQuestions['children'][x]['children']:
            answerDict = {}
            answerDict['question'] = data['label']
            questionDict[data['name']] = answerDict     

    #based on submission_id, create questionsDict with answers
    for responseNum in range(0, len(dataAnswers)):
        if (str(dataAnswers[responseNum]['_id']) == str(submission_id)):
  
            resultsDict = dataAnswers[responseNum]

            #edit resultsDict to have trimmed keys
            tempResultsDict = {}

            for key,value in resultsDict.iteritems():
                if "submission_time" in key:
                    
                    d = datetime.datetime.strptime(resultsDict.get(key), '%Y-%m-%dT%H:%M:%S')
                    submissionDateFormatted = d.strftime('%b %d, %Y')

                if "/" in key:
                    tempResultsDict[key.split("/")[1]] = resultsDict[key]

            resultsDict = tempResultsDict

            #combine questionDict and resultsDict
            for key,value in questionDict.iteritems():
                result = resultsDict.get(key)
                
                if (result):
                    #update answerDict in questionDict w/ results
                    answerDict = questionDict[key]
                    answerDict['answer'] = result
                    questionDict[key] = answerDict
                else: #groups that aren't filled out get an answer of 'n/a
                    answerDict = questionDict[key]
                    answerDict['answer'] = "n/a"
                    questionDict[key] = answerDict
                    
            
            #iterate through groups, now store group size in questionDict
            totalScore = 0
            numQuestionsTotal = 0
            
            questionDict['submission_time'] = submissionDateFormatted
            
            for groupNum in range(0, len(groups)): #should be 9
                groupScore = 0
                groupSize = 0

                #determine the number of questions in each group
                for key,value in questionDict.iteritems():
                    if groups[groupNum] + '_question_' in key:
                        if groups[groupNum] == "sanitation":    #if group is sanitation
                            if key.split("_")[0] == "sanitation":   #then only add sanitation, not education_sanitation
                                groupSize += 1
                        else:   #default case
                            groupSize += 1

                #record # of questions in each list for viz
                #groupSizeList.append(groupSize)
                questionDict[groups[groupNum] + '_size'] = groupSize
                
                #every group except personalization
                if groupNum != 0:
                    #calculate scores
                    for x in range (1, groupSize+1): ###
                        outputQuestion = questionDict.get(groups[groupNum] + '_question_' + str(x))
                        outputComment = questionDict.get(groups[groupNum] + '_comment_' + str(x))

                        if (outputQuestion):
                            #handle n/a response
                            if(outputQuestion.get('answer') != 'n/a'):                                
                                groupScore += float(outputQuestion.get('answer')) #calculate total score for group
                                groupFilled = True
                            else: #if group isn't filled out = n/a, don't add to score total
                                groupFilled = False
                    
                    groupTitle = questionDict.get(groups[groupNum] + '_note') 
                    
                    if(groupTitle):
                        questionDict[groups[groupNum] + '_title'] = groupTitle.get('question')
                    
                    #record total score for all groups
                    totalScore += groupScore
                    #record groupScores and groupFilled for viz section
                    
                    if (groupFilled):
                        questionDict[groups[groupNum] + '_score'] = groupScore
                        questionDict[groups[groupNum] + '_average'] = (groupScore/(groupSize*2))
                        numQuestionsTotal += groupSize
                    else:
                        questionDict[groups[groupNum] + '_average'] = 'n/a'
                        questionDict[groups[groupNum] + '_score'] = 'n/a'
                                    
                    
                    questionDict[groups[groupNum] + '_filled'] = groupFilled
                    
            questionDict['total_score'] = totalScore
            questionDict['total_average'] = (totalScore/(numQuestionsTotal*2))
                
                                    
    return questionDict
                    
                    