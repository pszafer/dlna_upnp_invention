'''
Created on 15-07-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8

'''

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine import create_engine
from sqlalchemy.types import Integer, String
from sqlalchemy.schema import Sequence, Column, Table, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(autoflush=True, autocommit=True))
Base = declarative_base()

#FIXME LOG INFORMATION ABOUT NOT CREATED DATA



class DBSettings(Base):
    '''
    Database object with media information
    '''
    __tablename__ = "settings"
    
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(30))
    uuid = Column(String(120))
    transcoding = Column(String(5))
    do_mimetype_container = Column(String(5))
    ip_addr = Column(String(30))
    port = Column(Integer)
    enable_inotify = Column(Integer)
    max_child_items = Column(Integer)
    
    def __init__(self, 
                 name = None, 
                 uuid = None, 
                 transcoding = "no", 
                 do_mimetype_container = "yes", 
                 ip_addr = None, 
                 port = 0, 
                 enable_inotify = True,
                 max_child_items = 300):
        self.name = unicode(name)
        self.uuid = unicode(uuid)
        self.transcoding = unicode(transcoding)
        self.do_mimetype_container = unicode(do_mimetype_container)
        self.ip_addr = unicode(ip_addr)
        self.port = port
        self.enable_inotify = int(enable_inotify)
        self.max_child_items = int(max_child_items)
        
    
    def getjson(self):
        dict = {}
        dict['name'] = self.name
        dict['uuid'] = self.uuid
        dict['transcoding'] = self.transcoding
        dict['do_mimetype_container'] = self.do_mimetype_container 
        dict['ip_addr'] = self.ip_addr 
        dict['port'] = self.port 
        dict['enable_inotify'] = self.enable_inotify
        dict['max_child_items'] = self.max_child_items
        return dict

class DBIgnorePatterns(Base):
    __tablename__ = "ignorepatterns"
    
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    ignore_pattern = Column(String(120))
    
    def __init__(self, ignore_patterns = None):
        self.ignore_patterns = unicode(ignore_patterns)

class DBContent(Base):
    '''
    Database object with storing of folders to get media content from
    '''
    
    __tablename__ = "content"
    
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    content = Column(String(180))
    
    def __init__(self, content = None):
        self.content = content
        
    def getjson(self):
        dict = {}
        dict['content'] = self.content
        return dict

class DBCursor(object):
    '''
    Cursor to work with sqlite3 database
    '''
    
    
    def __init__(self, db_path=None):
        self.db_path = db_path
        uri = "sqlite:///"+os.path.abspath(db_path)
        self.isClosed = False
        engine = create_engine(uri)
        Base.metadata.create_all(engine)
        Session.configure(bind=engine)        
        self.session = Session()
    
    def commit(self):
        self.session.expunge_all()
        self.session.commit()
        self.session.close()
    
    def update(self, object):
        self.session.expunge_all()
        self.session.add(object)
        self.session.commit()
        self.session.close()
    
    def set_ip(self, ipaddress):
        #self.info("Setting ip to use by Media server")
        self.session.expunge_all()
        settings = self.session.query(DBSettings).first()
        settings.ip_addr = ipaddress
        self.session.flush()
        self.session.close()
    
    def set_port(self, port):
        #self.info("Setting ip to use by Media server")
        self.session.expunge_all()
        settings = self.session.query(DBSettings).first()
        settings.port = port
        self.session.flush()
        self.session.close()
        
    def insert(self, object):
        self.session.expunge_all()
        self.session.add(object)
        self.session.close()
    
    def insertCommit(self, object):
        self.session.expunge_all()
        self.session.add(object)
        self.session.flush()
        id = object.id
        self.session.close()
        return id
    
    def removeObject(self, type, id):
        #table = None
        id = str(id)
        object= None
        if type == "settings":
            #table = DBSettings()
            object = self.select("settings", "id="+id)
        elif type == "content":
            #table = DBContent()
            object = self.session.query("content", "id="+id)
        elif type == "ignore_patterns":
            #table = DBIgnorePatterns()
            object = self.session.query("ignore_patterns", "id="+id)
        self.session.expunge_all()
        self.session.delete(object)
        self.session.flush()
        self.session.close()
    
    def select(self, tableName, condition=None, single = True):
        session = self.session
        table = None
        if tableName == "settings":
            table = DBSettings()
        elif tableName == "content":
            table = DBContent()
        elif tableName == "ignore_patterns":
            table = DBIgnorePatterns()
        self.session.expunge_all()
        if not condition:
            if single:
                return session.query(type(table)).first()
            else:
                return session.query(type(table)).all()
        else:
            if single:
                return session.query(type(table)).filter(condition).first()
            else:
                return session.query(type(table)).filter(condition).all()
        session.flush()
        session.close()