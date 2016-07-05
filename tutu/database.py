from tutu import tutuconfig;
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
import datetime;

def get_session():
	return _DBSession();

def _init_db():
	if _is_initialised():
		return
	Base.metadata.create_all(_engine);
	return

def _is_initialised():
	from sqlalchemy.engine.reflection import Inspector
	inspector = Inspector.from_engine(_engine);
	return 'user' in inspector.get_table_names()

def auditlog(username, message):
	alog = AuditLog();
	alog.uname = username;
	alog.action = message;
	alog.date = datetime.now();
	
	session = get_session();
	session.add(alog);
	session.commit();

def check_login(username, password):
	session = get_session();
	results = session.query(User).filter(User.uname == username).all();
	if password != 'letmein':
		results = None;
	return results is not None;

Base = declarative_base();


class User(Base):
	__tablename__ = 'users';

	id = Column(Integer, primary_key = True);
	uname = Column(String);
	pword = Column(String);
	fname = Column(String);
	lname = Column(String);
	email = Column(String);

class AuditLog(Base):
	__tablename__ = 'auditlog';

	id = Column(Integer, primary_key = True);
	uname = Column(String);
	action = Column(String);
	date = Column(DateTime);

_uri = tutuconfig.get('uri', 'database');

_engine = create_engine(_uri);
_DBSession = sessionmaker(bind=_engine);
_init_db();

# vim: set ts=2: