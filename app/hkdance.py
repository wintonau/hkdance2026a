import hkdanceDataIO
import hkdanceGlobal as glo
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import current_user, LoginManager, login_user, logout_user, login_required, fresh_login_required
import webLogin
from flask_bcrypt import Bcrypt

# import os

import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='')
bcrypt = Bcrypt(app)
app.secret_key = glo.config['FLASKSECRETKEY']
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Please login to access this page."
login_manager.needs_refresh_message = "Please reauthenticate to access this page."
login_manager.init_app(app)


@login_manager.needs_refresh_handler
def refresh():
    # do stuff
    return redirect(url_for("root"))

@login_manager.user_loader
def load_user(thisLogin):
    return webLogin.QueryLogin(thisLogin)

@app.route('/')
def root():
    return render_template(
        glo.config['HKDANCELOGINHTML'],
        title='HKDANCE Audience Survey Research',
        loginStatus="never",
        lastLogin="")


@app.route('/logout/', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("root"))

@app.route('/test/')
def test():
    print("test")
    return 'the test page'

@app.route('/login/', methods=['POST'])
def login():
    if (request.method == 'POST'):
        thisLogin = request.form['login']
        thisPassword = request.form['password']
    else:
        return redirect(url_for(root))

    user = webLogin.QueryLogin(thisLogin)
    if (user != None):
        if webLogin.PasswordCorrectORM(thisLogin, thisPassword):
            loginStatus="success"
        else:
            loginStatus="badpassword"
    else:
        loginStatus="badlogin"


    if loginStatus == "success":
        login_user(user, remember=False)
        if ((thisLogin==glo.config["ADMINLOGIN"]) | (thisLogin==glo.config['SULOGIN'])):
            return redirect(url_for("admin", login="yes"))
        else:
            return redirect(url_for("generate_report", login="yes"))
    else:
        #print('login 2')
        return render_template(
            glo.config['HKDANCELOGINHTML'],
            title='Hong Kong Dance Audience Survey',
            loginStatus = loginStatus,
            lastLogin = thisLogin)



