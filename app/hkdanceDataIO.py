import hkdanceGlobal as glo
# import QualtricsAPI
import pandas
import os.path
import openpyxl
from openpyxl.styles import Alignment as xlAlignment, Font as xlFont
from pathlib import Path
from math import floor
import copy
import datetime
import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Inches, Pt

import requests
import time
import pyreadstat

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.shapes import MSO_SHAPE_TYPE
# from pptx.util import Pt
# from pptx.enum.text import PP_ALIGN
# from collections.abc import Mapping
import collections.abc

import re
# import pytz
from zoneinfo import ZoneInfo

numericVar = [
    'show', 'showtime', 'firsttime', 'numdance', 
    'seeshowwhy_1', 'seeshowwhy_2', 'seeshowwhy_3', 'seeshowwhy_4', 'seeshowwhy_5', 'seeshowwhy_6', 'seeshowwhy_7', 'seeshowwhy_8', 'seeshowwhy_9', 'seeshowwhy_10', 'seeshowwhy_11', 'seeshowwhy_88', 
    'seeshowwho_1', 'seeshowwho_2', 'seeshowwho_3', 'seeshowwho_4', 'seeshowwho_5', 'seeshowwho_88', 
    'buytixwhat', 
    'buytixwhen', 
    'knowshowhow_1', 'knowshowhow_2', 'knowshowhow_3', 'knowshowhow_4', 'knowshowhow_5', 'knowshowhow_6', 'knowshowhow_7', 
    'knowshowhow_8', 'knowshowhow_9', 'knowshowhow_10', 'knowshowhow_11', 'knowshowhow_12', 'knowshowhow_13', 'knowshowhow_14', 'knowshowhow_15', 'knowshowhow_88', 
    'impact_1', 'impact_2', 'impact_3', 
    'sat_1', 'sat_2', 'sat_3', 'sat_4', 'sat_5', 'sat_6', 'sat_11', 
    'fri_1', 'fri_2', 'fri_3',
    'otherart_1', 'otherart_2', 'otherart_3', 'otherart_4', 'otherart_5', 
    'sex', 'age', 'language', 'industry', 'district', 'income', 'hkdancefriend', 'edm', 
    ]

MISSINGDATAVALUE=999
MISSINGARGVALUE=888
LINEBREAKSTR="__LINEBREAK__"

npsProList=[9, 10]
npsPasList=[7, 8]
npsDetList=[0, 1, 2, 3, 4, 5, 6]
npsProLabel="Promotor"
npsPasLabel="Passive"
npsDetLabel="Detractor"

def ReadDataFromLocal():
    if os.path.isfile(glo.config['HKDANCEDATAPICKLE']) :
        data=pandas.read_pickle(glo.config['HKDANCEDATAPICKLE'])
    else:
        data=GetDataFromQualServer()
    return data

def UpdateMissingFirsttimeAsNonFirsttime(data):
    data.loc[data['firsttime']==999,'firsttime']=0

def DeleteLocalData():
    if os.path.isfile(glo.config['HKDANCEDATAPICKLE']):
        os.remove(glo.config['HKDANCEDATAPICKLE'])

