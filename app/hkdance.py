import os
from pathlib import Path

import hkdanceDataIO
import hkdanceGlobal as glo
import webLogin
from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    fresh_login_required,
    login_required,
    login_user,
    logout_user,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

ALLOWED_UPLOAD_EXTENSIONS = frozenset({"pptx", "xlsx"})

app = Flask(__name__, static_url_path='')
bcrypt = Bcrypt(app)
app.secret_key = glo.config['FLASKSECRETKEY']
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Please login to access this page."
login_manager.needs_refresh_message = "Please reauthenticate to access this page."
login_manager.init_app(app)


def _selected_form_values(field_prefix, options):
    """Return submitted integer values that are valid options."""
    valid_options = set(options)
    selected = set()
    for field_name, value in request.form.items():
        if not field_name.startswith(field_prefix):
            continue
        try:
            selected_value = int(value)
        except ValueError:
            continue
        if selected_value in valid_options:
            selected.add(selected_value)
    return selected


def _is_administrator(login):
    return login in {glo.config['ADMINLOGIN'], glo.config['SULOGIN']}


@login_manager.needs_refresh_handler
def refresh():
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
    return 'the test page'


@app.route('/login/', methods=['POST'])
def login():
    thisLogin = request.form.get('login', '').strip()
    thisPassword = request.form.get('password', '')

    user = webLogin.QueryLogin(thisLogin) if thisLogin else None
    if user is None:
        loginStatus = "badlogin"
    elif webLogin.PasswordCorrectORM(thisLogin, thisPassword):
        loginStatus = "success"
    else:
        loginStatus = "badpassword"

    if loginStatus == "success":
        login_user(user, remember=False)
        if _is_administrator(thisLogin):
            return redirect(url_for("admin", login="yes"))
        return redirect(url_for("generate_report", login="yes"))

    return render_template(
        glo.config['HKDANCELOGINHTML'],
        title='Hong Kong Dance Audience Survey',
        loginStatus=loginStatus,
        lastLogin=thisLogin)


