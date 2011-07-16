'''
Created on 15-07-2011

@author: pszafer@gmail.com
'''

from storm.locals import Store, Int, Unicode
from storm.database import create_database

TABLES = ["media", "settings"]
database = None
store = None

class DBMedia(object):
    '''
    Database object with media information
    '''
    __storm_table__ = "media"
    
    id = Int(primary=True)
    name = Unicode()
    
    def __init__(self, name = None):
        if(name is None):
            self.name = unicode(name)
    
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
        
    def create_table_media(self):
        tablename = "media"
        variables= "(id INTEGER PRIMARY KEY, name VARCHAR)"
        self.create_table(tablename, variables)  
        
    def clear_db(self):
        #for table in TABLES:
        store.find(DBMedia).remove()
        
    
    def begin(self, db_filename, clearTable=False):
        store = self.load_db("sqlite:"+db_filename)
        self.create_table_media()
        if clearTable:
            self.clear_db()
        return store
    
    def insert(self, tableName, object):
        store.add(object)
        store.commit()
    
    def select(self, tableName, condition=None, single = True):
        table = None
        if tableName == "media":
            table = DBMedia(None)
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