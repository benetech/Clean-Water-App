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

from data_model import formatData
from server_request import fetchJSON

#now go through and reformat formatting so that it writes out same XLS file as before
#then add loop logic

def xlsDownload(request, survey_id, login_name, survey_title, submission_id):   
        
    #fetch json data from formhub, returns a list [dataAnswers, dataQuestions]    
    jsonData = fetchJSON(login_name, survey_id)
        
    #combine dictionaries and perform calculations in data_model
    questionDict = formatData(submission_id, jsonData[0], jsonData[1])
    
    output = StringIO.StringIO()
    
    #Setup XLS file
    #-----------------------------------
    OCSA_name = questionDict.get('personalization_question_3')['answer']         
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheetData = workbook.add_worksheet('Data')

    #Cell formatting Data section
    #-----------------------------------
    formatWhite = workbook.add_format({'border': True, 'text_wrap' : True})
    formatWhiteBold = workbook.add_format({'border': True, 'text_wrap' : True, 'bold' : True})
    formatCenter = workbook.add_format({'border': True, 'text_wrap' : True, 'align' : 'center'})
    formatRight = workbook.add_format({'border': True, 'text_wrap' : True, 'align' : 'right'})
    formatCenterBoldUnderline = workbook.add_format({'border': True, 'text_wrap' : True})

    formatPersonalization = workbook.add_format({'bg_color':'#FF0000', 'border': True, 'bold' : True})
    formatCommunity = workbook.add_format({'bg_color':'#FFFF00', 'border': True, 'bold' : True})
    formatAdministration = workbook.add_format({'bg_color':'#92D050', 'border': True, 'bold' : True})
    formatOperation = workbook.add_format({'bg_color':'#00B0F0', 'border': True, 'bold' : True})
    formatSanitation = workbook.add_format({'bg_color':'#FFC000', 'border': True, 'bold' : True})
    formatEducation = workbook.add_format({'bg_color':'#C00000', 'border': True, 'bold' : True})
    formatGIRH = workbook.add_format({'bg_color':'#B1A0C7', 'border': True, 'bold' : True})
    formatGIRS = workbook.add_format({'bg_color':'#D8E4BC', 'border': True, 'bold' : True})
    formatCommunication = workbook.add_format({'bg_color':'#948A54', 'border': True, 'bold' : True})

    #cell formatting Interpretation section
    formatRed = workbook.add_format({'bg_color':'#FF0000', 'border': True, 'bold' : False, 'text_wrap' : True, 'align' : 'center'})
    formatOrange = workbook.add_format({'bg_color':'#F79646', 'border': True, 'bold' : False, 'text_wrap' : True, 'align' : 'center'})
    formatYellow = workbook.add_format({'bg_color':'#FFFF00', 'border': True, 'bold' : False, 'text_wrap' : True, 'align' : 'center'})
    formatGreen = workbook.add_format({'bg_color':'#00B050', 'border': True, 'bold' : False, 'text_wrap' : True, 'align' : 'center'})
    formatPercentage = workbook.add_format({'num_format': '0%', 'border': True, 'bold' : False, 'text_wrap' : True, 'align' :'right'})
    formatSpacer = workbook.add_format({'bg_color':'#538DD5', 'border': False, 'bold' : False, 'text_wrap' : True, 'align' : 'center'})

    formats = [formatPersonalization, formatCommunity, formatAdministration, formatOperation, formatSanitation, formatEducation, formatGIRH, formatGIRS, formatCommunication]
    groups = ['personalization', 'community', 'administration', 'operation', 'sanitation', 'education_sanitation', 'GIRH', 'GIRS', 'communication']

    #set column sizes
    worksheetData.set_column(0, 0, 10)
    worksheetData.set_column(1, 1, 50)
    worksheetData.set_column(2, 2, 30)
    worksheetData.set_column(3, 3, 20)

    #-----------------------------------

    row = 0
    col = 0
    
    for groupNum in range(0, len(groups)): #should be 9
    
        #Write Personalization header to XLS
        if groupNum == 0:
            worksheetData.write(row, col, '#', formats[groupNum])
            worksheetData.write(row, col + 1, u'PERSONALIZACIÓN', formats[groupNum])
            worksheetData.merge_range('C' + str(row + 1) + ':D' + str(row + 1),'REPUESTAS', formats[groupNum])

            row += 1

            #Write answers to Personalization group to XLS
            for x in range (1, questionDict.get(groups[groupNum] + '_size')+1):
                outputQuestion = questionDict.get(groups[groupNum] + '_question_' + str(x))
                if(outputQuestion):
                    worksheetData.write(row, col, outputQuestion.get('question').split(' ')[0], formatWhite)
                    worksheetData.write(row, col + 1, outputQuestion.get('question').split(' ', 1)[1], formatWhite)
                    worksheetData.merge_range('C' + str(row + 1) + ':D' + str(row + 1),outputQuestion.get('answer'), formatWhite)
                    row += 1

            row += 1
        
        #Case for rest of groups
        else:
            #Write header to XLS
            worksheetData.write(row, col, '#', formats[groupNum])
            worksheetData.write(row, col + 1, questionDict.get(groups[groupNum] + '_title'), formats[groupNum])
            worksheetData.write(row, col + 2, 'OBSERVACIONES / COMENTARIOS', formats[groupNum])
            worksheetData.write(row, col + 3, u'CALIFICACIÓN', formats[groupNum])

            row += 1
            #write out the rest of the groups scores
            for x in range (1, questionDict.get(groups[groupNum] + '_size') + 1):
                outputQuestion = questionDict.get(groups[groupNum] + '_question_' + str(x))
                outputComment = questionDict.get(groups[groupNum] + '_comment_' + str(x))

                if (outputQuestion):
                    worksheetData.write(row, col, outputQuestion.get('question').split(' ')[0], formatWhite)
                    worksheetData.write(row, col + 1, outputQuestion.get('question').split(' ', 1)[1], formatWhite)

                    #handle n/a response
                    if(outputQuestion.get('answer') != 'n/a'):
                        worksheetData.write_number(row, col + 3, float(outputQuestion.get('answer')), formatWhite)
                    else: 
                        worksheetData.write(row, col + 3, outputQuestion.get('answer'), formatWhite)
                        
                if (outputComment):
                    worksheetData.write(row, col + 2, outputComment.get('answer'), formatWhite)

                row += 1

            #summation for each group
            worksheetData.write(row, col, '', formatWhite)
            worksheetData.write(row, col + 1, 'PUNTAJE TOTAL', formatWhiteBold)
            worksheetData.write(row, col + 2, '', formatWhite)
            
            #if group wasn't filled out, n/a is the total
            if(questionDict.get(groups[groupNum] + '_filled')):
                worksheetData.write(row, col + 3, questionDict.get(groups[groupNum] + '_score'), formatWhiteBold)
            else:
                worksheetData.write(row, col + 3, 'n/a', formatWhiteBold)

            row += 3
    
    
    #create Interpretación tab in XLS
    #------------------------------
    worksheetViz = workbook.add_worksheet(u'Interpretación')

    #set column sizes
    worksheetViz.set_column(0, 0, 5)
    worksheetViz.set_column(1, 1, 30)
    worksheetViz.set_column(2, 2, 15)
    worksheetViz.set_column(3, 3, 15)
    worksheetViz.set_column(4, 7, 15)

    row = 0
    col = 0

    #VIZ SECTION 1
    #------------------------------

    #Write header to XLS
    worksheetViz.write(row, col, '#', formatWhite)
    worksheetViz.write(row, col + 1, 'Variable', formatWhite)
    worksheetViz.write(row, col + 2, '# de preguntas', formatWhite)
    worksheetViz.write(row, col + 3, u'Puntaje Máximo de acuerdo al numero de preguntas', formatWhite)
    worksheetViz.write(row, col + 4, 'NACIENTE \n (0-30%)', formatRed)
    worksheetViz.write(row, col + 5, u'EXPANSIÓN MODERTADA \n (31-55%)', formatOrange)
    worksheetViz.write(row, col + 6, u'EXPANSIÓN AVANZADA \n (56-80%)', formatYellow)
    worksheetViz.write(row, col + 7, u'CONSOLIDACIÓN \n (81-100%)', formatGreen)


    for x in range(1, len(groups)): #8 because not including Personalization section
        worksheetViz.write(x, col, x, formatWhite)
        worksheetViz.write(x, col + 1, questionDict.get(groups[x] + '_title'), formatWhite)
        worksheetViz.write(x, col + 2, questionDict.get(groups[x] + '_size'), formatWhite)
        worksheetViz.write(x, col + 3, questionDict.get(groups[x] + '_size')*2, formatWhite) #multiply (group size)*2 because each question is worth max 2 points

        
        averageScore = questionDict.get(groups[x] + '_average')
        groupScore = questionDict.get(groups[x] + '_score')
        
        #for each column, follow inequality and write out score
        if (questionDict.get(groups[x] + '_filled')):
                        
            if (averageScore) <= .30:
                worksheetViz.write(x, col + 4, groupScore, formatRed)
            elif (averageScore) > .30 and (averageScore) <= .55:
                worksheetViz.write(x, col + 5, groupScore, formatOrange)
            elif (averageScore) > .55 and (averageScore) <= .80:
                worksheetViz.write(x, col + 6, groupScore, formatYellow)
            elif (averageScore) > .80:
                worksheetViz.write(x, col + 7, groupScore, formatGreen)
                
    #VIZ SECTION 2
    #------------------------------

    #write blue separator  
    row += 10
    worksheetViz.set_row(row - 1 , 3)
    worksheetViz.merge_range('A' + str(row) + ':H' + str(row), " ", formatSpacer)
    row += 2

    #write section header 
    worksheetViz.merge_range('B' + str(row + 1) + ':H' + str(row + 1), 'Puntajes', formatCenter)
    row += 1
    worksheetViz.write(row, col, '#', formatWhite)
    worksheetViz.write(row, col + 1, 'Variable', formatWhite)
    worksheetViz.write(row, col + 2, 'Puntaje', formatWhite)
    worksheetViz.write(row, col + 3, 'Porcentaje', formatWhite)
    worksheetViz.merge_range('E' + str(row + 1) + ':H' + str(row + 1), 'ETAPA', formatWhite)
    row += 1
    
    #write out points, percentage, and category
        
    for x in range(1, len(groups)):
        
        averageScore = questionDict.get(groups[x] + '_average')
        groupScore = questionDict.get(groups[x] + '_score') 
        
        #write names of groups to XLS
        worksheetViz.write(row, col, x, formatWhite)
        worksheetViz.write(row, col + 1, questionDict.get(groups[x] + "_title"), formatWhite)
        worksheetViz.write(row, col + 2, groupScore, formatRight)


        if (questionDict.get(groups[x] + '_filled')):    
            worksheetViz.write(row, col + 3, averageScore, formatPercentage)

            #inequality to determine category based off percentage
            if (averageScore) <= .30:
                worksheetViz.merge_range('E' + str(row + 1) + ':H' + str(row + 1), 'NACIENTE', formatRed)
            elif (averageScore) > .30 and (averageScore) <= .55:
                worksheetViz.merge_range('E' + str(row + 1) + ':H' + str(row + 1), u'EXPANSIÓN MODERTADA', formatOrange)
            elif (averageScore) > .55 and (averageScore) <= .80:
                worksheetViz.merge_range('E' + str(row + 1) + ':H' + str(row + 1), u'EXPANSIÓN AVANZADA', formatYellow)
            elif (averageScore) > .80:
                worksheetViz.merge_range('E' + str(row + 1) + ':H' + str(row + 1), u'CONSOLIDACIÓN', formatGreen)
        else: #case where group hasn't been filled out -> 'n/a'
            worksheetViz.write(row, col + 3, groupScore, formatRight)

        row += 1


    totalScore = questionDict.get('total_score')
    totalAverage = questionDict.get('total_average')
    
    worksheetViz.write(row, col + 1, 'TOTAL', formatWhite)
    worksheetViz.write(row, col + 2, totalScore, formatWhite)
    worksheetViz.write(row, col + 3, totalAverage, formatPercentage)

    row += 1

    #Inequality for category based off total average score
    if (totalAverage) <= .30:
        worksheetViz.merge_range('E' + str(row) + ':H' + str(row), 'NACIENTE', formatRed)
    elif (totalAverage) > .30 and (totalAverage) <= .55:
        worksheetViz.merge_range('E' + str(row) + ':H' + str(row), u'EXPANSIÓN MODERTADA', formatOrange)
    elif (totalAverage) > .55 and (totalAverage) <= .80:
        worksheetViz.merge_range('E' + str(row) + ':H' + str(row), u'EXPANSIÓN AVANZADA', formatYellow)
    elif (totalAverage) > .80:
        worksheetViz.merge_range('E' + str(row) + ':H' + str(row), u'CONSOLIDACIÓN', formatGreen)

    row += 1

    ##write blue separator  
    worksheetViz.set_row(row-1, 3)
    worksheetViz.merge_range('A' + str(row) + ':H' + str(row), " ", formatSpacer)

    #VIZ SECTION 3 (Bar Chart)
    #------------------------------

    chart = workbook.add_chart({'type': 'column'})
    chart.set_title({'name': u'Diagnóstico \n' + questionDict.get("submission_time")})
    chart.set_size({'width': 915, 'height': 550})
    chart.set_legend({'none': True})
    
    #write bar chart to XLS
    chart.add_series({
        'categories': u'Interpretación!B15:B23',
        'values': u'Interpretación!D15:D23',
        'data_labels': {'value': True},
    })
    
    worksheetViz.insert_chart('A' + str(row + 2), chart)

    
    #Case for rest of groups
    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'filename=' + OCSA_name + '.xlsx'

    return response
