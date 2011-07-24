'''
Created on 09-07-2011

@author: xps
'''

import mimetypes
from coherence.upnp.core import DIDLLite
from coherence.upnp.core.DIDLLite import classChooser , Container, Resource
import coherence.upnp.devices.media_server
import os
from sets import Set
import re
mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('audio/x-musepack', '.mpc')
mimetypes.add_type('audio/x-wavpack', '.wv')
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/divx', '.divx')
mimetypes.add_type('video/divx', '.avi')
mimetypes.add_type('video/ogg', '.ogv')
#mimetypes.add_type('video/x-matroska', '.mkv')
mimetypes.add_type('video/mkv', '.mkv')
mimetypes.add_type('text/plain', '.srt')
mimetypes.add_type('image/png', '.png')

from coherence.backend import BackendItem, BackendStore

## Sorting helpers
NUMS = re.compile('([0-9]+)')
def _natural_key(s):
    # strip the spaces
    s = s.get_name().strip()
    return [ part.isdigit() and int(part) or part.lower() for part in NUMS.split(s) ]

class MediaContainer(BackendItem):
    logType = 'dlna_upnp_MediaContainer'
    
    def __init__(self, id, item, parent_id, name, store=None):
        self.id = id
        
        self.parent_id = parent_id
        self.name = name
        
       # if mimetype == 'root':
      #      self.location = unicode(path)
        self.item = item(id, parent_id, name)
        if isinstance(self.item, Container):
            self.item.childCount = 0
        #aaa  = self.item.toString()
        #print aaa
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
        return self.item

    def get_name(self):
        return self.name
    
    def get_id(self):
        return self.id