def GetQualtricSurveySPSS(fn, xapitoken, surveyId):
    
    time_sleep = 0.1
    time_max = 40
    data=pandas.DataFrame({'A' : []})

    fileId_not_found = True
    headers = {'Content-Type': 'application/json', 'X-API-TOKEN': xapitoken,  'charset': 'UTF-8'}
    json_data = {"format": "spss", "compress" : False}
    
    response = requests.post(
        'https://yul1.qualtrics.com/API/v3/surveys/' + surveyId + '/export-responses',
        headers=headers,
        json=json_data,
        )
    
    rj=response.json()
    if (rj['meta']['httpStatus'] == '200 - OK'):
        progressId = rj['result']['progressId']
        print(progressId)
    
        headers = {
            'Content-Type': 'application/json',
            'X-API-TOKEN': xapitoken,
            }
        
        time_lapse = 0 

        fileId_not_found = True
        while fileId_not_found:
            try:
                response = requests.get(
                    'https://yul1.qualtrics.com/API/v3/surveys/' + surveyId + '/export-responses/' + progressId,
                    headers=headers,
                    json=json_data,
                    )
                print(time_lapse)
                rj=response.json()
            except:
                print("error making a request to qualtrics for fileId")
            else:
                print("response to fileID request received")
                print(time_lapse)

            
                
            
            if (rj['meta']['httpStatus'] == '200 - OK'):
                if (rj['result']['percentComplete'] == 100):
                    fileId = rj['result']['fileId']
                    percentcomplete = rj['result']['percentComplete']
                    print(fileId)
                    print(percentcomplete)
                    fileId_not_found = False
                
            if fileId_not_found:
                time.sleep(time_sleep)
                time_lapse = time_lapse + time_sleep
                if time_lapse > time_max:
                    break
        
        if fileId_not_found==False:
            headers = {'Content-Type': 'application/json', 'X-API-TOKEN': xapitoken}
            file_not_found = True
            time_lapse = 0 
            while file_not_found:
                try:
                    response = requests.get(
                        'https://yul1.qualtrics.com/API/v3/surveys/' + surveyId + '/export-responses/' + fileId + '/file',
                        headers=headers,
                    )
                    with open(fn, mode='wb') as localfile:
                        localfile.write(response.content)
                    
                except:
                    print("error in downaloading data file")
                    time.sleep(time_sleep)
                    time_lapse = time_lapse + time_sleep
                    if time_lapse > time_max:
                        break
                else:
                    file_not_found = False
                    print("data file downloaded successfully")
                    print(time_lapse)
        
                    
        
        if file_not_found==False:
            if os.path.isfile(fn):
                data, meta=pyreadstat.read_sav(fn, apply_value_formats=False)
            
    return data

def GetDataFromQualServer():
    # QualtricsAPI.Setup.Credentials().qualtrics_api_credentials(token=glo.config['QUALTRICSAPITOKEN'], data_center=glo.config['QUALTRICSDATACENTER'])


    # glo.config['HKDANCESURVEYID1'] = "SV_6kTCiQjvvXAEB3o"
    # glo.config['HKDANCESURVEYID2'] = "SV_07mZtVRrFyy6Mp8"
    
    # glo.config['HKDANCESURVEYID1'] = "SV_07mZtVRrFyy6Mp8"
    # glo.config['HKDANCESURVEYID2'] = "SV_6kTCiQjvvXAEB3o"
    
    print("about to get data from ", glo.config['HKDANCESURVEYID1'])
    # dataFrameWithHeader=QualtricsAPI.Survey.Responses().get_survey_responses(survey=glo.config['HKDANCESURVEYID1'])
    # data1=dataFrameWithHeader.drop(dataFrameWithHeader.index[[0,1]])
    data=GetQualtricSurveySPSS(glo.config['QUALTRICS_DATAFILE_ONLINE'], glo.config['QUALTRICSAPITOKEN'], glo.config['HKDANCESURVEYID1'])
    


    print("about to get data from ", glo.config['HKDANCESURVEYID2'])
    # dataFrameWithHeader=QualtricsAPI.Survey.Responses().get_survey_responses(survey=glo.config['HKDANCESURVEYID2'])
    # data2=dataFrameWithHeader.drop(dataFrameWithHeader.index[[0,1]])
    # data2=GetQualtricSurveySPSS(glo.config['QUALTRICS_DATAFILE_PAPER'], glo.config['QUALTRICSAPITOKEN'], glo.config['HKDANCESURVEYID2'])

    # if (data1.empty==False) and (data2.empty==False):
    #     data=pandas.concat([data1, data2], ignore_index=True, sort=False)
    #     print("both ok")
    # if (data1.empty) and (data2.empty==False):
    #     data=data2
    #     print('paper ok')
    # if (data1.empty==False) and (data2.empty):
    #     data=data1
    #     print('online ok')
    # if (data1.empty) and (data2.empty):
    #     data=pandas.DataFrame({'A' : []})
    #     print('none')
    
    if data.empty==False:
        data=data.rename(columns={"Duration__in_seconds_":"Duration"})
    
    
        for thisNumericVar in numericVar:
            # print(thisNumericVar)
            data[thisNumericVar]=data[thisNumericVar].fillna(MISSINGDATAVALUE).astype('int32')
            
        UpdateMissingFirsttimeAsNonFirsttime(data)
    
        data['StartDate']=pandas.to_datetime(data['StartDate'])
        data['EndDate']=pandas.to_datetime(data['EndDate'])
        data['RecordedDate']=pandas.to_datetime(data['RecordedDate'])
        data["duplicate"]=0
    
        data['showtime']=data['onetime_showtime'].where(data['onetime_showtime'].notnull(),data['showtime']) 
        data['show']=pandas.to_numeric(data['show'])
        data['comment']=data['comment'].str.replace("\n",LINEBREAKSTR)
        data['nps_why']=data['nps_why'].str.replace("\n",LINEBREAKSTR)
    

        
        data['showtime']=data['onetime_showtime'].where(data['onetime_showtime'].notnull(),data['showtime']) 
        
        data['showtime'] = data['showtime'].replace(250101, 240301)
        data['showtime'] = data['showtime'].replace(250102, 240302)
        data['showtime'] = data['showtime'].replace(250103, 240303)
        data['showtime'] = data['showtime'].replace(250201, 240401)
        data['showtime'] = data['showtime'].replace(250202, 240402)
        data['showtime'] = data['showtime'].replace(250203, 240403)
        data['showtime'] = data['showtime'].replace(250204, 240404)
        
        data.loc[data['showtime'] == 240705, 'show'] = 2409
        data.loc[data['showtime'] == 240705, 'showtime'] = 240905
        
        data.loc[data['showtime'] == 240706, 'show'] = 2409
        data.loc[data['showtime'] == 240706, 'showtime'] = 240906


        
        print("replace data")
        
        # data.to_excel(glo.config['HKDANCEDATAXLSX'], encoding='utf-16')
        data.to_excel(glo.config['HKDANCEDATAXLSX'])
        data.to_json(glo.config['HKDANCEDATAJSON'], orient="index")
        data.to_pickle(glo.config['HKDANCEDATAPICKLE'])
        


        
        
    return data

