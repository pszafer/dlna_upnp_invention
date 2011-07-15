'''
Created on 08-07-2011

@author: xps
'''

parameters = {
              'port' : 0,
              'ip_addr': None,
              }

from coherence import log
import sqlite3

class MediaServer(log.Loggable):
    logType = 'dlna_upnp_MediaServer'
    
    def __init__(self):
        self.coherence = None
        #create config
    
    def run(self):
        #reactor install
        self.coherence = self.get_coherence()
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
        server = MediaServer(coherence, MediaStore, **kwargs)         #TODO change here
        return server
    
    def create_MediaRenderer(self, coherence):
        from coherence.upnp.devices.media_renderer import MediaRenderer
        #TODO import VLC | MusicPlayer | Picture
        #renderer = MediaRenderer(coherence, "PLayer", **kwargs) #TODOchange kwargs
        
        #FIXME create sqllite database
        #FIXME we will have server there

from twisted.internet import reactor
mediaServer = MediaServer()
reactor.callWhenRunning(mediaServer.run)
reactor.run()