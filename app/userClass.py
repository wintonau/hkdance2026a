import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin

import hkdanceGlobal as glo

Base = declarative_base()
print(glo.config['SQLALCHEMY_ENGINECREDENTIAL'])
engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL'], echo=False)

class user(UserMixin, Base):
    __table__ = sa.Table(glo.config['LOGINDBTABLE'], Base.metadata, autoload_with=engine)
    def __init__(self, login, password, accountcreated, lastaccess, accesscount, showallowed):
        self.login = login
        self.password = password
        self.accountcreated = accountcreated
        self.lastaccess = lastaccess
        self.accesscount = accesscount
        self.showallowed = showallowed
    def get_id(self):         
        return str(self.login)