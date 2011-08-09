'''
Created on 08-07-2011

@author: xps
'''
import Database
from server.Database import DBCursor, DBMedia


'''
Main parameters, not used
'''
parameters = {
              'port' : 0, 
              'ip_addr': None,
              }

from coherence import log


class MediaServer(log.Loggable):
    '''
    Class which starts server with own MediaStore
    '''
    logType = 'dlna_upnp_MediaServer'
    
    
    def __init__(self):
        self.coherence = None
    
    def run(self):
        '''
        Create coherence and run media server
        '''
        #reactor install
        self.coherence = self.get_coherence()
        #self.dbCursor = dbCursor
        if self.coherence is None:
            self.error("None Coherence")
            return
        self.warning("RUNNING")
        self.server = self.create_MediaServer(self.coherence)
    
    def create_uuid(self):
        '''
        Create Your own uuid
        TODO: change to run this once and then get from db
        '''
        import uuid
        return uuid.uuid4()
    
    def get_coherence(self):
        '''
        Create instance of Coherence
        '''
        try:
            from coherence.base import Coherence
        except ImportError, e:
            self.error("Coherence not found %d", e)
            return None
        coherence_config = {
                            'logmode' : 'info',
                            'controlpoint' : 'yes',
                            'plugins' : {},
                            'transcoding' : 'yes',
                            }
        serverport = parameters.get("port")
        if serverport:
            coherence_config['serverport'] = serverport
        ip_addr = parameters.get("ip_addr")
        if ip_addr:
            coherence_config['interface'] = ip_addr
        coherence_instance = Coherence(coherence_config)
        return coherence_instance
    
    def create_MediaServer(self, coherence):
        '''
        Run MediaStore and Coherence server
        @param coherence:coherence instance from get_coherence
        TODO: get data from db, not from strings
        '''
        from coherence.upnp.devices.media_server import MediaServer as CoherenceMediaServer
        #from fs_storage import FSStore as MediaStore
        from MediaStorage import MediaStore
        kwargs = {}
        kwargs['uuid'] = self.create_uuid()
        uuid = str(kwargs['uuid'])
        kwargs['uuid'] = uuid
        self.warning("MediaServer run, what I got: %r", kwargs)
        name = "ServerUPNP"
        if name:
            name = name.replace('{host}', coherence.hostname)
            kwargs['name'] = name
        content = ["/home/xps/Wideo/test/"]#, "/home/xps/Obrazy/majowka2011/connect", "/home/xps/Muzyka/mp3"]
        kwargs['content']= content
        kwargs['urlbase'] = coherence.hostname
        kwargs['transcoding'] = 'no'
        kwargs['do_mimetype_container'] =  True
        kwargs['max_child_items'] = 10
        #kwargs['dbCursor'] = dbCursor
        
        server = CoherenceMediaServer(coherence, MediaStore, **kwargs)         #TODO change here
        return server
    
  
        
from twisted.internet import reactor

#dbCursor = DBCursor()
#dbCursor.begin("media.db", True)
#dbCursor.insert("media", DBMedia("aaa"))
#dbCursor.insert("media", DBMedia("bbb"))
#md = dbCursor.select("media", single = True)
#if isinstance(md, DBMedia):
#    print "One something %r, %s" % (md.id, md.name)
#else:
#    if md is not None:
#        for i in md:
#            print "something %r, %s" % (i.id, i.name)


mediaServer = MediaServer()
reactor.callWhenRunning(mediaServer.run)
reactor.run()