'''
Created on 15-07-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8

'''

from storm.locals import Store, Int, Unicode
from storm.database import create_database
from storm.exceptions import IntegrityError

TABLES = ["media", "settings"]
database = None
store = None

#FIXME LOG INFORMATION ABOUT NOT CREATED DATA

class DBSettings(object):
    '''
    Database object with media information
    '''
    __storm_table__ = "settings"
    
    id = Int(primary=True)
    name = Unicode()
    uuid = Unicode()
    transcoding = Unicode()
    do_mimetype_container = Unicode()
    ip_addr = Unicode()
    port = Int()    
    enable_inotify = Int()
    max_child_items = Int()
    
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

class DBIgnorePatterns(object):
    __storm_table__ = "ignorepatterns"
    
    id = Int(primary=True)
    ignore_pattern = Unicode()
    
    def __init__(self, ignore_patterns = None):
        self.ignore_patterns = unicode(ignore_patterns)

class DBContent(object):
    '''
    Database object with storing of folders to get media content from
    '''
    
    __storm_table__ = "content"
    
    id = Int(primary=True)
    content = Unicode()
    
    def __init__(self, content = None):
        self.content = unicode(content)

class DBCursor(object):
    '''
    Cursor to work with sqlite3 database
    '''
    def load_db(self, uri):
        global database
        global store
        
        if not store:
            database = create_database(uri)
            store = Store(database)
        return store
    
    def create_table(self, tablename, variables):
        store.execute("CREATE TABLE IF NOT EXISTS " + tablename + " " + variables)
        
    def create_table_settings(self):
        tablename = "settings"
        variables= "(id INTEGER PRIMARY KEY, \
            name VARCHAR NOT NULL UNIQUE,\
            uuid VARCHAR UNIQUE,\
            transcoding VARCHAR UNIQUE,\
            do_mimetype_container VARCHAR UNIQUE,\
            ip_addr VARCHAR UNIQUE,\
            port INTEGER,\
            enable_inotify INTEGER,\
            max_child_items INTEGER)"
        self.create_table(tablename, variables)  
    
    def create_table_content(self):
        tablename = "content"
        variables= "(id INTEGER PRIMARY KEY, content VARCHAR NOT NULL UNIQUE)"
        self.create_table(tablename, variables)  
        
    def create_table_ignore_patterns(self):
        tablename = "ignorepatterns"
        variables= "(id INTEGER PRIMARY KEY, ignorepatterns VARCHAR NOT NULL UNIQUE)"
        self.create_table(tablename, variables)
        
    def clear_db(self):
        #for table in TABLES:
        store.find(DBSettings).remove()
        
    
    def begin(self, db_filename, clearTable=False):
        store = self.load_db("sqlite:"+db_filename)
        self.create_table_settings()
        self.create_table_content()
        self.create_table_ignore_patterns()
        if clearTable:
            self.clear_db()
        return store
    
    def insert(self, object):
        try:
            store.add(object)
            store.commit()
        except IntegrityError:
            pass
    
    def select(self, tableName, condition=None, single = True):
        table = None
        if tableName == "settings":
            table = DBSettings()
        elif tableName == "content":
            table = DBContent()
        elif tableName == "ignore_patterns":
            table = DBIgnorePatterns()
        if not condition:
            if single:
                return store.find(type(table)).any()
            else:
                return store.find(type(table))
        else:
            if single:
                return store.find(type(table), condition).any()
            else:
                return store.find(type(table), condition)