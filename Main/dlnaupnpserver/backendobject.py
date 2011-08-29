'''
Created on 21-08-2011

@author: xps
'''
from Database2 import DBSettings, DBContent
import os.path
from modCoherence import log

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
        

class BackendObject(log.Loggable):
    '''
    classdocs
    '''
    logCategory = 'dlna_upnp_backend'

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
        self.info("Setting name of Media server")
        settings = self.get_settings()
        settings.name = name
        #self.dbCursor.commit()
        #self.dbCursor.commit()
        #return self.settings.name
    
    def set_ip(self, ipaddress):
        self.dbCursor.set_ip(ipaddress)
        
    def set_port(self, port):
        self.dbCursor.set_port(port)
        
    def get_settings(self):
        self.info("Returning settings")
        return self.dbCursor.select("settings", "id=1", True)
    
    def create_settings(self, server_name):
        self.info("Creating settings")
        self.dbCursor.insert(DBSettings(server_name, create_uuid(), 'no', 'yes', None, 0, True, 300)) #TODO: change settings to be flexible
        return self.dbCursor.select("settings", "id=1", True)
        
    def get_server_name(self):
        self.info("Returning server name")
        return self.server_name
    
    def add_content_to_server(self, path):
        self.info("Added content to share: %s", path)
        self.dbCursor.insert(DBContent(path))
        
    def get_content(self, single = False):
        self.info("Returning all shared content")
        md = self.dbCursor.select("content", single=single)
        return md
        
    def get_max_child_items(self):
        max = self.settings.max_child_items
        self.info("Return number of children each media store can have, %s", max)
        return max
    
    def set_max_child_items(self, max):
        self.info("Set up number of children each media store can have, %s", max)
        self.settings.max_child_items = int(max)
        self.dbCursor.commit()

    def set_Ip_Port_Name_maxChildItems(self, ip_addr, port, name, max):
        self.info("Setting many settins: ip - %s, port - %s, name - %s, max child items - %s", ip_addr, port, name, max)
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
        self.info("Added content to share: %s", path)
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
        self.info("ECHO")
        dict = {}
        dict["Status"] = "Running"
        return dict
    
    def getpid(self):
        dict = {}
        dict['PID'] = os.getpid()
        return dict
    
    def getaddress(self):
        settings = self.get_settings()
        dict = {}
        dict['ip'] = settings.ip_addr
        dict['port'] = str(settings.port)
        self.info("Returning address and port of webserver, ip - %s, port - %s", settings.ip_addr, settings.port)
        return dict