def GenerateGroupTitle(varName, valueList, d100Init):

    tempStr=""
    for thisKey, thisValue in d100Init[varName]['optList'].items():
        if thisKey in valueList:
            tempStr+=thisValue['label']+', '
    tempStr=tempStr[:-2]

    return tempStr

def GetDataCreationTime():

    t = os.path.getmtime(glo.config['HKDANCEDATAPICKLE'])
    t_timestamp = datetime.datetime.fromtimestamp(t)
    return t_timestamp.astimezone(ZoneInfo('Asia/Hong_Kong'))
     


def SampleSize(data, showList, firsttimeList):
    return int(data[(data['Progress']==100) & (data['show'].isin(showList)) & (data['firsttime'].isin(firsttimeList))]['Progress'].count())


def RemoveIrrelevantShowTime(showList, d100):
    these_show_time = list(d100['showtime']['optList'])
    for this_show_time in these_show_time:
        if (this_show_time // 100 not in showList) and (this_show_time != MISSINGDATAVALUE):
            d100['showtime']['optList'][MISSINGDATAVALUE]['yesCount']=d100['showtime']['optList'][MISSINGDATAVALUE]['yesCount'] + d100['showtime']['optList'][this_show_time]['yesCount']
            d100['showtime']['optList'][MISSINGDATAVALUE]['yesPct']=d100['showtime']['optList'][MISSINGDATAVALUE]['yesPct'] + d100['showtime']['optList'][this_show_time]['yesPct']
            d100['showtime']['optList'].pop(this_show_time)
    

def ExtractData100(data, showList, firsttimeList, d100Init):
    d100=copy.deepcopy(d100Init)
    numValid = SampleSize(data, showList, firsttimeList)
    # print("numvalid", numValid)
    for thisPieVar in d100Init:
        tempFreq={}
        # print(thisPieVar)
        tempFreq=data[
            (data['Progress']==100) &
            (data['show'].isin(showList)) &
            (data['firsttime'].isin(firsttimeList))][thisPieVar].value_counts().sort_index().to_dict()
        # print(thisPieVar, tempFreq.items())
        d100[thisPieVar]["numValid"]=numValid
        #print (d100[thisPieVar]["numValid"], " | ", d100Init[thisPieVar]["numValid"])
        #print(tempFreq)
        #print(d100)
        #print(tempFreq)
        for key, value in tempFreq.items():
            # print(thisPieVar)
            # print(key)
            # print(value)
            print(thisPieVar + " | " + str(key) + " | " + str(value))
            try:
                d100[thisPieVar]['optList'][key]["yesCount"]=value
                if numValid==0:
                    d100[thisPieVar]['optList'][key]["yesPct"]=0
                else:
                    d100[thisPieVar]['optList'][key]["yesPct"]=value/numValid
            except:
                print("XXXXXXXXXXXXX", thisPieVar, "has no key ", key)
            

        # print(thisPieVar, d100[thisPieVar]['optList'][999])
        # print('-----------------------------')
        
    npsProCount = data[
        (data['Progress']==100) &
        (data['show'].isin(showList)) &
        (data['firsttime'].isin(firsttimeList)) &
        (data['nps_0'].isin(npsProList))]['nps_0'].count()
    npsPasCount = data[
        (data['Progress']==100) &
        (data['show'].isin(showList)) &
        (data['firsttime'].isin(firsttimeList)) &
        (data['nps_0'].isin(npsPasList))]['nps_0'].count()
    npsDetCount = data[
        (data['Progress']==100) &
        (data['show'].isin(showList)) &
        (data['firsttime'].isin(firsttimeList)) &
        (data['nps_0'].isin(npsDetList))]['nps_0'].count()

    numValidNPS = npsProCount + npsPasCount + npsDetCount
    d100['nps_0']={'label':"客戶滿意度", 'numOption':3, "numValid":numValidNPS, 'optList':{1:{}, 2:{}, 3:{}}, 'sort':False}
    if numValidNPS==0:
        npsProPct=0 
        npsPasPct=0 
        npsDetPct=0 
    else:
        npsProPct=npsProCount/numValidNPS 
        npsPasPct=npsPasCount/numValidNPS
        npsDetPct=npsDetCount/numValidNPS
        
    d100['nps_0']['optList'][1]={'label':"推薦者", 'yesCount':npsProCount, 'yesPct':npsProPct}
    d100['nps_0']['optList'][2]={'label':"被動者", 'yesCount':npsPasCount, 'yesPct':npsPasPct}
    d100['nps_0']['optList'][3]={'label':"批評者", 'yesCount':npsDetCount, 'yesPct':npsDetPct}
        
    d100['nps_2']={'label':"淨推薦值", 'numOption':1, "numValid":numValidNPS, 'optList':{1:{}}, 'sort':False}
    d100['nps_2']['optList'][1]={'label':"淨推薦值", 'yesCount':npsProCount-npsDetCount, 'yesPct':(npsProPct-npsDetPct)}

    RemoveIrrelevantShowTime(showList, d100)
    

    
    return d100

def ExtractDataNot100(data, showList, firsttimeList, dNot100Init):
    dNot100=copy.deepcopy(dNot100Init)
    numValid = SampleSize(data, showList, firsttimeList)
    # maxNumValid = 0
    # print("numvalid", numValid)
    for thisBarItem, thisBarAttr in dNot100Init.items():
        for thisVar in thisBarAttr['varList']:
            # print(thisBarItem)
            # print(thisVar)
            tempCount = data[
                (data['Progress']==100) &
                (data['show'].isin(showList)) &
                (data['firsttime'].isin(firsttimeList)) &
                (data[thisVar].isin(thisBarAttr['yesList']))][thisVar].count()
            tempValid = data[
                (data['Progress']==100) &
                (data['show'].isin(showList)) &
                (data['firsttime'].isin(firsttimeList)) &
                (data[thisVar].isin(thisBarAttr['validValueList']))][thisVar].count()
            dNot100[thisBarItem]['varList'][thisVar]["numValid"]=tempValid
            dNot100[thisBarItem]['varList'][thisVar]["yesCount"]=tempCount
            if tempValid==0:
                dNot100[thisBarItem]['varList'][thisVar]["yesPct"]=0 
            else:
                dNot100[thisBarItem]['varList'][thisVar]["yesPct"]=tempCount/tempValid
    return dNot100



def ReadVarLabelValue(d100, dNot100):
    d100.clear()
    dNot100.clear()
    thisFile = Path('', glo.config['HKDANCEVARLABELVALUEFILE'])
    thisWB = openpyxl.load_workbook(thisFile)
    wsPie = thisWB['piechart']
    maxPie = floor(wsPie.max_row / 3)
    #print(maxPie)
    emptyOption = {MISSINGDATAVALUE : {"label":"沒有資料", "yesCount":0, "yesPct":0.0}}
    for piedx in range(maxPie):
        rowdxValue = piedx*3+1
        rowdxLabel = piedx*3+2
        rowdxSort = piedx*3+3
        piedx = int(wsPie[rowdxValue][0].value)
        pieVar = wsPie[rowdxValue][2].value
        pieLabel = wsPie[rowdxValue][3].value
        numOption = int(wsPie[rowdxValue][4].value)
        d100[pieVar]={}
        d100[pieVar]={"label":pieLabel, "numOption":numOption, "numValid":0, "sort":int(wsPie[rowdxSort][4].value)==1}
        #print(dict100InitData)
        dictOpt = {}
        for vdx in range(numOption):
            dictOpt.update(
                {int(wsPie[rowdxValue][vdx+5].value) : {
                    "label" : wsPie[rowdxLabel][vdx+5].value,
                    "yesCount" : 0,
                    "yesPct" : 0.0}})
        emptyOption = {}
        emptyOption = {MISSINGDATAVALUE : {"label":"沒有資料", "yesCount":0, "yesPct":0.0}}
        dictOpt.update(emptyOption)
        d100[pieVar].update({"optList":dictOpt})

    #print(dict100InitData)

    wsBar = thisWB['barchart']
    maxBar = floor(wsBar.max_row / 5)
    for bardx in range(maxBar):
        rowdxVar = bardx*5+1
        rowdxLabel = bardx*5+2
        rowdxValidValue = bardx*5+3
        rowdxYes = bardx*5+4
        rowdxSort = bardx*5+5
        bardx = int(wsBar[rowdxVar][0].value)
        barItem = wsBar[rowdxVar][2].value
        barLabel = wsBar[rowdxVar][3].value
        numValidValue = wsBar[rowdxValidValue][4].value
        numVar = int(wsBar[rowdxVar][4].value)
        numYes = int(wsBar[rowdxYes][4].value)
        dNot100[barItem]={}
        dNot100[barItem]={"itemLabel":barLabel, "numValidValue":numValidValue, "numVar":numVar, "numYes":numYes, "sort":int(wsBar[rowdxSort][4].value)==1}
        print(barItem, barLabel, dNot100[barItem]['sort'])
        dictVar = {}
        for vdx in range(numVar):
            dictVar.update(
                {wsBar[rowdxVar][vdx+5].value : {
                    "label": wsBar[rowdxLabel][vdx+5].value,
                    "numValid":0,
                    "yesCount":0,
                    "yesPct":0.0}})
        yesList=[]
        for yesdx in range(numYes):
            yesList.append(int(wsBar[rowdxYes][yesdx+5].value))
        validValueList=[]
        for validValudedx in range(numValidValue):
            validValueList.append(int(wsBar[rowdxValidValue][validValudedx+5].value))

        dNot100[barItem].update({"varList":dictVar, 'yesList':yesList, 'validValueList':validValueList})

    #print(dictNot100InitData)


#data=GetQualData()
#data=ReadFromLocal()
#ReadVarLabelValue()

def WriteOneGroup2WorkSheet(ws, title, sampleSize, d1, dx1, startCol):
    fontSizeTitle=15
    rowdx=1
    coldx=startCol
    ws.cell(rowdx, coldx).value=title
    ws.cell(rowdx, coldx).font=xlFont(bold=True, size=fontSizeTitle)
    ws.cell(rowdx+1, coldx).value=sampleSize
    ws.cell(rowdx+1, coldx+1).value="人"
    rowdx+=2
    for key1, value1 in d1.items():
        rowdx+=1
        coldx=startCol
        ws.cell(rowdx, coldx).value=value1['label']
        ws.cell(rowdx, coldx).alignment=xlAlignment(horizontal="left")
        ws.cell(rowdx, coldx).font=xlFont(bold=True, size=fontSizeTitle)
        for key2, value2 in value1['optList'].items():
            coldx+=1
            ws.cell(rowdx+1, coldx).value=value2['label']
            ws.cell(rowdx+1, coldx).alignment=xlAlignment(horizontal="center")
            ws.cell(rowdx+1, coldx).font=xlFont(bold=True)

            ws.cell(rowdx+2, coldx).value=value2['yesCount']
            ws.cell(rowdx+2, coldx).alignment=xlAlignment(horizontal="center")

            ws.cell(rowdx+3, coldx).value=value2['yesPct']
            ws.cell(rowdx+3, coldx).alignment=xlAlignment(horizontal="center")
            ws.cell(rowdx+3, coldx).number_format = '0%'

        rowdx+=4

    rowdx+=3
    for key1, value1 in dx1.items():
        rowdx+=1
        coldx=startCol
        ws.cell(rowdx, coldx).value=value1['itemLabel']
        ws.cell(rowdx, coldx).alignment=xlAlignment(horizontal="left")
        ws.cell(rowdx, coldx).font=xlFont(bold=True, size=fontSizeTitle)
        for key2, value2 in value1['varList'].items():
            coldx+=1
            ws.cell(rowdx+1, coldx).value=value2['label']
            ws.cell(rowdx+1, coldx).alignment=xlAlignment(horizontal="center")
            ws.cell(rowdx+1, coldx).font=xlFont(bold=True)
            
            ws.cell(rowdx+2, coldx).value=value2['numValid']
            ws.cell(rowdx+2, coldx).alignment=xlAlignment(horizontal="center")   

            ws.cell(rowdx+3, coldx).value=value2['yesCount']
            ws.cell(rowdx+3, coldx).alignment=xlAlignment(horizontal="center")

            ws.cell(rowdx+4, coldx).value=value2['yesPct']
            ws.cell(rowdx+4, coldx).alignment=xlAlignment(horizontal="center")
            ws.cell(rowdx+4, coldx).number_format = '0%'
        rowdx+=5

    rowdx+=3
    for feedback in ['impact', 'sat', 'impactTop1', 'satTop1', 'fringe', 'fringeTop1']:
        rowdx+=2
        ws.cell(rowdx, startCol).value=dx1[feedback]['itemLabel']
        ws.cell(rowdx, startCol).alignment=xlAlignment(horizontal="left")
        ws.cell(rowdx, startCol).font=xlFont(bold=True, size=fontSizeTitle)
        sorted_items = sorted(dx1[feedback]['varList'].items(), key=lambda x:x[1]['yesPct'], reverse=True)
        for value2 in sorted_items:
            rowdx+=1
            ws.cell(rowdx, startCol+1).value=value2[1]['label']
            ws.cell(rowdx, startCol+1).alignment=xlAlignment(horizontal="right")
            ws.cell(rowdx, startCol+1).font=xlFont(bold=True)
            
            ws.cell(rowdx, startCol+2).value=value2[1]['numValid']
            ws.cell(rowdx, startCol+2).alignment=xlAlignment(horizontal="right")

            ws.cell(rowdx, startCol+3).value=value2[1]['yesCount']
            ws.cell(rowdx, startCol+3).alignment=xlAlignment(horizontal="right")

            ws.cell(rowdx, startCol+4).value=value2[1]['yesPct']
            ws.cell(rowdx, startCol+4).alignment=xlAlignment(horizontal="right")
            ws.cell(rowdx, startCol+4).number_format = '0%'
        rowdx+=3
        
def UpdateText(thisText, tag_dict):
    matches=re.findall("<<(.*?)>>", thisText)
    for match in matches:
        r = tag_dict[match]
        if ("%" in match):
            newText = "{:.0%}".format(r)
        else:
            newText = str(r)
        thisText=thisText.replace("<<"+match+">>", newText)
    return thisText

def UpdateParagraphs(theseParagraphs, tag_dict):
    for thisPara in theseParagraphs:
        oriText = thisPara.text
        p = thisPara._p
        for idx, run in enumerate(thisPara.runs):
            if idx == 0:
                continue
            p.remove(run._r)
        thisPara.runs[0].text=UpdateText(oriText, tag_dict)
        
       
def CreatePpt(fn, title, showList, sampleSize, d1, dx1):
    results={}
    for this_var_key, this_var_attr in d1.items():
        results[this_var_key] = {} 
        results[this_var_key]['label'] = this_var_attr['label'] 
        results[this_var_key]['sort'] = this_var_attr['sort'] 
        results[this_var_key]['cat']={}
        
        for this_option_key, this_option_attr in this_var_attr['optList'].items():
            results[this_var_key]['cat'][this_option_key] = {}
            results[this_var_key]['cat'][this_option_key]['label']=this_option_attr['label']
            results[this_var_key]['cat'][this_option_key]['numValid'] = this_var_attr['numValid'] 
            results[this_var_key]['cat'][this_option_key]['yesPct']=this_option_attr['yesPct']
            results[this_var_key]['cat'][this_option_key]['yesCount']=this_option_attr['yesCount']
            
            
    for this_var_key, this_var_attr in dx1.items():
        results[this_var_key] = {} 
        results[this_var_key]['label'] = this_var_attr['itemLabel'] 
        results[this_var_key]['sort'] = this_var_attr['sort'] 
        results[this_var_key]['cat']={}

        for this_option_key, this_option_attr in this_var_attr['varList'].items():
            results[this_var_key]['cat'][this_option_key] = {}
            results[this_var_key]['cat'][this_option_key]['label']=this_option_attr['label']
            results[this_var_key]['cat'][this_option_key]['numValid'] = this_option_attr['numValid']
            results[this_var_key]['cat'][this_option_key]['yesPct']=this_option_attr['yesPct']
            results[this_var_key]['cat'][this_option_key]['yesCount']=this_option_attr['yesCount']


    text_showList = ""
    for sdx in showList:
        text_showList = text_showList + d1['show']['optList'][sdx]['label'] + " (" + str(d1['show']['optList'][sdx]['yesCount']) + ")" + "\n"
        
    dictText = {}
    dictText['showlist'] = text_showList
    dictText['title'] = title + " ("+ str(sampleSize) + ")"
    dictText['reportdate'] = datetime.datetime.today().strftime('%Y-%m-%d')
    
    prs = Presentation(Path(glo.config['HKDANCEPPTTEMPLATE']))
    for thisSlide in prs.slides:
        for thisShape in thisSlide.shapes:
            if (thisShape.shape_type==MSO_SHAPE_TYPE.CHART) and (thisShape.alt_text in results.keys()):
                thisChart = thisShape.chart
                thisVar = thisShape.alt_text
                
                chartData=CategoryChartData()
                if (results[thisVar]['sort']):
                    data = collections.OrderedDict(
                        {k:v for k, v in sorted(results[thisVar]['cat'].items(), key=lambda item:item[1]['yesPct'])})
                else:
                    data = results[thisVar]['cat']

                dataCategories=list()
                dataSeries=list()
                for k, v in data.items():
                    dataCategories.append(v['label'])
                    dataSeries.append(v['yesPct'])
                # print(dataCategories)
                # print(dataSeries)
                chartData.categories=dataCategories
                chartData.add_series(results[thisVar]['label'], dataSeries)
                thisChart.replace_data(chartData)
                
            if (thisShape.alt_text=="replacetext") and (thisShape.has_text_frame):
                UpdateParagraphs(thisShape.text_frame.paragraphs, dictText)

                    
    prs.save(glo.config['PATHSTATIC']+fn)
  
    
            
    


def WritePptData2Excel(ws, title, sampleSize, d1, dx1):
    rowdx=1
    for this_var_key, this_var_attr in d1.items():
        ws.cell(rowdx, 1).value="<" + this_var_key + "_title>" 
        ws.cell(rowdx, 2).value=this_var_attr['label'] 
        rowdx=rowdx+1
        for this_option_key, this_option_attr in this_var_attr['optList'].items():
            ws.cell(rowdx, 1).value="<" + this_var_key + "_" + str(this_option_key) + ">" 
            ws.cell(rowdx, 2).value= this_option_attr['label']
            ws.cell(rowdx, 3).value="<" + this_var_key + "_" + str(this_option_key) + "_value>" 
            ws.cell(rowdx, 4).value= this_option_attr['yesPct']
            rowdx = rowdx+1
    for this_var_key, this_var_attr in dx1.items():
        ws.cell(rowdx, 1).value="<" + this_var_key + "_title>" 
        ws.cell(rowdx, 2).value=this_var_attr['itemLabel'] 
        rowdx=rowdx+1
        for this_option_key, this_option_attr in this_var_attr['varList'].items():
            ws.cell(rowdx, 1).value="<" + this_option_key + ">" 
            ws.cell(rowdx, 2).value= this_option_attr['label']
            ws.cell(rowdx, 3).value="<" + this_option_key + "_value>" 
            ws.cell(rowdx, 4).value= this_option_attr['yesPct']
            rowdx = rowdx+1



def SaveSummaryData2Excel(titleF, ssf, d1f, dx1f, titleA, ssa, d1a, dx1a, titleB, ssb, d1b, dx1b):
#    filename = glo.config['SUMMARYDATAEXCELFILEPREFIX']+"-"+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.xlsx'
    filename = glo.config['SUMMARYDATAEXCELFILE']
    print(filename)
    wb=openpyxl.Workbook()
    ws = wb.active
    WriteOneGroup2WorkSheet(ws, titleF, ssf, d1f, dx1f, 1)
    WriteOneGroup2WorkSheet(ws, titleA, ssa, d1a, dx1a, 26)
    WriteOneGroup2WorkSheet(ws, titleB, ssb, d1b, dx1b, 51)
    # ws = wb.create_sheet('pptdata_all')
    # WritePptData2Excel(ws, titleF, ssf, d1f, dx1f)
    
    
    wb.save(filename)


def WriteComment2Word(showList, d1, listComment):
#    filename = glo.config['SUMMARYDATAEXCELFILEPREFIX']+"-"+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.docx'
    filename = glo.config['COMMENTFILE']
    print(filename)
    doc = docx.Document()


    style = doc.styles.add_style('listCommentIndent', WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = doc.styles['List Number']
    paragraph_format = style.paragraph_format
    paragraph_format.left_indent = Inches(0.75)
    paragraph_format.first_line_indent = Inches(-0.5)
    paragraph_format.space_before = Pt(18)
    paragraph_format.space_after = Pt(12)

    paragraph_format.widow_control = True

    doc.add_heading('香港舞蹈團', 0)

    doc.add_heading(datetime.datetime.today().strftime('%Y-%m-%d'), 3)

    sorted_listcomment = sorted(listComment, key=lambda x:x[0])

    # for s in showList:
    #     doc.add_heading(d1['show']['optList'][s]['label'], 2)


    current_show=99
    for c in sorted_listcomment:
        if c[0]!=current_show:
            doc.add_heading(d1['show']['optList'][c[0]]['label'], 2)
        current_show=c[0]
        if len(c[1])>0:
            doc.add_paragraph(c[1].replace(LINEBREAKSTR, "\n"), style='listCommentIndent')


    doc.save(filename)


def ExtractComment(data, showList, firsttimeList, varname): 
    all_comment = data[
        (data['show'].isin(showList)) &
        (data['firsttime'].isin(firsttimeList)) &
        (data[varname].notnull())][['show', varname]].values.tolist()
    non_empty_comment=[]
    for this_comment in all_comment:
        if this_comment[1]!="":
            non_empty_comment.append(this_comment)
    return non_empty_comment