@app.route('/report/', methods=['GET', 'POST'])
@login_required
@fresh_login_required
def generate_report():
    userShowAllowed = sorted(set(current_user.showallowed))
    webLogin.UpdateLastAccessdORM(current_user.login)
    d100Init = {}
    dNot100Init = {}
    hkdanceDataIO.ReadVarLabelValue(d100Init, dNot100Init)

    firsttime_options = [
        value for value in d100Init['firsttime']['optList']
        if value not in (hkdanceDataIO.MISSINGDATAVALUE, hkdanceDataIO.MISSINGARGVALUE)
    ]
    firsttimeFullList = set(firsttime_options)
    allowed_show_options = [
        value for value in userShowAllowed
        if value in d100Init['show']['optList']
        and value not in (hkdanceDataIO.MISSINGDATAVALUE, hkdanceDataIO.MISSINGARGVALUE)
    ]
    showList = set()
    firsttimeListDisplay = set()

    if request.method == 'POST':
        if request.form.get("logout") == "logout":
            logout_user()
            return redirect(url_for("root"))

        if request.form.get("renewDataYN") == "Yes":
            hkdanceDataIO.DeleteLocalData()

        showList = _selected_form_values("cbShowName", allowed_show_options)
        firsttimeListDisplay = _selected_form_values(
            "cbFirstTimeName", firsttime_options)

    effectiveShowList = showList or set(allowed_show_options)
    firsttimeListAAA = {0}
    firsttimeListBBB = {1}

    data = hkdanceDataIO.ReadDataFromLocal()

    dict100FullFull = hkdanceDataIO.ExtractData100(
        data, userShowAllowed, firsttimeFullList, d100Init)
    sampleSizeFull = hkdanceDataIO.SampleSize(
        data, effectiveShowList, firsttimeFullList)

    if not showList:
        dict100Full = dict100FullFull
        dictNot100Full = hkdanceDataIO.ExtractDataNot100(
            data, userShowAllowed, firsttimeFullList, dNot100Init)
        thisTitleFull = "全部 (" + str(sampleSizeFull) + ")"

        dict100AAA = dict100Full
        dictNot100AAA = dictNot100Full
        sampleSizeAAA = sampleSizeFull
        showNameAAA = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeFullList, d100Init)
        thisTitleAAA = thisTitleFull

        dict100BBB = dict100Full
        dictNot100BBB = dictNot100Full
        sampleSizeBBB = sampleSizeFull
        showNameBBB = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeFullList, d100Init)
        thisTitleBBB = thisTitleFull

        listComment = hkdanceDataIO.ExtractComment(
            data, effectiveShowList, firsttimeFullList, 'comment')
        listNPSWhy = hkdanceDataIO.ExtractComment(
            data, effectiveShowList, firsttimeFullList, 'nps_why')
        firsttimeListDisplay = [0, 1]
    else:
        dict100Full = hkdanceDataIO.ExtractData100(
            data, effectiveShowList, firsttimeFullList, d100Init)
        dictNot100Full = hkdanceDataIO.ExtractDataNot100(
            data, effectiveShowList, firsttimeFullList, dNot100Init)
        thisTitleFull = "全部 (" + str(sampleSizeFull) + ")"

        dict100AAA = hkdanceDataIO.ExtractData100(
            data, effectiveShowList, firsttimeListAAA, d100Init)
        dictNot100AAA = hkdanceDataIO.ExtractDataNot100(
            data, effectiveShowList, firsttimeListAAA, dNot100Init)
        sampleSizeAAA = hkdanceDataIO.SampleSize(data, effectiveShowList, firsttimeListAAA)
        showNameAAA = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeListAAA, d100Init)
        thisTitleAAA = showNameAAA + " (" + str(sampleSizeAAA) + ")"

        dict100BBB = hkdanceDataIO.ExtractData100(
            data, effectiveShowList, firsttimeListBBB, d100Init)
        dictNot100BBB = hkdanceDataIO.ExtractDataNot100(
            data, effectiveShowList, firsttimeListBBB, dNot100Init)
        sampleSizeBBB = hkdanceDataIO.SampleSize(data, effectiveShowList, firsttimeListBBB)
        showNameBBB = hkdanceDataIO.GenerateGroupTitle("firsttime", firsttimeListBBB, d100Init)
        thisTitleBBB = showNameBBB + " (" + str(sampleSizeBBB) + ")"

        listComment = hkdanceDataIO.ExtractComment(
            data, effectiveShowList, firsttimeFullList, 'comment')
        listNPSWhy = hkdanceDataIO.ExtractComment(
            data, effectiveShowList, firsttimeFullList, 'nps_why')

    hkdanceDataIO.SaveSummaryData2Excel(
        "全部", sampleSizeFull, dict100Full, dictNot100Full,
        showNameAAA, sampleSizeAAA, dict100AAA, dictNot100AAA,
        showNameBBB, sampleSizeBBB, dict100BBB, dictNot100BBB,
        )

    hkdanceDataIO.CreatePpt(
        "HKDANCE2026-全部.pptx", "全部", effectiveShowList,
        sampleSizeFull, dict100Full, dictNot100Full)
    hkdanceDataIO.CreatePpt(
        "HKDANCE2026-首次觀賞.pptx", "首次觀賞", effectiveShowList,
        sampleSizeAAA, dict100AAA, dictNot100AAA)
    hkdanceDataIO.CreatePpt(
        "HKDANCE2026-非首次觀賞.pptx", "非首次觀賞", effectiveShowList,
        sampleSizeBBB, dict100BBB, dictNot100BBB)

    hkdanceDataIO.WriteComment2Word(
        effectiveShowList, d100Init, listComment + listNPSWhy)

    output_from_parsed_template = render_template(
        glo.config['HKDANCECHARTTEMPLATE'],
        title='HKDANCE Audience Survey Research',
        dataDateTime=hkdanceDataIO.GetDataCreationTime().strftime('%Y-%m-%d　%H:%M'),
        selectedComments=listComment+listNPSWhy,
        showChosen=sorted(effectiveShowList),
        showAllowed=userShowAllowed,
        firsttimeChosen=firsttimeListAAA,
        firsttimeChosenDisplay=firsttimeListDisplay,
        d100FullFull=dict100FullFull,
        d100=dict100Full,
        dNot100=dictNot100Full,
        d100AAA=dict100AAA,
        dNot100AAA=dictNot100AAA,
        d100BBB=dict100BBB,
        dNot100BBB=dictNot100BBB,
        titleFull=thisTitleFull, titleAAA=thisTitleAAA, titleBBB=thisTitleBBB)
    with open(glo.config['RENDEREDHTMLFILENAME'], "w", encoding='utf-8') as f:
        f.write(output_from_parsed_template)
    return output_from_parsed_template




