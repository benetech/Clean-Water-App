#_*_ coding: utf-8
from django.conf import settings
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

FHServer = "http://54.86.146.199"

def photosDownload(request, survey_id, login_name, survey_title, submission_id): 
    
    urlAnswers = FHServer + "/api/v1/data/" + login_name + '/' + survey_id
    urlQuestions = FHServer + "/api/v1/forms/" + login_name + '/' + survey_id + '/' + 'form.json'
   
    apiKey = settings.FH_API_TOKENS[login_name]
    headers = {'Authorization':'Token ' + apiKey}

    result = requests.get(urlAnswers, headers=headers)
    dataAnswers = json.loads(result.content)
    result = requests.get(urlQuestions, headers=headers)
    dataQuestions = json.loads(result.content)

    #fill Question dict with questions
    #communication_question_1, {question:“question”, answer:“answer”}
    questionDict = {}

    #Photo is 11th entry here, only photo and personalization are important
    for x in range (2, 12):
        for data in dataQuestions['children'][x]['children']:
            answerDict = {}
            answerDict['question'] = data['label']
            questionDict[data['name']] = answerDict

    #get response correlating to id of form 
    for responseNum in range(0, len(dataAnswers)):
        if (str(dataAnswers[responseNum]['_id']) == str(submission_id)):
  
            resultsDict = dataAnswers[responseNum]

            tempResultsDict = {}

            #trim the keys with "/"
            for key,value in resultsDict.iteritems():
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
                else:
                    answerDict = questionDict[key]
                    answerDict['answer'] = 'n/a'
                    questionDict[key] = answerDict

            #determine the number of questions in photo group and personalization group
            photoGroupSize = 0
            personalizationGroupSize = 0

            for key,value in questionDict.iteritems():
                if 'photo_question_' in key:
                    photoGroupSize += 1
                if 'personalization_question_' in key:
                    personalizationGroupSize += 1

            #setup zip file
            unzippedImages = BytesIO()
            zipdata = BytesIO()
            zipf = zipfile.ZipFile(zipdata, mode='w')

            #setup XLS file and write to buffer
            OCSA_name = questionDict.get('personalization_question_3')['answer']         
            workbook = xlsxwriter.Workbook(unzippedImages)
            worksheetPhotos = workbook.add_worksheet('Foto')

            #define formats for XLS
            formatWhite = workbook.add_format({'border': True, 'text_wrap' : True})
            formatPersonalization = workbook.add_format({'bg_color':'#FF0000', 'border': True, 'bold' : True})
            formatPhotos = workbook.add_format({'bg_color':'#92D050', 'border': True, 'bold' : True})

            #set column sizes for XLS format
            worksheetPhotos.set_column(0, 0, 10)
            worksheetPhotos.set_column(1, 1, 50)
            worksheetPhotos.set_column(2, 2, 30)
            worksheetPhotos.set_column(3, 3, 20)

            #write out Personalization section 
            row = 0
            col = 0

            #Personalization Header
            worksheetPhotos.write(row, col, '#', formatPersonalization)
            worksheetPhotos.write(row, col + 1, u'PERSONALIZACIÓN', formatPersonalization)
            worksheetPhotos.write(row, col + 2, 'REPUESTAS', formatPersonalization)

            row +=1

            #Personalization data
            for x in range (1, personalizationGroupSize):
                outputQuestion = questionDict.get('personalization_question_' + str(x))

                if(outputQuestion):
                    worksheetPhotos.write(row, col, outputQuestion.get('question').split(' ')[0], formatWhite)
                    worksheetPhotos.write(row, col + 1, outputQuestion.get('question'), formatWhite)
                    worksheetPhotos.write(row, col + 2, outputQuestion.get('answer'), formatWhite)
                    row += 1

            row += 2

            #Photo Header
            worksheetPhotos.write(row, col, '#', formatPhotos)
            worksheetPhotos.write(row, col + 1, u'FOTOS', formatPhotos)
            worksheetPhotos.write(row, col + 2, 'OBSERVACIONES / COMENTARIOS', formatPhotos)

            row += 1

            #Photo Data
            #In this case, allow user to determine label of image through answer to photo_question_x
            for x in range (1, photoGroupSize+1):
                outputQuestion = questionDict.get('photo_question_' + str(x))
                outputComment = questionDict.get('photo_comment_' + str(x))

                if(outputQuestion):
                    worksheetPhotos.write(row, col, outputQuestion.get('question').split(' ')[0], formatWhite)
                    worksheetPhotos.write(row, col + 1, outputQuestion.get('answer'), formatWhite)
                if(outputComment):
                    worksheetPhotos.write(row, col + 2, outputComment.get('answer'), formatWhite)

                row += 1

            #Close workbook and write to zip file
            workbook.close()
            zipf.writestr(OCSA_name + ' Foto.xlsx', unzippedImages.getvalue())

            #Get photo attachement file names and retrieve them via URL, then add to byte stream
            for x in range (1, photoGroupSize+1):
                imageData = questionDict.get('photo_capture_' + str(x))  
                questionInput = questionDict.get('photo_question_' + str(x))  
                if(imageData and imageData['answer'] != 'n/a'):        
                    url = FHServer + '/attachment/original?media_file=' + login_name + '/attachments/' + imageData['answer']
                    unzippedImages = BytesIO(urlopen(url).read())
                    unzippedImages.seek(0)
                    zipf.writestr(questionInput['answer'] + '.jpg', unzippedImages.getvalue())


            zipf.close()
            zipdata.seek(0)

            response = HttpResponse(zipdata.read(), content_type='application/x-zip')
            response['Content-Disposition'] = 'attachment; filename='+ OCSA_name + ' Foto.zip'

            return response
