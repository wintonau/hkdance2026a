import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
import hkdanceGlobal as glo

Base = declarative_base()
print(glo.config['SQLALCHEMY_ENGINECREDENTIAL'])
engine = sa.create_engine(glo.config['SQLALCHEMY_ENGINECREDENTIAL'], echo=False)

class user(Base):
    __table__ = sa.Table(glo.config['LOGINDBTABLE'], Base.metadata, autoload_with=engine)
    def __init__(self, login, password, accountcreated, lastaccess, accesscount, showallowed):
        self.login = login
        self.password = password
        self.accountcreated = accountcreated
        self.lastaccess = lastaccess
        self.accesscount = accesscount
        self.showallowed = showallowed
    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.login)