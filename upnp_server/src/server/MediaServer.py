'''
Created on 08-07-2011

@author: xps
'''
import Database
from server.Database import DBCursor, DBMedia

parameters = {
              'port' : 0,
              'ip_addr': None,
              }

from coherence import log
import storm

class MediaServer(log.Loggable):
    logType = 'dlna_upnp_MediaServer'
    
    
    def __init__(self):
        self.coherence = None
        #create config
    
    def run(self):
        #reactor install
        self.coherence = self.get_coherence()
        #self.dbCursor = dbCursor
        if self.coherence is None:
            self.error("None Coherence")
            return
        self.warning("RUNNING")
        self.server = self.create_MediaServer(self.coherence)
    
    def create_uuid(self):
        import uuid
        return uuid.uuid4()
    
    def get_coherence(self):
        try:
            from coherence.base import Coherence
        except ImportError, e:
            self.error("Coherence not found %d", e)
            return None
        coherence_config = {
                            'logmode' : 'info',
                            'controlpoint' : 'yes',
                            'plugins' : {},
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
        from coherence.upnp.devices.media_server import MediaServer
        from MediaStorage import MediaStore
        kwargs = {
                  'version' : 2,
                  'no_thread_needed' : True,
                  'db' : None,
                  'plugin' : self,
                  }
        kwargs['uuid'] = self.create_uuid()
        uuid = str(kwargs['uuid'])
        kwargs['uuid'] = uuid
        self.warning("MediaServer run, what I got: %r", kwargs)
        name = "ServerUPNP"
        if name:
            name = name.replace('{host}', coherence.hostname)
            kwargs['name'] = name
        #kwargs['dbCursor'] = dbCursor
        
        server = MediaServer(coherence, MediaStore, **kwargs)         #TODO change here
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