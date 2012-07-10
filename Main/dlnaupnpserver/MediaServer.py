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
from Database2 import DBCursor, DBContent
from JSONRPCServer import JsonRpcApp
from backendobject import BackendObject
from modCoherence import log
from threading import Lock
import os.path
import threading
import signal

import sys
import time
from twisted.internet import reactor, defer
def set_exit_handler(func):
    if os.name == "nt":
        try:
            import win32api
            win32api.SetConsoleCtrlHandler(func, True)
        except ImportError:
            version = ".".join(map(str, sys.version_info[:2]))
            raise Exception("pywin32 not installed for Python " + version)
    else:
        signal.signal(signal.SIGUSR1, func)


def write_settings_to_file(external_address, media_db_path):
    file = open(".settings.dat", "w")
    file.write("Do not change anything in this file!!!\n")
    file.write(str(external_address).encode("hex")+"\n")
    file.write(str(media_db_path).encode("hex"))
    file.close()

#class SocketServer(ThreadedJsonServer):
#    def __init__(self):
#        super(SocketServer, self).__init__()
#        self.timeout = 2.0
#    def processMessage(self, obj):
#        if obj != '':
#            if obj['message'] == "new connection":
#                print "ttt"

class MediaServer(log.Loggable):
    '''
    Class which starts server with own MediaStore
    '''
    logCategory = 'dlna_upnp_MediaServer'
    
    
    def __init__(self, backendObject=None, lock=None):
        self.coherence = None
        self.backendObject = backendObject
        self.lock = lock
        self.lock.acquire()
    
    def run(self):
        '''
        Create coherence and run media server
        '''
        #reactor install
        settings = self.backendObject.get_settings()
        md = self.backendObject.get_content()
        content = []
        for con in md:
            content.append(con.content)
        if len(content) == 0:
            self.lock.release()
            self.error('Content is empty. Nothing to share')
            return
        self.coherence = self.get_coherence(None, None, settings.transcoding)
        #self.dbCursor = dbCursor
        if self.coherence is None:
            self.lock.release()
            self.error("None Coherence")
            return
        self.info("RUNNING")
        settings = self.backendObject.get_settings()
        md = self.backendObject.get_content()
        self.server = self.create_MediaServer(self.coherence, md, content, settings)
        self.backendObject.close_connection_to_db()
        self.info(self.backendObject.dbCursor.db_path)
        self.lock.release()
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
                            'interface' : 'wlan0'
                            }
        if port:
            coherence_config['serverport'] = port
        if ip_addr:
            coherence_config['interface'] = ip_addr
        coherence_instance = Coherence(coherence_config)
        self.backendObject.set_ip(coherence_instance.hostname)
        self.backendObject.set_port(coherence_instance.web_server_port)
        return coherence_instance
    
    def create_MediaServer(self, coherence, dbContent, content, settings):
        '''
        Run MediaStore and Coherence server
        @param coherence:coherence instance from get_coherence
        TODO: get data from db, not from strings
        '''
        from modCoherence.upnp.devices.media_server import MediaServer as CoherenceMediaServer
        #from fs_storage import FSStore as MediaStore
        from MediaStorage import MediaStore
        
        
        kwargs = {}
        kwargs['settings'] = settings
        kwargs['uuid'] = str(settings.uuid)
        self.warning("MediaServer run, what I got: %r", kwargs)
        name = settings.name
        if name:
            name = name.replace('{host}', coherence.hostname)
            kwargs['name'] = "test"
        kwargs['content']= content
        kwargs['dbContent'] = dbContent
        kwargs['urlbase'] = coherence.hostname
        kwargs['transcoding'] = settings.transcoding
        logofile = "file://"+os.path.abspath("logo2.png")
        kwargs['icons'] = [
                           {'mimetype' : 'image/png',
                            'url': logofile,
                            'width':'48',
                            'height':'48',
                            'depth':'24'}
                           ,
                           {'mimetype' : 'image/png',
                            'url': logofile,
                            'width':'120',
                            'height':'120',
                            'depth':'24'}]
        if settings.enable_inotify == 0:
            kwargs['enable_inotify'] = "no" 
        else: 
            kwargs['enable_inotify'] = "yes"
        kwargs['do_mimetype_container'] =  settings.do_mimetype_container
        kwargs['max_child_items'] = settings.max_child_items
        kwargs['backendObject'] = self.backendObject
        server = CoherenceMediaServer(coherence, MediaStore, **kwargs)         #TODO change here
        return server
    def stopMediaServer(self):
        self.info("SERVER NOT WORKING ANYMORE")
        self.server.unregister()
    
class Runserver(threading.Thread):

    def __init__(self, mediaServer):
        self.mediaServer = mediaServer
        self.reactor = reactor
        threading.Thread.__init__(self)
        self.finished = threading.Event()
        self.setDaemon(True)
        
    def run(self):
        self.reactor.callWhenRunning(self.mediaServer.run)
        #self.reactor._disconnectedDeferred = defer.Deferred()
        self.reactor.run(installSignalHandlers=0)
    
    def stop(self):
        self.mediaServer.stopMediaServer()
        self.reactor.stop()
        self.finished.set()
        

class RunRPCServer():
    def __init__(self, backendObject):
        self.backendObject = backendObject
    def run(self):
        import optparse
        from wsgiref import simple_server
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] MODULE:EXPRESSION")
        parser.add_option(
            '-p', '--port', default='7777',
            help='Port to serve on (default 7777)')
        parser.add_option(
            '-H', '--host', default='127.0.0.1',
            help='Host to serve on (default localhost; 0.0.0.0 to make public)')
        options, _ = parser.parse_args()
        #if not args or len(args) > 1:
        #    print 'You must give a single object reference'
        #    parser.print_help()
        #    sys.exit(2)
        app = JsonRpcApp(self.backendObject)
        server = simple_server.make_server(
            options.host, int(options.port),
            app)
        print 'Serving on http://%s:%s' % (options.host, options.port)
        self.backendObject.set_name("Nazwa serwera")
        try:
            server.serve_forever()
        except Exception:
            pass 
if __name__ == "__main__":
    path_to_db = "media.db"
    dbpath = os.path.abspath(path_to_db)
    lock = Lock()
    
    dbCursor = DBCursor(db_path=dbpath)
    backendObject = BackendObject(dbCursor, "test")
    
    
    #EXPUNGE HERE?
    #
    #backendObject.close_connection_to_db()
    mediaServer = MediaServer(backendObject=backendObject, lock=lock)
    s = Runserver(mediaServer)
    s.start()
    def on_exit(sig, func=None):
        print "Exiting"
        s.stop()
        print "Bye Bye"
        sys.exit(0)
    set_exit_handler(on_exit)
    lock.acquire()
    time.sleep(3)
    try:
        r = RunRPCServer(backendObject)
        r.run()
    finally:
        lock.release()