@app.route('/report/', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def generate_report():
    print("current user ----------", current_user.login)
    print("show allowed ----------", current_user.showallowed)
    print(type(current_user.showallowed))
    userShowAllowed = current_user.showallowed
    userShowAllowed = sorted(userShowAllowed)
    webLogin.UpdateLastAccessdORM(current_user.login)
    d100Init={}
    dNot100Init={}
    # pptdata_Full={}
    # pptdata_AAA={}
    # pptdata_BBB={}
    
    hkdanceDataIO.ReadVarLabelValue(d100Init, dNot100Init)

    firsttimeListDisplay=set()
    firsttimeListAAA=set()
    firsttimeListBBB=set()
    firsttimeFullList=set()
    showList=set()
    showFullList=set()


    for firsttimedx in d100Init['firsttime']['optList']:
        firsttimeFullList.add(firsttimedx)
    firsttimeFullList.discard(hkdanceDataIO.MISSINGDATAVALUE)

    for showdx in d100Init['show']['optList']:
        showFullList.add(showdx)
    showFullList.discard(hkdanceDataIO.MISSINGDATAVALUE)

    if (request.method == 'POST'):
        
        if (request.form.get("logout")=="logout"):
            logout_user()
            return redirect(url_for("root"))

        if (request.form.get("renewDataYN")=="Yes"):
            hkdanceDataIO.DeleteLocalData()


        # print('we are here 1')


        idx=0
        for showdx in d100Init['show']['optList']:
            idx+=1
            if request.form.get('cbShowName'+str(idx))!=None:
                showList.add(int(request.form['cbShowName'+str(idx)]))
        showList.discard(hkdanceDataIO.MISSINGARGVALUE)


        # print('we are here 2')


        idx=0
        for firsttimedx in d100Init['firsttime']['optList']:
            idx+=1
            if request.form.get('cbFirstTimeName'+str(idx))!=None:
                firsttimeListAAA.add(int(request.form['cbFirstTimeName'+str(idx)]))
                firsttimeListDisplay.add(int(request.form['cbFirstTimeName'+str(idx)]))
        firsttimeListAAA.discard(hkdanceDataIO.MISSINGARGVALUE)
        firsttimeListBBB = firsttimeFullList-firsttimeListAAA
        
    # preset choices
    firsttimeListAAA = {0}
    firsttimeListBBB = {1}




    data=hkdanceDataIO.ReadDataFromLocal()

    dict100FullFull=hkdanceDataIO.ExtractData100(data, userShowAllowed, firsttimeFullList, d100Init)
    print("showlist", showList)
    print('firsttimeFullList', firsttimeFullList)
    sampleSizeFull=hkdanceDataIO.SampleSize(data, showList, firsttimeFullList)
    print('samplesize', sampleSizeFull)

    if showList==set():
        dict100Full=dict100FullFull
        dictNot100Full=hkdanceDataIO.ExtractDataNot100(data, userShowAllowed, firsttimeFullList, dNot100Init)
        thisTitleFull="全部"+" (" + str(hkdanceDataIO.SampleSize(data, userShowAllowed, firsttimeFullList))+")"

        dict100AAA=dict100Full
        dictNot100AAA=dictNot100Full
        sampleSizeAAA=hkdanceDataIO.SampleSize(data, userShowAllowed, firsttimeFullList)
        showNameAAA = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeFullList, d100Init)
        thisTitleAAA=thisTitleFull

        dict100BBB=dict100Full
        dictNot100BBB=dictNot100Full
        sampleSizeBBB=hkdanceDataIO.SampleSize(data, userShowAllowed, firsttimeFullList)
        showNameBBB = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeFullList, d100Init)
        thisTitleBBB=thisTitleFull

        listComment = hkdanceDataIO.ExtractComment(data, showList, firsttimeFullList, 'comment')
        listNPSWhy = hkdanceDataIO.ExtractComment(data, showList, firsttimeFullList, 'nps_why')
        
        firsttimeListDisplay = [0, 1]

        # print(listComment)

    else:
        dict100Full = hkdanceDataIO.ExtractData100(data, showList, firsttimeFullList, d100Init)
        dictNot100Full = hkdanceDataIO.ExtractDataNot100(data, showList, firsttimeFullList, dNot100Init)
        thisTitleFull="全部"+" (" + str(sampleSizeFull)+")"
        print(thisTitleFull, 'sample size', sampleSizeFull)
        print('-----------------------------')

        dict100AAA = hkdanceDataIO.ExtractData100(data, showList, firsttimeListAAA, d100Init)
        dictNot100AAA = hkdanceDataIO.ExtractDataNot100(data, showList, firsttimeListAAA, dNot100Init)
        sampleSizeAAA=hkdanceDataIO.SampleSize(data, showList, firsttimeListAAA)
        showNameAAA = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeListAAA, d100Init)
        thisTitleAAA = showNameAAA + " (" + str(sampleSizeAAA)+")"
        print(thisTitleAAA, 'sample size', sampleSizeAAA)
        print('-----------------------------')
        
        #hkdanceDataIO.ReadVarLabelValue()
        dict100BBB = hkdanceDataIO.ExtractData100(data, showList, firsttimeListBBB, d100Init)
        dictNot100BBB = hkdanceDataIO.ExtractDataNot100(data, showList, firsttimeListBBB, dNot100Init)
        sampleSizeBBB=hkdanceDataIO.SampleSize(data, showList, firsttimeListBBB)
        showNameBBB = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeListBBB, d100Init)
        thisTitleBBB = showNameBBB + " (" + str(sampleSizeBBB)+")"
        print(thisTitleBBB, 'sample size', sampleSizeBBB)
        print('-----------------------------')

        listComment = hkdanceDataIO.ExtractComment(data, showList, firsttimeFullList, 'comment')
        listNPSWhy = hkdanceDataIO.ExtractComment(data, showList, firsttimeFullList, 'nps_why')

    hkdanceDataIO.SaveSummaryData2Excel(
        "全部", sampleSizeFull, dict100Full, dictNot100Full,
        showNameAAA, sampleSizeAAA, dict100AAA, dictNot100AAA,
        showNameBBB, sampleSizeBBB, dict100BBB, dictNot100BBB,
        )
    
    hkdanceDataIO.CreatePpt("HKDANCE2025-全部.pptx", "全部", showList, sampleSizeFull, dict100Full, dictNot100Full)
    hkdanceDataIO.CreatePpt("HKDANCE2025-首次觀賞.pptx", "首次觀賞", showList, sampleSizeAAA, dict100AAA, dictNot100AAA)
    hkdanceDataIO.CreatePpt("HKDANCE2025-非首次觀賞.pptx", "非首次觀賞", showList, sampleSizeBBB, dict100BBB, dictNot100BBB)
    
    hkdanceDataIO.WriteComment2Word(showList, d100Init, listComment+listNPSWhy)
    
    print("show full list", showFullList)
    print("user show allowed", userShowAllowed)
    print("show list", showList)
    print("firsttime list AAA", firsttimeListAAA)
    print("firsttime list BBB", firsttimeListBBB)
    print("firsttimeListDisplay", firsttimeListDisplay)
    # print(dict100Full)
    
    output_from_parsed_template = render_template(
        glo.config['HKDANCECHARTTEMPLATE'],
        title='HKDANCE Audience Survey Research',
        dataDateTime = hkdanceDataIO.GetDataCreationTime().strftime('%Y-%m-%d　%H:%M'),
        selectedComments=listComment+listNPSWhy,
        showChosen=showList,
        showAllowed=userShowAllowed,
        firsttimeChosen=firsttimeListAAA,
        firsttimeChosenDisplay=firsttimeListDisplay,
        d100FullFull = dict100FullFull,
        d100 = dict100Full,
        dNot100 = dictNot100Full,
        d100AAA = dict100AAA,
        dNot100AAA = dictNot100AAA,
        d100BBB = dict100BBB,
        dNot100BBB = dictNot100BBB,
        titleFull=thisTitleFull, titleAAA=thisTitleAAA, titleBBB=thisTitleBBB)
    with open(glo.config['RENDEREDHTMLFILENAME'], "w", encoding='utf-8') as f:
        f.write(output_from_parsed_template)
    return output_from_parsed_template




