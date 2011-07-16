'''
Created on 09-07-2011

@author: xps
'''

import mimetypes
from backend import LazyContainer
from server.Database import DBMedia
from coherence.upnp.core import DIDLLite
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
    
    def __init__(self, id, parent_id, name, children_callback=None, store=None, play_container=False):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        if children_callback != None:
            self.children = children_callback
        self.store = store
        self.play_container = play_container
        
    def add_child(self, child):
        self.children.append(child)

    def get_children(self, start=0, end=0):
        return BackendItem.get_children(self, start, end)


    def get_child_count(self):
        if callable(self.children):
            return len(self.children())
        else:
            return len(self.children)


    def get_item(self):
        item = DIDLLite.Container(self.id, self.parent_id, self.name)
        item.childCount = self.get_child_count()
        return item

    def get_name(self):
        return self.name
    
    def get_id(self):
        return self.id
        

class MediaStore(AbstractBackendStore):
    logType = 'dlna_upnp_MediaStore'
    implements = ['MediaServer']
    
    def __init__(self, server, **kwargs):
        AbstractBackendStore.__init__(self, server, **kwargs)
        self.next_id = 1000
        self.warning("MediaStore init, what I got: %r", kwargs)
        self.db = kwargs['db']
        self.name = kwargs.get('name', 'Media')
        self.dbCursor = kwargs['dbCursor']
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
            
            
        self.rootContainer = Container(None, "Test")
        self.set_root_item(self.rootContainer)
        self.refresh = int(kwargs.get('refresh',60))*60
        self.nextContainer = MediaContainer(id=1,parent_id=0, children_callback=["1", "2", "3"], name="tttt")
        self.secondContainer = MediaContainer(id=2,parent_id=0, name="tttat", children_callback=["1", "2", "3"])
        self.rootContainer.add_child(self.nextContainer, external_id=1)
        self.rootContainer.add_child(self.secondContainer)
        self.init_completed()

#    def get_by_id(self, id):
#        return self.rootContainer

    
    def retrieveAlbums(self, parent=None):
        albums = []
        albums = self.dbCursor.select("media",  single=False)
        # albums.add(DBMedia("nameeee"))
        return albums
    
    def upnp_init(self):
        self.current_connection_id = None
        if self.server:
            self.server.connection_manager_server.set_variable(0, 'SourceProtocolInfo',
                        'http-get:*:image/jpeg:*,'
                        'http-get:*:image/gif:*,'
                        'http-get:*:image/png:*',
                        default=True)
           # self.server.content_directory_server.set_variable(0, 'SystemUpdateID', self.update_id)
    
    def getNextID(self):
        ret = self.next_id
        self.next_id += 1
        return ret
    