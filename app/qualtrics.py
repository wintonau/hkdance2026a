import requests
import time
import hkrepGlobal as glo
import pandas
import os

xapitoken = 'SwTiZTtFzkQIrXxkGIKRLpohiYcbyAyoEmu22LjQ'
surveyId = 'SV_6kTCiQjvvXAEB3o'
surveyId = 'SV_07mZtVRrFyy6Mp8'

    
def GetQualtricSurveySPSS(fn, xapitoken, surveyId):

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
        time_sleep = 1
        time_max = 10
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
            time_sleep = 1
            time_max = 10
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
                data=pandas.read_spss(fn)
    return data
                
            
    



xapitoken = 'SwTiZTtFzkQIrXxkGIKRLpohiYcbyAyoEmu22LjQ'

surveyId = 'SV_6kTCiQjvvXAEB3o'
data1=GetQualtricSurveySPSS(glo.config['QUALTRICS_DATAFILE_ONLINE'],xapitoken, surveyId)
print(data1)
                      
surveyId = 'SV_07mZtVRrFyy6Mp8'
data2=GetQualtricSurveySPSS(glo.config['QUALTRICS_DATAFILE_PAPER'],xapitoken, surveyId)
print(data2)