class MediaItem(BackendItem):   
    logCategory = 'smewt_media_store'

    '''
        item - defining type of item:
            - Container,
            - Item:
                    - VideoItem
                    - MusicItem
                    - etc.
    '''
    def __init__(self, id, itemClass, path, hostname, urlbase, mimetype, name, parent, store=None, image = None):
        self.id = id
        
        self.store = store
        self.mimetype = mimetype
        self.parent = parent
        if parent == None:
            parent_id = -1
            self.parent_id = parent_id
        else:
            parent_id = parent.get_id()
            self.parent_id = parent_id
            parent.add_child(self)
        self.name = name
        if mimetype == 'root':
                self.location = unicode(path)
        self.image = image
        
        self.cover = image
        
        self.url = urlbase + str(self.id)
        
        
        self.item = itemClass(id, self.parent_id, self.name)
        
        self.child_count = 0
        self.children = []
        self.caption = None
        self.location = path
        
        
        
        if mimetype in ['directory','root']:
            self.get_url = lambda : self.url
            self.get_path = lambda : None
            self.update_id = 0
            self.item = itemClass(id, self.parent_id, self.name)
            if isinstance(self.item, Container):
                self.item.childCount = 0
           
            self.mimetype = mimetype
        else:
            self.get_url = lambda : self.url
            external_url = '%s%d@%d' % (self.store.urlbase, self.id, self.parent_id,)
            filename = path
            self.location = filename
            internal_url = 'file://' + filename
            mimetype, _ = mimetypes.guess_type(filename, strict=False)
            self.mimetype = mimetype
            size = None
            if os.path.isfile(filename):
                size = os.path.getsize(filename)
            if mimetype != 'item':
                res = Resource(internal_url, 'internal:%s:%s:*' % (hostname, mimetype))
                res.size = size
                self.item.res.append(res)
            #if mimetype != 'item':
            res = Resource(external_url, 'http-get:*:%s:*' % (mimetype,))
            #else:
            #res = Resource(external_url, 'http-get:*:*:*')
            res.size = size
            self.item.res.append(res)
               
    def create_item(self):
        external_url = '%s%d@%d' % (self.store.urlbase, self.id, self.parent_id,)
        #external_url = self.store.urlbase + str(self.id)
        # add http resource
        filename = "/home/xps/Wideo/test/Friends_S06_E20.avi"
        internal_url = 'file://' + filename
        mimetype, _ = mimetypes.guess_type(filename, strict=False)
        item = classChooser(mimetype)
        item = item(self.id, self.parent_id, self.get_name())
        size = None
        if os.path.isfile(filename):
            size = os.path.getsize(filename)
        
        res = DIDLLite.Resource(internal_url, 'internal:%s:%s:*' % (self.store.server.coherence.hostname, mimetype))
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
    
    def add_child(self, child):
        self.children.append(child)
        self.child_count += 1
        if isinstance(self.item, Container):
            self.item.childCount += 1
        self.update_id += 1
        self.sorted = False
    
    def get_children(self,start=0, end=0):
        if self.sorted == False:
            self.children.sort(key=_natural_key)
            self.sorted = True
        if end == 0:
            return self.children[start:]
        else:
            return self.children[start:end]
        
    def get_child_count(self):
        return self.child_count
  
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
        #self.db = kwargs['db']
        self.name = kwargs.get('name', 'Media')
        #self.dbCursor = kwargs['dbCursor']
        self.content = kwargs.get('content',None)
        self.store = {}
        if self.content != None:
            if(isinstance(self.content, basestring)):
                self.content = [self.content]
            l = []
            for i in self.content:
                l += i.split(',')
            self.content = l
        #self.content = Set([os.path.abspath(x) for x in self.content])
        #ignore_patterns = kwargs.get('ignore_patterns',[])
        
        self.import_folder = kwargs.get('import_folder',None)
        self.import_folder = "/home/xps/Wideo"
        if self.import_folder != None:
            self.import_folder = os.path.abspath(self.import_folder)
            if not os.path.isdir(self.import_folder):
                self.import_folder = None
        
        self.items = {}
        self.ids = {}
        #self.plugin = kwargs['plugin']
        self.urlbase = kwargs.get('urlbase','')
        if( len(self.urlbase) > 0 and self.urlbase[len(self.urlbase)-1] != '/'):
            self.urlbase += '/'
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "TYT"
        parent = None
        id = self.getNextID()
        itemClass=classChooser("root")
        self.store[id] = rootC = parent = MediaItem(
                                       id = id, 
                                       parent = parent,
                                       path="/home/xps/Wideo/test",
                                       name = 'test',
                                       mimetype="directory",
                                       store=self,
                                       hostname = self.server.coherence.hostname,
                                       urlbase = self.urlbase,
                                       itemClass=itemClass)
        self.update_id += 1
        id = self.getNextID()  
        self.store[id] = parent = MediaItem(
                                         id = id,
                                         parent = parent, 
                                         name = 'test2',
                                         mimetype='directory',
                                         path="/home/xps/Wideo/test/test2",
                                         store=self,
                                         urlbase = self.urlbase,
                                         hostname = self.server.coherence.hostname,
                                         itemClass=itemClass)
        self.update_id += 1
        id = self.getNextID()  
        self.store[id] = you = MediaItem(
                                         id = id,
                                         parent = parent, 
                                         name = 'friends.avi',
                                         path = "/home/xps/Wideo/test/test2/Friends_S06_E20.avi",
                                         mimetype='video/divx',
                                         store=self,
                                         urlbase = self.urlbase,
                                         hostname = self.server.coherence.hostname,
                                         itemClass=classChooser("video/divx"))
        self.update_id += 1
        #rootC.add_child(you)
        #newItem = MediaItem(id = self.getNextID(), store=self, media=None, name="myname34.avi", parent_id=self.rootContainer.get_id(), image=None)
        #self.secondContainer.add_child(newItem)
        #self.new_item(self.secondContainer)
        #self.add_item(newItem)
        #print self.rootContainer.toString()
        self.wmc_mapping.update({'14': '0',
                                 '15': '0',
                                 '16': '0',
                                 '17': '0'
                                })
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
                
    def getNextID(self):
        ret = self.next_id
        self.next_id += 1
        return ret
    
    def getCurrentID(self):
        return self.next_id
    
    def add_item(self, item):
        self.store[item.get_id()] = item

    
    def get_by_id(self,id):
        self.info("looking for id %r", id)
        if isinstance(id, basestring):
            id = id.split('@',1)
            id = id[0]
        return self.store[int(id)]

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