# @app.route('/admin/', methods=['POST'])
@app.route('/admin/', methods=['POST', 'GET'])
@login_required
@fresh_login_required
def admin():
    webLogin.UpdateLastAccessdORM(current_user.login)

    d100Init={}
    dNot100Init={}
    hkdanceDataIO.ReadVarLabelValue(d100Init, dNot100Init)


    full_list={}
    full_list['show']={}
    full_list['login']={}

    userallowed_showlist={}

    for k, v in d100Init['show']['optList'].items():
        full_list['show'][k]=v['label']
    for k in webLogin.GetAllLogin():
        full_list['login'][k[0]]=k[0]
        userallowed_showlist[k[0]]=k[1]


    full_list['show']=sorted(full_list['show'].items(), key=lambda x:x[1])
    full_list['login']=sorted(full_list['login'].items(), key=lambda x:x[1])

    message_login = ""

    add_login=False
    del_login=False
    rev_login=False
    change_password=False
    download_data=False
    upload_file=False
    refresh_data=False
    message_upload=""
    inputted_login=""
    inputted_password=""
    userchosen_showlist=set()


    user2check = glo.config['ADMINLOGIN']
    show_list_to_display = set(userallowed_showlist[user2check])
    if (request.method == 'POST'):
        
        
        if (request.form.get("logout")=="logout"):
            logout_user()
            return redirect(url_for("root"))
        
        
        user2check = request.form["rblogin"]
        show_list_to_display = set(userallowed_showlist[user2check])




        idx=0
        for showdx in d100Init['show']['optList']:
            idx+=1
            if (request.values.get('cbshowname'+str(idx))!=None):
                userchosen_showlist.add(int(request.form['cbshowname'+str(idx)]))
        userchosen_showlist.discard(hkdanceDataIO.MISSINGARGVALUE)


        if (request.values.get("inputtedlogin")!=None):
            inputted_login = request.form["inputtedlogin"]
        else:
            inputted_login=""

        if (request.values.get("inputtedpassword")!=None):
            inputted_password = request.form["inputtedpassword"]
        else:
            inputted_password=""


        if (request.values.get("action")!=None):
            add_login=request.form["action"]=="addlogin"
            del_login=request.form["action"]=="dellogin"
            rev_login=request.form["action"]=="revlogin"
            change_password=request.form["action"]=="changepassword"
            download_data=request.form["action"]=="downloaddata"
            upload_file=request.form["action"]=="uploadfile"
            refresh_data=request.form["action"]=="refreshdata"
            print("uploadfile", upload_file)


    if add_login:
        if (inputted_login==""):
            message_login = "Please enter a login"
        else:
            if (inputted_password==""):
                message_login = "Password field cannot be empty"
            else:
                if (inputted_login, inputted_login) in full_list['login']:
                    message_login = "Login already exists"
                    webLogin.UpdateShowAllowed(inputted_login, userchosen_showlist)
                else:
                    webLogin.AddLoginORM(inputted_login, inputted_password, userchosen_showlist)
                user2check=inputted_login

    if change_password:
        if (inputted_login== glo.config['SULOGIN']):
            message_login = "Cannot change password of super admin"
        else:
            if (inputted_login==""):
                message_login = "Please type in the login that the password needs to be changed"
            else:
                if ((inputted_login, inputted_login) in full_list['login']):
                    if (inputted_password==""):
                        message_login = "Password field is empty"
                    else:
                        webLogin.UpdatePasswordORM(inputted_login, inputted_password)
                else:
                    message_login = "The login you entered does not exist"


    if del_login:
        if (inputted_login != glo.config['SULOGIN']) & (inputted_login != glo.config['ADMINLOGIN']):
            print("to be deleted", inputted_login)
            webLogin.DeleteLogin(inputted_login)
        else:
            message_login = "Cannot remove HKDANCE accounts"

    if rev_login:
        print(userchosen_showlist)
        webLogin.UpdateShowAllowed(user2check, userchosen_showlist)
        show_list_to_display=userchosen_showlist

    if add_login | del_login:
        full_list['login']={}
        for k in webLogin.GetAllLogin():
            full_list['login'][k[0]]=k[0]
            userallowed_showlist[k[0]]=k[1]
        full_list['login']=sorted(full_list['login'].items(), key=lambda x:x[1])
        user2check=inputted_login
        if del_login:
            user2check="hkdance"
        show_list_to_display = set(userallowed_showlist[user2check])
        
    if refresh_data:
        data=hkdanceDataIO.GetDataFromQualServer()

    if download_data:
        hkdanceDataIO.GetDataFromQualServer()
        return send_from_directory("", glo.config['HKDANCEDATAXLSX'], as_attachment=True)
    
    if upload_file:
        
        if 'file' in request.files:
            this_upload_file = request.files['file']
        
            if this_upload_file.filename != '':
                filetype_allowed = ['pptx', 'xlsx']
                if "." in this_upload_file.filename:
                    if this_upload_file.filename.rsplit('.', 1)[1].lower() in filetype_allowed:
                        this_upload_file.save(os.path.join(glo.config['PATHSTATIC'], secure_filename(this_upload_file.filename)))
                        message_upload = this_upload_file.filename +' uploaded successfully'
                    else:
                        message_upload = 'Can only upload .pptx or .xlsx files'
                else:
                    message_upload = 'Can only upload .pptx or .xlsx files'
            else:
                message_upload='File to be uploaded cannot be found'
        else:
            message_upload = 'File to be uploaded cannot be found'
            
            
            

    output_from_parsed_template = render_template(
        glo.config['HKDANCEADMINTEMPLATE'],
        title='HKDANCE Audience Survey',
        dataDateTime = hkdanceDataIO.GetDataCreationTime().strftime('%Y-%m-%d %H:%M'),
        user2check = user2check,
        all_list_info = full_list,
        user_allowed=show_list_to_display,
        message_login = message_login,
        message_upload = message_upload
        )
    with open(glo.config['RENDEREDHTMLFILENAME'], "w", encoding='utf-8') as f:
        f.write(output_from_parsed_template)
    return output_from_parsed_template


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)