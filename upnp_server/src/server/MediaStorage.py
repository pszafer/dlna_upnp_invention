'''
Created on 09-07-2011

@author: xps
'''

import mimetypes
from backend import LazyContainer
mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('audio/x-musepack', '.mpc')
mimetypes.add_type('audio/x-wavpack', '.wv')
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/divx', '.divx')
mimetypes.add_type('video/divx', '.avi')
mimetypes.add_type('video/x-matroska', '.mkv')
mimetypes.add_type('text/plain', '.srt')

from coherence.backend import BackendItem, AbstractBackendStore, Container
import coherence.extern.louie as louie

from coherence.upnp.core.DIDLLite import classChooser as upnpItems

class MediaContainer(BackendItem):
    logType = 'dlna_upnp_MediaContainer'
    
    def __init__(self, id, ):
        None
        

class MediaStore(AbstractBackendStore):
    logType = 'dlna_upnp_MediaStore'
    implements = ['MediaServer']
    
    def __init__(self, server, **kwargs):
        AbstractBackendStore.__init__(self, server, **kwargs)
        self.next_id = 1000
        self.warning("MediaStore init, what I got: %r", kwargs)
        self.db = kwargs['db']
        self.name = kwargs.get('name', 'Media')
        self.content = kwargs.get('content',None)
        if self.content != None:
            if(isinstance(self.content, basestring)):
                self.content = [self.content]
            l = []
            for i in self.content:
                l += i.split(',')
            self.content = l
        
        self.plugin = kwargs['plugin']
        self.urlbase = kwargs.get('urlbase','')
        if( len(self.urlbase) > 0 and self.urlbase[len(self.urlbase)-1] != '/'):
            self.urlbase += '/'
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "TYT"
            
            
        rootContainer = Container(None, "Test")
        self.set_root_item(rootContainer)
        self.refresh = int(kwargs.get('refresh',60))*60
        self.nextContainer = LazyContainer(rootContainer, 'My Album2', None, self.refresh, self.retrieveAlbums())
        rootContainer.add_child(self.nextContainer)
        self.init_completed()
    
    def retrieveAlbums(self, parent=None):
        albums = {"1":"1", "2":"2", "3":"3", "4":"4",}
        return albums
    
    def upnp_init(self):
        self.current_connection_id = None
        if self.server:
            self.server.connection_manager_server.set_variable(0, 'SourceProtocolInfo',
                        'http-get:*:image/jpeg:*,'
                        'http-get:*:image/gif:*,'
                        'http-get:*:image/png:*',
                        default=True)
            self.server.content_directory_server.set_variable(0, 'SystemUpdateID', self.update_id)
    
    def getNextID(self):
        ret = self.next_id
        self.next_id += 1
        return ret
    