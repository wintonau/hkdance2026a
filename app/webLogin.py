import hkdanceGlobal as glo
import sqlalchemy as sa
import datetime
import sqlalchemy.orm as saorm
from flask import Flask
from flask_bcrypt import Bcrypt
from userClass import user, engine

app = Flask(__name__, static_url_path='')
bcrypt = Bcrypt(app)


#Session = saorm.sessionmaker(bind=engine)
#s = saorm.Session(engine)
#aaa=s.query(user).first()
#aaa.login

def EncryptPassword(pw):
    return bcrypt.generate_password_hash(pw, 12)

def GetAllLogin():
    with saorm.Session(engine) as s:
        a = s.query(user.login, user.showallowed).all()
    return a


def QueryLogin(thisLogin):
    with saorm.Session(engine) as s:
        a = s.query(user).filter(user.login.in_([thisLogin])).first()
    return a

def DeleteLogin(thisLogin):
    with saorm.Session(engine) as s:
        s.query(user).filter(user.login == thisLogin).delete()
        s.commit()

def PasswordCorrectORM(thisLogin, thisPassword):
    pw =QueryLogin(thisLogin).password
    return bcrypt.check_password_hash(pw, thisPassword)

def AddLoginORM(thisLogin, thisPassword, thisshowallowed):

    newLogin = user(
        login = thisLogin,
        password = EncryptPassword(thisPassword),
        accountcreated = datetime.datetime.now(),
        lastaccess=None, accesscount=0,
        showallowed=thisshowallowed)
    with saorm.Session(engine) as s:
        s.add(newLogin)
        s.commit()


def UpdateShowAllowed(thisLogin, thisShowAllowed):
    with saorm.Session(engine) as s:
        s.execute(
            sa.update(user).
            where(user.login == thisLogin).
            values(showallowed=thisShowAllowed))
        s.commit()


def UpdatePasswordORM(thisLogin, thisPassword):
    with saorm.Session(engine) as s:
        s.execute(
            sa.update(user).
            where(user.login == thisLogin).
            values(password=EncryptPassword(thisPassword)))
        s.commit()

def UpdateLastAccessdORM(thisLogin):
    with saorm.Session(engine) as s:
        s.execute(
            sa.update(user).
            where(user.login == thisLogin).
            values(lastaccess=datetime.datetime.now(), accesscount=user.accesscount+1))
        s.commit()

if QueryLogin(glo.config['SULOGIN'])==None:
    AddLoginORM(glo.config['SULOGIN'], glo.config['SUPASSWORD'], [])
else:
    UpdatePasswordORM(glo.config['SULOGIN'], glo.config['SUPASSWORD'])


if QueryLogin(glo.config['ADMINLOGIN'])==None:
    AddLoginORM(glo.config['ADMINLOGIN'], glo.config['ADMINPASSWORD'], [])
else:
    UpdatePasswordORM(glo.config['ADMINLOGIN'], glo.config['ADMINPASSWORD'])

# =============================================================================
# def LoginExist(thisLogin):
#     engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL_HKDANCE'], echo=False)
#     #metadata=sa.MetaData(engine)
#     #t = sa.Table('user', metadata, autoload=True, autoload_with=engine)
#     stmt = sa.text("select login from user where login=:thisLogin")
#     with saorm.Session(engine) as s:
#         result = s.execute(stmt, [{"thisLogin":thisLogin}])
#     return len(result.all())>0
#
# def PasswordCorrect(thisLogin, thisPassword):
#     engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL_HKDANCE'], echo=False)
#     #metadata=sa.MetaData(engine)
#     #t = sa.Table('user', metadata, autoload=True, autoload_with=engine)
#     stmt = sa.text("select password from user where login=:thisLogin")
#     with saorm.Session(engine) as s:
#         result = s.execute(stmt, [{"thisLogin":thisLogin}])
#     return result.first()[0]==thisPassword
#
# def AddLogin(thisLogin, thisPassword):
#     engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL_HKDANCE'], echo=False)
#     metadata=sa.MetaData(engine)
#     t = sa.Table('user', metadata, autoload=True, autoload_with=engine)
#     stmt = (sa.insert(t).values(login=thisLogin, password=EncryptPassword(thisPassword), accountcreated=datetime.datetime.now()))
#     engine.connect().execute(stmt)
#     engine.connect().close()
#
# def UpdatePassword(thisLogin, thisPassword):
#     engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL_HKDANCE'], echo=False)
#     stmt = sa.text("update user set password=:thisPassword where login=:thisLogin")
#     with saorm.Session(engine) as s:
#         result = s.execute(stmt, [{"thisLogin":thisLogin, "thisPassword":EncryptPassword(thisPassword)}])
#         s.commit()
#
# def UpdateLastAccess(thisLogin):
#     engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL_HKDANCE'], echo=False)
#     stmt = sa.text("update user set lastaccess=:timeNow where login=:thisLogin")
#     with saorm.Session(engine) as s:
#         result = s.execute(stmt, [{"thisLogin":thisLogin, "timeNow":datetime.datetime.now()}])
#         s.commit()
#
#
# =============================================================================
