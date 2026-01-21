from dotenv import load_dotenv
import os

load_dotenv()

config={}

config['PATHSTATIC']='static/'
config['QUALTRICS_DATAFILE_ONLINE']=config['PATHSTATIC']+"HKDANCE2025-online.sav"
config['QUALTRICS_DATAFILE_PAPER']=config['PATHSTATIC']+"HKDANCE2025-paper.sav"
config['HKDANCEDATAJSON']=config['PATHSTATIC']+'HKDANCE2025Data.json'
config['HKDANCEDATAXLSX']=config['PATHSTATIC']+'HKDANCE2025Data.xlsx'
config['HKDANCEDATAPICKLE']=config['PATHSTATIC']+'HKDANCE2025Data.pickle'
config['HKDANCEVARLABELVALUEFILE']=config['PATHSTATIC']+'hkdanceVarLabelValue.xlsx'
config['SUMMARYDATAEXCELFILE']=config['PATHSTATIC']+'HKDANCE2025-圖表數據.xlsx'
config['COMMENTFILE']=config['PATHSTATIC']+'HKDANCE2025-觀眾意見.docx'
config['HKDANCEPPTTEMPLATE']=config['PATHSTATIC']+'hkdance2025_template.pptx'

config['PATHTEMPLATE']='templates/'
config['RENDEREDHTMLFILENAME']=config['PATHTEMPLATE']+'rendered.html'
config['HKDANCECHARTTEMPLATE']='hkdanceChartTemplate.html'
config['HKDANCEADMINTEMPLATE']='hkdanceAdmin.html'
config['HKDANCELOGINHTML']='hkdanceLogin.html'

config['QUALTRICSAPITOKEN']=os.getenv('QUALTRICSAPITOKEN')
config['QUALTRICSDATACENTER']=os.getenv('QUALTRICSDATACENTER')
config['QUALTRICSUSERID']=os.getenv('QUALTRICSUSERID')
config['HKDANCESURVEYID2']=os.getenv('HKDANCESURVEYID2')
config['HKDANCESURVEYID1']=os.getenv('HKDANCESURVEYID1')
config['FLASKSECRETKEY']=os.getenv('FLASKSECRETKEY')
config['SQLALCHEMY_ENGINECREDENTIAL']=os.getenv('SQLALCHEMY_ENGINECREDENTIAL')
config['LOGINDBTABLE']=os.getenv('LOGINDBTABLE')
config['SULOGIN']=os.getenv('SULOGIN')
config['SUPASSWORD']=os.getenv('SUPASSWORD')
config['ADMINLOGIN']=os.getenv('ADMINLOGIN')
config['ADMINPASSWORD']=os.getenv('ADMINPASSWORD')



