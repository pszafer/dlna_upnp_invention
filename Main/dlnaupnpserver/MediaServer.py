'''
Created on 08-07-2011
@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8

'''
#import Database
#from Database import DBCursor, DBSettings
from Database import DBCursor, DBSettings, DBContent

from modCoherence import log
import sys
import os.path
from JSONRPCServer import ThreadedJsonServer

def create_uuid():
        '''
        Create Your own uuid
        TODO: change to run this once and then get from db
        '''
        import uuid
        return uuid.uuid4()

def write_settings_to_file(external_address, media_db_path):
    file = open(".settings.dat", "w")
    file.write("Do not change anything in this file!!!\n")
    file.write(str(external_address).encode("hex")+"\n")
    file.write(str(media_db_path).encode("hex"))
    file.close()

class SocketServer(ThreadedJsonServer):
    def __init__(self):
        super(SocketServer, self).__init__()
        self.timeout = 2.0
    def processMessage(self, obj):
        if obj != '':
            if obj['message'] == "new connection":
                print "ttt"

class MediaServer(log.Loggable):
    '''
    Class which starts server with own MediaStore
    '''
    logType = 'dlna_upnp_MediaServer'
    
    
    def __init__(self, dbCursor = None):
        self.coherence = None
        if dbCursor is None:
            self.dbCursor = DBCursor()
        else:
            self.dbCursor = dbCursor
    def run(self):
        '''
        Create coherence and run media server
        '''
        #reactor install
        settings = self.dbCursor.select("settings", "id=1", True)
        self.coherence = self.get_coherence(settings.ip_addr, settings.port, settings.transcoding)
        #self.dbCursor = dbCursor
        if self.coherence is None:
            self.error("None Coherence")
            return
        self.warning("RUNNING")
        self.server = self.create_MediaServer(self.coherence, settings)
    
    
    
    def get_coherence(self, ip_addr, port, transcoding="no"):
        '''
        Create instance of Coherence
        '''
        try:
            from modCoherence.base import Coherence
        except ImportError, e:
            self.error("Coherence not found %d", e)
            return None
        coherence_config = {
                            'logmode' : 'info',
                            'controlpoint' : 'yes',
                            'plugins' : {},
                            'transcoding' : transcoding,
                            }
        if port:
            coherence_config['serverport'] = port
        if ip_addr:
            coherence_config['interface'] = ip_addr
        coherence_instance = Coherence(coherence_config)
        write_settings_to_file(coherence_instance.external_address, self.dbCursor.db_path)
        return coherence_instance
    
    def create_MediaServer(self, coherence, settings):
        '''
        Run MediaStore and Coherence server
        @param coherence:coherence instance from get_coherence
        TODO: get data from db, not from strings
        '''
        from modCoherence.upnp.devices.media_server import MediaServer as CoherenceMediaServer
        #from fs_storage import FSStore as MediaStore
        from MediaStorage import MediaStore
        
        
        kwargs = {}
        kwargs['uuid'] = settings.uuid
        uuid = str(kwargs['uuid'])
        kwargs['uuid'] = uuid
        self.warning("MediaServer run, what I got: %r", kwargs)
        name = settings.name
        if name:
            name = name.replace('{host}', coherence.hostname)
            kwargs['name'] = name
        md = self.dbCursor.select("content", single = False)
        content = []
        for con in md:
            content.append(con.content)
        kwargs['content']= content
        kwargs['urlbase'] = coherence.hostname
        kwargs['transcoding'] = settings.transcoding
        kwargs['icons'] = [
                           {'url': "file://"+os.path.abspath("logo2.png"),
                            'mimetype' : 'image/png'}
                           ,]
        if settings.enable_inotify == 0:
            kwargs['enable_inotify'] = "no" 
        else: 
            kwargs['enable_inotify'] = "yes"
        kwargs['do_mimetype_container'] =  settings.do_mimetype_container
        kwargs['max_child_items'] = settings.max_child_items
        server = CoherenceMediaServer(coherence, MediaStore, **kwargs)         #TODO change here
        return server
    
  
        
from twisted.internet import reactor
path_to_db = "media.db"
dbpath = os.path.abspath(path_to_db)
PROJECT_DIR = os.path.normpath(os.path.dirname(__file__))
new_dir, _ = os.path.split(PROJECT_DIR)
print sys.path
sys.path.insert(0, new_dir)
print sys.path
dbCursor = DBCursor(db_path=dbpath)

dbCursor.begin(dbpath, False)
#dbCursor.insert(DBContent("/home/xps/Wideo/test"))
#dbCursor.insert(DBSettings("GreatServer", create_uuid(), 'no', 'yes', None, 0, True, 300))

#jsonServer = SocketServer()
#jsonServer.start()

mediaServer = MediaServer(dbCursor)
reactor.callWhenRunning(mediaServer.run)
reactor.run()
