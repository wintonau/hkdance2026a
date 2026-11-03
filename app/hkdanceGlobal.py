from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

APP_DIR = Path(__file__).resolve().parent

config={}

config['PATHSTATIC']=str(APP_DIR / 'static') + os.sep
config['QUALTRICS_DATAFILE_ONLINE']=config['PATHSTATIC']+"HKDANCE2026-online.sav"
config['QUALTRICS_DATAFILE_PAPER']=config['PATHSTATIC']+"HKDANCE2026-paper.sav"
config['HKDANCEDATAJSON']=config['PATHSTATIC']+'HKDANCE2026Data.json'
config['HKDANCEDATAXLSX']=config['PATHSTATIC']+'HKDANCE2026Data.xlsx'
config['HKDANCEDATAPICKLE']=config['PATHSTATIC']+'HKDANCE2026Data.pickle'
config['HKDANCEVARLABELVALUEFILE']=config['PATHSTATIC']+'hkdanceVarLabelValue.xlsx'
config['SUMMARYDATAEXCELFILE']=config['PATHSTATIC']+'HKDANCE2026-圖表數據.xlsx'
config['COMMENTFILE']=config['PATHSTATIC']+'HKDANCE2026-觀眾意見.docx'
config['HKDANCEPPTTEMPLATE']=config['PATHSTATIC']+'hkdance2026_template.pptx'

config['PATHTEMPLATE']=str(APP_DIR / 'templates') + os.sep
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


