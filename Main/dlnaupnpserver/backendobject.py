'''
Created on 21-08-2011

@author: xps
'''
from Database2 import DBSettings, DBContent
import os.path

def create_uuid():
        '''
        Create Your own uuid
        TODO: change to run this once and then get from db
        '''
        import uuid
        return uuid.uuid4()

class Publisher:
    def __init__(self):
        #MAke it uninheritable
        pass
    def register(self):
        #OVERRIDE
        pass
    def unregister(self):
        #OVERRIDE
        pass
    def notifyAll(self):
        #OVERRIDE
        pass

class ContentPublisher(Publisher):
    def __init__(self):
        self._listOfUsers = []
        self.postname = False
    def register(self, userObj):
        if userObj not in self._listOfUsers:
            self._listOfUsers.append(userObj)
    def unregister(self, userObj):
        self._listOfUsers.remove(userObj)
    def notifyAll(self):
        for objects in self._listOfUsers:
            objects.notify(self.postname)
    def contentChanged(self, postname=False):
        # User writes a post.
        self.postname = postname
        # When submits the post is published and notification is sent to all
        self.notifyAll()
        

class BackendObject(object):
    '''
    classdocs
    '''
    

    def __init__(self, dbCursor, server_name=None):
        '''
        Constructor
        '''
        self.dbCursor = dbCursor
        self.server_name = server_name
        self.contentObserver = ContentPublisher()
        #settings = self.get_settings()
        #if settings is None:
            #settings = self.create_settings(server_name)
        #self.settings = settings
#        if server_name is not None:
            #self.set_name(server_name)
    
    def set_name(self, name):
        settings = self.get_settings()
        settings.name = name
        #self.dbCursor.commit()
        #self.dbCursor.commit()
        #return self.settings.name
    
    def set_ip(self, ipaddress):
        #self.settings = self.dbCursor.select("settings", "id=1", True)
        #value = "10.10.10.12"
        #self.dbCursor.tlocal.store.find(self.settings, "id=1").set(ip_addr = (u"%s", value))
        settings = self.get_settings()
        settings.ip_addr = ipaddress
        #self.dbCursor.commit()
        #self.dbCursor.commit()
        #print settings.ip_addr
        
        
    def set_port(self, port):
        settings = self.get_settings()
        settings.port = int(port)
        #self.dbCursor.commit()
        
    def get_settings(self):
        return self.dbCursor.select("settings", "id=1", True)
    
    def create_settings(self, server_name):
        self.dbCursor.insert(DBSettings(server_name, create_uuid(), 'no', 'yes', None, 0, True, 300)) #TODO: change settings to be flexible
        return self.dbCursor.select("settings", "id=1", True)
        
    def get_server_name(self):
        return self.server_name
    
    def add_content_to_server(self, path):
        self.dbCursor.insert(DBContent(path))
        
    def get_content(self, single = False):
        md = self.dbCursor.select("content", single=single)
        return md
        
    def get_max_child_items(self):
        return self.settings.max_child_items
    
    def set_max_child_items(self, max):
        self.settings.max_child_items = int(max)
        self.dbCursor.commit()

    def set_Ip_Port_Name_maxChildItems(self, ip_addr, port, name, max):
        self.settings.ip_addr = unicode(ip_addr)
        self.settings.port = int(port)
        self.settings.max = int(max)
        self.settings.name = unicode(name)
        self.dbCursor.commit()
        
    def close_connection_to_db(self):
        pass
        #self.dbCursor.close_connection()
        
    def restore_connection(self):
        pass
        #self.dbCursor.connect2DB(self.dbCursor.db_path)
    def create_session(self):
        return self.dbCursor.create_session()
    def add_content(self, path):
        if os.path.isdir(path):
            for x in self.get_content():
                if x.content == path:
                    return False
            self.dbCursor.insertCommit(DBContent(path))
            self.contentObserver.contentChanged(True)
            return True
        else:
            return False
    
    def removeObject(self, object):
        self.dbCursor.removeObject(object)
    def echo(self):
        dict = {}
        dict["Status"] = "Running"
        return dict