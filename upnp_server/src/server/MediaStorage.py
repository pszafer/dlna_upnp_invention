'''
Created on 09-07-2011

@author: xps
'''

import mimetypes
from coherence.upnp.core import DIDLLite
import os
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
mimetypes.add_type('image/png', '.png')

from coherence.backend import BackendItem, BackendStore

class MediaContainer(BackendItem):
    logType = 'dlna_upnp_MediaContainer'
    
    def __init__(self, parent_id, name, store=None):
        self.id = store.new_item(self)
        self.parent_id = parent_id
        self.name = name
        self.mimetype = 'directory'
        self.store = store
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)

    def get_children(self, start=0, end=0):
        if callable(self.children):
            children = self.children()
        else:
            children = self.children
        self.info("Container get_children %r (%r,%r)", children, start, end)
        if end == 0:
            return children[start:]
        else:
            return children[start:end]


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

class MediaItem(BackendItem):   
    logCategory = 'smewt_media_store'

    def __init__(self,  store, media, name, parent_id, image = None):
        self.id = store.new_item(self)
        self.store = store
        self.media = media
        self.name = name
        self.image = image
        self.cover = image
        self.parent_id = parent_id
        self.item = self.create_item()
        self.caption = None
        
    def create_item(self):
        item = DIDLLite.ImageItem(self.id, self.parent_id, self.get_name())

        external_url = '%s/%d@%d' % (self.store.urlbase, self.id, self.parent_id,)
        external_url = self.store.urlbase + str(self.id)
        # add http resource
        filename = "/home/xps/Obrazy/320n.png"
        internal_url = 'file://' + filename
        mimetype, _ = mimetypes.guess_type(filename, strict=False)
        size = None
        if os.path.isfile(filename):
            size = os.path.getsize(filename)
        
        res = DIDLLite.Resource(internal_url, 'internal:%s:%s:*' % (self.store.server.coherence.hostname, mimetype,))
        res.size = size
        item.res.append(res)
        
        res = DIDLLite.Resource(external_url, 'http-get:*:%s:*' % (mimetype,))
        res.size = size
        #res.
        item.res.append(res)
        self.location = filename
    
#        if self.image and os.path.isfile(self.image):
#            mimetype,_ = mimetypes.guess_type(self.image, strict=False)
#            if mimetype in ('image/jpeg','image/png'):
#                if mimetype == 'image/jpeg':
#                    dlna_pn = 'DLNA.ORG_PN=JPEG_TN'
#                else:
#                    dlna_pn = 'DLNA.ORG_PN=PNG_TN'
#
#                dlna_tags = simple_dlna_tags[:]
#                dlna_tags[3] = 'DLNA.ORG_FLAGS=00f00000000000000000000000000000'
#                
#                hash_from_path = str(id(self.image))
#                _, ext = os.path.splitext(self.image)
#                item.albumArtURI = ''.join((external_url,'?cover',ext))
#
#                new_res = DIDLLite.Resource(external_url+'?attachment='+hash_from_path,
#                                            'http-get:*:%s:%s' % (mimetype, ';'.join([dlna_pn]+dlna_tags)))
#                new_res.size = os.path.getsize(self.image)
#                item.res.append(new_res)
#                if not hasattr(item, 'attachments'):
#                    item.attachments = {}
#                item.attachments[hash_from_path] = coherence_utils.StaticFile(self.image)
        return item
        
    def get_children(self,start=0, request_count=0):
        return []
        
    def get_child_count(self):
        return len(self.get_children())
  
    def get_item(self):
        return self.item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_cover(self):
        return self.cover  

class MediaStore(BackendStore):
    logType = 'dlna_upnp_MediaStore'
    implements = ['MediaServer']
    
    def __init__(self, server, **kwargs):
        BackendStore.__init__(self, server, **kwargs)
        self.next_id = 0
        self.warning("MediaStore init, what I got: %r", kwargs)
        self.db = kwargs['db']
        self.name = kwargs.get('name', 'Media')
        #self.dbCursor = kwargs['dbCursor']
        self.content = kwargs.get('content',None)
        self.store = FakeStore()
        if self.content != None:
            if(isinstance(self.content, basestring)):
                self.content = [self.content]
            l = []
            for i in self.content:
                l += i.split(',')
            self.content = l
        self.items = {}
        self.ids = {}
        self.plugin = kwargs['plugin']
        self.urlbase = kwargs.get('urlbase','')
        if( len(self.urlbase) > 0 and self.urlbase[len(self.urlbase)-1] != '/'):
            self.urlbase += '/'
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "TYT"            
        self.rootContainer = MediaContainer(parent_id=-1,
                                            name="root",
                                            store=self)
        self.secondContainer = MediaContainer(store=self, parent_id=self.rootContainer.get_id(), name="tttat")
        newItem = MediaItem(store=self, media=None, name="myname34", parent_id=self.secondContainer.get_id(), image=None)
        
        self.rootContainer.add_child(self.secondContainer)
        self.secondContainer.add_child(newItem)
        self.new_item(self.rootContainer)
        self.new_item(self.secondContainer)
        self.new_item(newItem)
        
        self.init_completed()

#    def get_by_id(self, id):
#        return self.rootContainer
    
    def upnp_init(self):
        self.current_connection_id = None
        if self.server:
            self.server.connection_manager_server.set_variable(0, 'SourceProtocolInfo',
                        ['internal:%s:video/mp4:*' % self.server.coherence.hostname,
                        'http-get:*:video/mp4:*',
                        'internal:%s:video/x-msvideo:*' % self.server.coherence.hostname,
                        'http-get:*:video/x-msvideo:*',
                        'internal:%s:video/mpeg:*' % self.server.coherence.hostname,
                        'http-get:*:video/mpeg:*',
                        'internal:%s:video/avi:*' % self.server.coherence.hostname,
                        'http-get:*:video/avi:*',
                        'internal:%s:video/divx:*' % self.server.coherence.hostname,
                        'http-get:*:video/divx:*',
                        'internal:%s:video/quicktime:*' % self.server.coherence.hostname,
                        'http-get:*:video/quicktime:*',
                        'internal:%s:image/png:*' % self.server.coherence.hostname,
                        'http-get:*:image/png:*'],
                        default=True)
            self.server.content_directory_server.set_variable(0, 'SystemUpdateID', self.update_id)
    
    def getNextID(self, item):
        ret = self.next_id
        #self.items[id] = item
        self.next_id += 1
        return ret
    
    def new_item(self, item):
        item_id = self.next_id
        self.items[item_id] = item
        self.next_id += 1
        return item_id

    
    def get_by_id(self,id):
        self.info("looking for id %r", id)
        if '@' in id:
            id = id.split('@')[0]
        return self.items[int(id)]

def tolist(obj):
    """Return object as a list:
     - if object is None, return the empty list
     - if object is a single object (i.e.: not a list), return a list with a
       single element being the given object
     - otherwise, (i.e.: it is a list), return the object itself
    """
    if obj is None:
        return []
    elif isinstance(obj, list):
        return obj
    else:
        return [ obj ]
    
class FakeCoherence:
    hostname = 'fake'

class FakeServer:
    coherence = FakeCoherence()

class FakeStore(BackendStore):
    def __init__(self, urlbase=''):
        self.urlbase = urlbase
        self.items = {}
        self.server = FakeServer()
        self.last_int = 0
      
    def new_item(self, item):
        id = self.last_int
        self.items[id] = item
        self.last_int += 1
        return id