@app.route('/admin/', methods=['POST', 'GET'])
@login_required
@fresh_login_required
def admin():
    if not _is_administrator(current_user.login):
        abort(403)

    webLogin.UpdateLastAccessdORM(current_user.login)

    d100Init = {}
    dNot100Init = {}
    hkdanceDataIO.ReadVarLabelValue(d100Init, dNot100Init)

    full_list = {'show': {}, 'login': {}}
    userallowed_showlist = {}

    for k, v in d100Init['show']['optList'].items():
        full_list['show'][k]=v['label']
    for k in webLogin.GetAllLogin():
        full_list['login'][k[0]]=k[0]
        userallowed_showlist[k[0]]=k[1]


    full_list['show']=sorted(full_list['show'].items(), key=lambda x:x[1])

    message_login = ""
    message_upload = ""
    inputted_login = ""
    inputted_password = ""
    userchosen_showlist = set()
    user2check = current_user.login

    if user2check not in userallowed_showlist:
        abort(403)

    if request.method == 'POST':
        if request.form.get("logout") == "logout":
            logout_user()
            return redirect(url_for("root"))

        selected_login = request.form.get("rblogin", user2check)
        if selected_login in userallowed_showlist:
            user2check = selected_login

        show_options = [
            value for value in d100Init['show']['optList']
            if value not in (hkdanceDataIO.MISSINGDATAVALUE, hkdanceDataIO.MISSINGARGVALUE)
        ]
        userchosen_showlist = _selected_form_values("cbshowname", show_options)
        inputted_login = request.form.get("inputtedlogin", "").strip()
        inputted_password = request.form.get("inputtedpassword", "")
        action = request.form.get("action")

        if action == "addlogin":
            if not inputted_login:
                message_login = "Please enter a login"
            elif not inputted_password:
                message_login = "Password field cannot be empty"
            elif inputted_login in userallowed_showlist:
                message_login = "Login already exists"
            else:
                webLogin.AddLoginORM(inputted_login, inputted_password, userchosen_showlist)
                user2check = inputted_login
        elif action == "changepassword":
            if inputted_login == glo.config['SULOGIN']:
                message_login = "Cannot change password of super admin"
            elif not inputted_login:
                message_login = "Please type in the login that the password needs to be changed"
            elif inputted_login not in userallowed_showlist:
                message_login = "The login you entered does not exist"
            elif not inputted_password:
                message_login = "Password field is empty"
            else:
                webLogin.UpdatePasswordORM(inputted_login, inputted_password)
        elif action == "dellogin":
            if inputted_login in (glo.config['SULOGIN'], glo.config['ADMINLOGIN']):
                message_login = "Cannot remove HKDANCE accounts"
            elif inputted_login not in userallowed_showlist:
                message_login = "The login you entered does not exist"
            else:
                webLogin.DeleteLogin(inputted_login)
                user2check = glo.config['ADMINLOGIN']
        elif action == "revlogin":
            webLogin.UpdateShowAllowed(user2check, userchosen_showlist)
        elif action == "refreshdata":
            hkdanceDataIO.GetDataFromQualServer()
        elif action == "downloaddata":
            hkdanceDataIO.GetDataFromQualServer()
            data_path = glo.config['HKDANCEDATAXLSX']
            return send_from_directory(
                os.path.dirname(data_path),
                os.path.basename(data_path),
                as_attachment=True)
        elif action == "uploadfile":
            uploaded_file = request.files.get('file')
            if uploaded_file is None or not uploaded_file.filename:
                message_upload = 'File to be uploaded cannot be found'
            else:
                filename = secure_filename(uploaded_file.filename)
                extension = Path(filename).suffix.lower().lstrip('.')
                if not filename or extension not in ALLOWED_UPLOAD_EXTENSIONS:
                    message_upload = 'Can only upload .pptx or .xlsx files'
                else:
                    uploaded_file.save(os.path.join(glo.config['PATHSTATIC'], filename))
                    message_upload = f'{filename} uploaded successfully'

    user_rows = webLogin.GetAllLogin()
    userallowed_showlist = {login: showlist for login, showlist in user_rows}
    full_list['login'] = sorted(
        ((login, login) for login in userallowed_showlist),
        key=lambda item: item[1])

    if user2check not in userallowed_showlist:
        user2check = glo.config['ADMINLOGIN']
    if user2check not in userallowed_showlist:
        abort(403)
    show_list_to_display = set(userallowed_showlist[user2check])

    if request.method == 'POST' and request.form.get("action") == "revlogin":
        show_list_to_display = userchosen_showlist

    output_from_parsed_template = render_template(
        glo.config['HKDANCEADMINTEMPLATE'],
        title='HKDANCE Audience Survey',
        dataDateTime=hkdanceDataIO.GetDataCreationTime().strftime('%Y-%m-%d %H:%M'),
        user2check=user2check,
        all_list_info=full_list,
        user_allowed=show_list_to_display,
        message_login=message_login,
        message_upload=message_upload
        )
    with open(glo.config['RENDEREDHTMLFILENAME'], "w", encoding='utf-8') as f:
        f.write(output_from_parsed_template)
    return output_from_parsed_template


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)