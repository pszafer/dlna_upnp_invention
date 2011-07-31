'''
Created on 09-07-2011

@author: xps
'''


from coherence.upnp.core.DIDLLite import classChooser , Container, Resource


import os
from sets import Set
import stat
from twisted.python.filepath import FilePath

from server import helpers

import datetime



from coherence.backend import BackendItem, BackendStore
from coherence.upnp.devices import media_server
import re
from aifc import Error

media_server.COVER_REQUEST_INDICATOR = re.compile("(.*?cover\.[A-Z\a-z]{3,4}(&WMHME=1)?)$")         #special patch to work thumbnails with WMP12 

class MediaItem(BackendItem):   
    logCategory = 'smewt_media_store'
    '''MediaItem is one class containing item, such as:
            - Container -- folder
            - VideoItem -- video file
            - MusicItem -- music file
            - ImageItem -- image
    '''
    def __init__(self, 
                 object_id, 
                 itemClass, 
                 path, 
                 urlbase, 
                 hostname, 
                 mimetype, 
                 parent, 
                 store=None, 
                 image = None,
                 add_child=True):
        '''
        Iniatilaze class for object
        
        Keyword arguments:
        @param object_id:   id of object, which is creating right now
        @param itemClass:   itemClass is class of DIDLLite, choose by classChooser method and pass here
        @param path:        is real path to file like /tmp/filename
        @param urlbase:     basically server.coherence.hostname, e.g. http://localhost:port/uuid/
                            important slash / in the end
        @param hostname:    this is only http://ipaddress
        @param mimetype:    mimetype, all handled mimetypes are in helpers module
        @param parent:      parent MediaItem, from whom we get id
        @param store:       we need to pass MediaStore in which MediaItem it is
        @param image:       used to get thumbnails, with that we got many many troubles
        '''
        
        self.id = object_id
        self.store = store
        self.mimetype = mimetype
        self.parent = parent
        self.sorted = False
        if parent == None:
            parent_id = -1
            self.parent_id = parent_id
        else:
            parent_id = parent.get_id()
            self.parent_id = parent_id
            if add_child:
                parent.add_child(self)
            
        if path != None:
            self.name = os.path.basename(path)
            if mimetype == 'root':
                self.location = unicode(path)
            else:
                if os.path.isdir(path) or os.path.isfile(path):
                    self.location = FilePath(path)
                else:
                    self.location = unicode(path)
        else:
            return
        self.image = image                                              #thumbnail path
        self.cover = image                                              #thumbnail path
        self.url = urlbase + str(self.id)                               #create url to this item
        self.item = itemClass(object_id, self.parent_id, self.name)     #create item like VideoItem, ImageItem, MusicItem with name, id, parent
        #self.item.DIDLElement.attrib['xmlns:dc'] = ''
        #self.item.DIDLElement.attrib['xmlns:upnp'] = ''        
        self.child_count = 0
        self.children = []                                              #children list
        self.caption = None                                             #subtitles?
        
        if mimetype in ['directory','root']:                            #check if this is container
            self.get_url = lambda : self.url                            #simple function to get url, we don't need nothing more complicated
            self.get_path = lambda : None                               #we don't need path for container so return None
            self.update_id = 0                                          #something to update?   
            if isinstance(self.item, Container):
                self.item.childCount = 0                                #if this is container we need make sure that at first place it has no children
        else:
            self.get_url = lambda : self.url                            #function to get url of MediaItem
            external_url = '%s%s' % (self.store.urlbase, str(self.id))  #creating of external url like http://localhost:port/uuid/dir/item
            internal_url = 'file://' + path                             #creating internal url like file:///tmp/file.txt
            size = None                                                 #we need size of file
            res = None
            if os.path.isfile(path):                                    #make sure file exists
                size = os.path.getsize(path)
                self.item.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))    #get file change date
                if mimetype != 'item':                                                          #make sure it has some reasonable mimetype
                    res = Resource(internal_url, 'internal:%s:%s:*' % (hostname, mimetype))    #create internal resource    
                if 'video' in mimetype:
                    res, res1 = self.create_VideoItem(res, size, external_url, mimetype, path)
                    self.createThumbnails(path, urlbase)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                                                   #add resource to item
                elif 'audio' in mimetype:
                    res, res1 = self.create_AudioItem(res, size, external_url, mimetype, path)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                     
                elif 'image' in mimetype:
                    res, res1 = self.create_ImageItem(res, size, external_url, mimetype, path)
                    self.createThumbnails(path, urlbase)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                                                   #add resource to item
                
    def add_child(self, child):
        '''
        Add child for container
        Can't be used with mimetypes != directory
        @param child:    MediaItem class with this child
        '''
        self.children.append(child)
        self.child_count += 1
        if isinstance(self.item, Container):
            self.item.childCount += 1
        self.update_id += 1
        self.sorted = False
    
    
    
    def add_children(self, children):
        '''
        Add child for container
        Can't be used with mimetypes != directory
        @param child:    MediaItem class with this child
        '''
        self.children = children
        self.child_count = len(children)
        if isinstance(self.item, Container):
            self.item.childCount = len(children)
        self.update_id += len(children)
        self.sorted = False
    
    def remove_children(self, start=-1, end=-1):
        for i in range(end, start,-1):
            if i < len(self.children):
                self.children.pop(i)
        self.child_count = len(self.children)
            
    def add_parent(self, parent, parent_id):
        self.parent = parent
        self.parent_id = parent_id        
    
    def get_children(self,start=0, end=0):
        '''
        Get children list
        @param start:    start index of children to return
        @param end:      end index of children to return
        '''
        if self.sorted == False:
            self.children.sort(key=helpers._natural_key)
            self.sorted = True
        if end == 0:
            return self.children[start:]
        else:
            return self.children[start:end]
        
    def get_child_count(self):
        '''
        Get number of children this container has
        '''
        return self.child_count
  
    def get_item(self):
        '''
        Get item
        '''
        return self.item

    def get_id(self):
        '''
        Get id of item
        '''
        return self.id

    def get_name(self):
        '''
        Get name of item
        '''
        return self.name

    def get_cover(self):
        '''
        Get cover of item
        Used also with video and images
        '''
        return self.cover
    
    def get_path(self):
        '''
        Get real path of file
        '''
        if isinstance( self.location,FilePath):
            return self.location.path
        else:
            self.location
    
    def get_mimetype(self):
        '''
        Get mimetype of item
        '''
        return self.mimetype
    
    def get_parent_id(self):
        return self.parent_id
    
    def set_path(self,path=None,extension=None):
        if path is None:
            path = self.get_path()
        if extension is not None:
            path,_ = os.path.splitext(path)
            path = ''.join((path,extension))
        if isinstance( self.location,FilePath):
            self.location = FilePath(path)
        else:
            self.location = path
            
    def create_VideoItem(self, res, size, external_url, mimetype, path):
        '''
        Create resource with videoItem and profiled metadata of video file
        @param res:             input internal resource
        @param size:            size of file
        @param external_url:    external url
        @param mimetype:        mimetype
        @param path:            path to file (not URI)
        '''
        metadata = helpers.getFileMetadata(path)                                    #get file metadata like duration, bitrate using ffprobe
        #dlna_tags = "DLNA.ORG_PN=AVI;DLNA.ORG_OP=01;DLNA.ORG_CI=0"                      #don't needed????
        res1 = Resource(external_url, 'http-get:*:%s:*' % (mimetype,))                   #create external resource
        res.size = res1.size = size
        res.duration = res1.duration = metadata['duration']
        res.bitrate = res1.bitrate = metadata['bitrate']
        res.nrAudioChannels = res1.nrAudioChannels = metadata['audio_channels']
        res.resolution = res1.resolution = metadata['resolution']
        return res, res1
    
    def create_AudioItem(self, res, size, external_url, mimetype, path):
        '''
        Create resource with audioItem and profiled metadata of audio file
        @param res:             input internal resource
        @param size:            size of file
        @param external_url:    external url
        @param mimetype:        mimetype
        @param path:            path to file (not URI)
        '''
        res1 = Resource(external_url, 'http-get:*:%s:*' % (mimetype,))                   #create external resource
        duration = None
        bitrate = None
        if 'mpeg' in mimetype:
            from mutagen.mp3 import MP3
            audio = MP3(path)
            duration = helpers.s2hms(audio.info.length)
            bitrate = audio.info.bitrate
        if 'x-wav' in mimetype:
            import wave
            wfile = wave.open (path, "r")
            duration = helpers.s2hms((1.0 * wfile.getnframes ()) / wfile.getframerate ())
        res.size = res1.size = size
        res.duration = res1.duration = duration 
        res.bitrate = res1.bitrate = bitrate 
        return res, res1
    
    def create_ImageItem(self, res, size, external_url, mimetype, path):
        '''
        Create resource with imageItem and profiled metadata of image file
        @param res:             input internal resource
        @param size:            size of file
        @param external_url:    external url
        @param mimetype:        mimetype
        @param path:            path to file (not URI)
        '''
        #dlna_tags = "DLNA.ORG_PN=AVI;DLNA.ORG_OP=01;DLNA.ORG_CI=0"                      #don't needed????
        res1 = Resource(external_url, 'http-get:*:%s:*' % (mimetype,))                   #create external resource
        res.size = res1.size = size
        resolution = None
        import Image
        im = Image.open(path)
        for i in im.size:
            if resolution is None:
                resolution = ""
            resolution += str(i)+"x"
        resolution = resolution[:len(resolution)-1]
        res.resolution = res1.resolution = resolution 
        return res, res1
    
    def createThumbnails(self, path, urlbase):
        '''
        create thumbnail
        now working only with importing nautilus thumbnails
        @param path:        path to file we want to get thumbnail
        @param urlbase:     urlbase of file to create thumbnail uri
        '''
        try:
            thumbnail_path,_,_ = helpers._find_thumbnail(helpers.import_thumbnail("file://"+path))     #get thumbnail path from gnome ~/.thumbnails
            #hash_from_path = str(test)
    #       self.item.albumArtURI = self.url+'?attachment='+hash_from_path
            self.cover = thumbnail_path
            _,ext =  os.path.splitext(self.cover)
            self.item.albumArtURI = ''.join((urlbase,str(self.id),'?cover',ext))                    #broadcast thumbnail as cover
                                                                                                            #WMP12 need's special treating...
        except Exception as inst:
            print inst

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
        self.containers_map = {}
        if self.content != None:
            if(isinstance(self.content, basestring)):
                self.content = [self.content]
            l = []
            for i in self.content:
                l += i.split(',')
            self.content = l
        self.content = Set([os.path.abspath(x) for x in self.content])
        #ignore_patterns = kwargs.get('ignore_patterns',[])
        
        self.import_folder = kwargs.get('import_folder',None)
        self.import_folder = "/home/xps/Wideo"
        if self.import_folder != None:
            self.import_folder = os.path.abspath(self.import_folder)
            if not os.path.isdir(self.import_folder):
                self.import_folder = None
        self.do_mimetypes_containers = kwargs.get('do_mimetype_container', False)
        self.max_child_items = kwargs.get('max_child_items', 10)
        self.hostname = self.server.coherence.hostname
        self.urlbase = kwargs.get('urlbase','')
        if( len(self.urlbase) > 0 and self.urlbase[len(self.urlbase)-1] != '/'):
            self.urlbase += '/'
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "TYT"
        self.createContainer("root",  parent = None, path="root", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("root"))
        self.createContainer("directories",  parent = self.store[str(0)], path="Directories", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.createContainer("Image", parent = self.store[str(0)], path="Image", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.createContainer("Audio", parent = self.store[str(0)], path="Audio", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.createContainer("Video", parent = self.store[str(0)], path="Video", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.update_id += 1
        self.searchInContentPath(self.content)                              #recurency search
            
        
        
        if self.do_mimetypes_containers:
            mimetypes_root_created = False
            mimetypes_containers = {}
            for item in self.store.values():
                itemmimetype = item.get_mimetype()
                mimetype_id = -2
                if itemmimetype not in ['directory','root']: 
                    if itemmimetype not in mimetypes_containers.keys():
                        id = self.getNextID()
                        if not mimetypes_root_created:
                            mimetype_id = self.createContainer(
                                                 "mimetypes", 
                                                 parent = self.store[str(0)], 
                                                 path="Mimetypes", 
                                                 mimetype="directory", 
                                                 urlbase = self.urlbase, 
                                                 hostname = self.hostname, 
                                                 itemClass=classChooser("directory"))
                            mimetypes_root_created = True
                        mimetypes_containers[itemmimetype] = self.createContainer(
                                             str(itemmimetype), 
                                             parent = self.store[str(self.containers_map['mimetypes'])], 
                                             path = str(itemmimetype), 
                                             mimetype="directory", 
                                             urlbase = self.urlbase, 
                                             hostname = self.hostname, 
                                             itemClass=classChooser("directory"),
                                             mimetype_container = True)
                    self.store[str(mimetypes_containers[itemmimetype])].add_child(item)
        #divide elements if too many childs
        try:
            for container in self.containers_map.values():
                if container == '3':
                    if container not in mimetypes_containers.values():
                        pass
                    test = str(self.containers_map['mimetypes'])
                    if container is not test:
                        pass
                if ((container != str(0)) and 
                (container not in mimetypes_containers.values()) and 
                (container is not str(self.containers_map['mimetypes']))):
                    child_count = self.store[container].get_child_count() 
                    new_cont_id = -2
                    if child_count > self.max_child_items:
                        iterator = 1
                        number_of_container = (child_count/self.max_child_items + 1)              #number of containers to make to have divided children in equal containers
                        items_in_container = (child_count + number_of_container // 2) // number_of_container
                        left_items = child_count
                        new_store_children_only = {}
                        new_children_container = []
                        old_path = self.store[container].get_path()
                        for i in range(number_of_container):
                            path = old_path
                            if path is None:
                                path = str(iterator)
                            else:
                                path += str(iterator)
                            name = self.store[container].get_name()
                            if name is None:
                                name = str(iterator)
                            else:
                                name += str(iterator)
                            new_cont_id = self.createContainer(
                                                 name =  name,
                                                 parent = self.store[container], 
                                                 path = path,
                                                 mimetype = 'directory', 
                                                 urlbase = self.urlbase, 
                                                 hostname = self.hostname, 
                                                 itemClass = classChooser('directory'),
                                                 add_child=False)
                            new_children_container.append(new_cont_id)
                            new_store_children_only[new_cont_id] = self.store[container].get_children(start=0, end=items_in_container)
                            self.store[container].remove_children(start=-1, end=items_in_container-1)
                            left_items -= items_in_container
                            if left_items < 10 and child_count == 286:
                                pass
                            iterator += 1
                        if left_items > 0:
                            children_left = self.store[container].get_children()
                            children_already_got = new_store_children_only[new_cont_id]
                            children_already_got += children_left
                            new_store_children_only[new_cont_id] = children_already_got
                            self.store[container].remove_children(start=0, end=left_items)
                        
                        for i in new_store_children_only:
                            id = self.store[i].get_parent_id()
                            self.store[str(id)].add_child(self.store[i])
                            self.store[i].add_children(new_store_children_only[i])
                        
                            #co jezeli w grupie children jest 
                            #change parent of item
                            #add children ommitting new containers
        except Exception, e:
            print e
        self.wmc_mapping.update({'14': '0',
                                 '15': '0',
                                 '16': '0',
                                 '17': '0'
                                })
        self.init_completed()

#    def get_by_id(self, id):
#        return self.rootContainer
    
    def createContainer(self, name, parent, path, mimetype, urlbase, hostname, itemClass, mimetype_container = False, add_child=True):
        id = self.getNextID()  
        self.store[id] = MediaItem(
                                         object_id = id,
                                         parent = parent, 
                                         path = path,
                                         mimetype=mimetype,
                                         store=self,
                                         urlbase = self.urlbase,
                                         hostname = self.server.coherence.hostname,
                                         itemClass = itemClass,
                                         add_child=add_child)
        if not mimetype_container:
            self.containers_map[name] = id
        return id
    
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
        if(ret == 315):
            pass
        self.next_id += 1
        return str(ret)
    
    def getCurrentID(self):
        return self.next_id
    
    def add_item(self, item):
        self.store[str(item.get_id())] = item

    
    def get_by_id(self,object_id):
        self.info("looking for id %r", object_id)
        if isinstance(object_id, basestring):
            object_id = object_id.split('@',1)
            object_id = object_id[0]
        return self.store[object_id]
    
    def searchInContentPath(self, content):
        for path in content:
            if isinstance(path, (list, tuple)):
                path = path[0]
            try:
                path = path.encode('utf-8')
                self.stepInto(path, self.store[str(self.containers_map['directories'])])
            except Exception, e:
                print "ee" + e
    
    def stepInto(self, path, parent=None):
        containers = []
        parent = self.insert(path, parent)
        if parent != None:
            containers.append(parent)
        while len(containers)>0:
            single_container = containers.pop()
            try:
                for child in single_container.location.children():
                    cache_container = self.insert(child.path, single_container)
                    if cache_container:
                        containers.append(cache_container)
            except UnicodeDecodeError, e:
                print "eee" + e
                
     
    def insert(self, path, parent):
        if os.path.exists(path) == False:
            return None
        if stat.S_ISFIFO(os.stat(path).st_mode):
            return None
        try:
            mimetype,_ = helpers.mimetypes.guess_type(path, strict=False)
            if mimetype == None:
                if os.path.isdir(path):
                    mimetype = 'directory'                                      #if path is direcotry we need mimetype directory
                else:
                    return None
            id = self.createItem(path, parent, mimetype)
            if mimetype == 'directory':
                return self.store[id]
        except OSError, e:
            print "eee" +e
            
    def createItem(self, path, parent, mimetype):
        itemClass = classChooser(mimetype)
        if itemClass == None:
            return None
        
        if mimetype not in ('root', 'directory'):                               #id will be no id +
            _,ext =  os.path.splitext(path)
            object_id = str(self.getNextID()) + ext.lower()
            self.store[object_id] = MediaItem(object_id=object_id,
                                          itemClass=itemClass,
                                          path=path,
                                          parent=parent,
                                          urlbase=self.urlbase,
                                          hostname = self.hostname,
                                          mimetype=mimetype,
                                          store=self)
        else:
            object_id = self.createContainer(
                                 name = os.path.abspath(path), 
                                 parent = parent, 
                                 path = path, 
                                 mimetype = mimetype, 
                                 urlbase = self.urlbase, 
                                 hostname = self.hostname, 
                                 itemClass = itemClass)
        if 'video' in mimetype:
            self.store[str(self.containers_map['Video'])].add_child(self.store[object_id])
        elif 'audio' in mimetype:
            self.store[str(self.containers_map['Audio'])].add_child(self.store[object_id])
        elif 'image' in mimetype:
            self.store[str(self.containers_map['Image'])].add_child(self.store[object_id])
        return object_id
        
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