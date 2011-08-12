'''
Created on 09-07-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8
'''


from coherence.upnp.core.DIDLLite import classChooser , Container, Resource, Item
from coherence.extern.et import ET

import os
from sets import Set
import stat
from twisted.python.filepath import FilePath

import helpers

import datetime
import gettext


from coherence.backend import BackendItem, BackendStore
from coherence.upnp.devices import media_server
from coherence.upnp.core import utils

import re
from aifc import Error
import traceback
from StringIO import StringIO
import Image
import imghdr
from gettext import locale


try:
    from coherence.extern.inotify import INotify
    from coherence.extern.inotify import IN_CREATE, IN_DELETE, IN_MOVED_FROM, IN_MOVED_TO, IN_ISDIR
    from coherence.extern.inotify import IN_CHANGED
    haz_inotify = True
except Exception,msg:
    haz_inotify = False
    no_inotify_reason = msg

media_server.COVER_REQUEST_INDICATOR = re.compile("(.*?cover\.[A-Z\a-z]{3,4}(&WMHME=1)?)$")         #special patch to work thumbnails with WMP12 

APP="dlnaupnpserver"
translations = gettext.translation(APP, "./locale", fallback = True, languages=['pl'])
translations.install()

#lang_pl = gettext.translation(APP, DIR, languages=['pl'])
#lang_en.install()
#lang_pl.install()

def raw_generate(fn):
        "Generate thumbnail (retruns rawdata)"
        im = Image.open(fn)
        buf = StringIO()
        im.save(buf, imghdr.what(fn))
        return buf.getvalue()


class MediaItem(BackendItem):   
    logCategory = 'smewt_media_store'
    '''MediaItem is one class containing item, such as:
            - Container -- folder
            - VideoItem -- Video file
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
                 add_child=True,
                 subtitles = False):
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
        @param add_child:   is needed to add child, False if we dividing elements, because we want to have same parent, but virtual other containers
        @param subtitles:   True if it is Item for subtitles
        '''
        
        self.id = object_id
        self.store = store
        self.mimetype = mimetype
        self.parent = parent
        self.otherparents = []
        self.hostname = hostname
        self.sorted = False
        if parent == None and subtitles == False:
            parent_id = -1
            self.parent_id = parent_id
        elif parent == None and subtitles == True:
            parent_id = -2
            self.parent_id = None
        else:
            parent_id = parent.get_id()
            self.parent_id = parent_id
            if add_child:
                parent.add_child(self)
            
        if path != None:
            if subtitles: 
                self.name = os.path.basename(path)
            else:
                self.name, _ = os.path.splitext(os.path.basename(path))
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
        url = urlbase + str(self.id)                               #create url to this item
        self.url = url
        self.item = itemClass(object_id, self.parent_id, self.name)     #create item like VideoItem, ImageItem, MusicItem with name, id, parent
        self.child_count = 0
        self.children = []                                              #children list
        self.caption = None                                             #subtitles?
        
        if mimetype in ['directory','root']:                            #check if this is container
            self.update_id = 0
            self.get_url = lambda : self.url                            #simple function to get url, we don't need nothing more complicated
            self.get_path = lambda : None                               #we don't need path for container so return None
            self.update_id = 0                                          #something to update?   
            if isinstance(self.item, Container):
                self.item.childCount = 0                                #if this is container we need make sure that at first place it has no children
        else:
            self.get_url = lambda : self.url                            #function to get url of MediaItem
            external_url = '%s%s' % (urlbase, str(self.id))  #creating of external url like http://localhost:port/uuid/dir/item
            internal_url = 'file://' + path                             #creating internal url like file:///tmp/file.txt
            size = None                                                 #we need size of file
            res = None
            if os.path.isfile(path):                                    #make sure file exists
                size = os.path.getsize(path)
                self.item.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))    #get file change date
                if mimetype != 'item':                                                          #make sure it has some reasonable mimetype
                    res = Resource(internal_url, 'internal:%s:%s:*' % (hostname, mimetype))    #create internal resource    
                if 'video' in mimetype:
                    res, res1, res2 = self.create_VideoItem(res, size, external_url, mimetype, path, urlbase)
                    res3 = self.createThumbnails(path, urlbase)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                                                   #add resource to item
                    if res2:
                        self.item.res.append(res2)                                                   #add resource with subtitles to item
                    if res3:
                        self.item.res.append(res3)
                elif 'audio' in mimetype:
                    res, res1 = self.create_AudioItem(res, size, external_url, mimetype, path)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                     
                elif 'image' in mimetype:
                    res, res1 = self.create_ImageItem(res, size, external_url, mimetype, path)
                    res3 = self.createThumbnails(path, urlbase)
                    self.item.res.append(res)                                                       #add resource to item
                    self.item.res.append(res1)                                                   #add resource to item
                    if res3:
                        self.item.res.append(res3)
                elif 'text' in mimetype:                                                            #especially for subtitles
                    res1 = Resource(external_url, 'http-get:*:%s:*' % (mimetype,))
                    self.item.res.append(res)
                    self.item.res.append(res1)
                
    def add_child(self, child, update=False):
        '''
        Add child for container
        Can't be used with mimetypes != directory
        @param child:    MediaItem class with this child
        @param update:    update id to inform other MediaRenderers about changes
        '''
        self.children.append(child)
        self.child_count += 1
        if isinstance(self.item, Container):
            self.item.childCount += 1
        if update == True:
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
        '''
        Remove range of children when start is first element to remove, and end is first
        Removing is backward
        @param start:first element to remove
        @param end:last element to remove
        '''
        for i in range(end, start,-1):
            if i < len(self.children):
                self.children.pop(i)
        self.child_count = len(self.children)
        self.update_id += 1
    
    def remove_child(self, child):
        '''
        Remove child item
        If child item is in mimetype remove it from there too
        @param child: MediaItem
        '''
        if child in self.children:
            self.child_count -= 1
            if isinstance(self.item, Container):
                self.item.childCount -= 1
            self.children.remove(child)
            self.update_id += 1
            if (self.parent.get_name() == "Mimetypes") and (self.get_child_count() <= 0):
                self.remove()
            self.sorted = False
    
    
    def remove(self):
        '''
        Remove self item and remove yourself from parent
        '''
        if self.parent:
            self.parent.remove_child(self)
        del self.item
    
    def add_parent(self, parent, parent_id):
        '''
        Add parent, can only be one
        @param parent: parent item
        @param parent_id: parent id
        '''
        self.parent = parent
        self.parent_id = parent_id        
    
    def add_other_parent(self, other_parent_id):
        '''
        We have mimetypes and categories, so we need other parents containers to know what is where
        @param other_parent_id: other parent id
        '''
        self.otherparents.append(other_parent_id)
    
    def get_other_parents(self):
        '''
        Return other parents
        '''
        if self.otherparents:
            return self.otherparents
        return None
    
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
        Used also with Video and images
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
        '''
        Return parent id
        '''
        return self.parent_id
    
    def get_parent(self):
        '''
        Return parent, which is instance of MediaItem
        '''
        return self.parent
    
    def get_update_id(self):
        '''
        Get current update id
        '''
        if hasattr(self, 'update_id'):
            return self.update_id
        else:
            return None
    
    def set_path(self,path=None,extension=None):
        '''
        Set path, problably used by coherence, not sure
        @param path:
        @param extension:
        '''
        if path is None:
            path = self.get_path()
        if extension is not None:
            path,_ = os.path.splitext(path)
            path = ''.join((path,extension))
        if isinstance( self.location,FilePath):
            self.location = FilePath(path)
        else:
            self.location = path
            
    def create_VideoItem(self, res, size, external_url, mimetype, path, urlbase):
        '''
        Create resource with VideoItem and profiled metadata of Video file
        @param res:             input internal resource
        @param size:            size of file
        @param external_url:    external url
        @param mimetype:        mimetype
        @param path:            path to file (not URI)
        @param urlbase:         urlbase of coherence server
        '''
        metadata = helpers.getFileMetadata(path)                                    #get file metadata like duration, bitrate using ffprobe
        res1 = Resource(external_url, 'http-get:*:%s:%s' % (mimetype,"DLNA.ORG_OP=01;DLNA.ORG_CI=0;DLNA.ORG_FLAGS=01500000000000000000000000000000"))                   #create external resource
        self.size = res.size = res1.size = size
        res.duration = res1.duration = metadata['duration']
        res.bitrate = res1.bitrate = metadata['bitrate']
        res.nrAudioChannels = res1.nrAudioChannels = metadata['audio_channels']
        res.resolution = res1.resolution = metadata['resolution']
        caption,_ =  os.path.splitext(self.get_path())
        caption_srt = caption + '.srt'
        caption_smi = caption + '.smi'
        #new_id = self.id.split(".")[0]+".SRT"
        captions = {}
        if os.path.exists(caption_srt):
            new_id = self.id.split(".")[0]+".SRT"
            mime = "text/srt"
            self.caption_size = os.path.getsize(caption_srt)
            captions[mime] = caption_srt
        if os.path.exists(caption_smi):
            caption = caption_smi
            new_id = self.id.split(".")[0]+".SMI"
            mime = "smi/caption"
            self.caption_size = os.path.getsize(caption_smi)
            captions[mime] = caption_smi
        for mime,caption in captions.iteritems():
            item = Item
            self.store.store[new_id] = MediaItem(object_id=new_id,
                                           itemClass=item,
                                           path=caption,
                                           parent=None,
                                           urlbase=urlbase,
                                           hostname = self.hostname,
                                           mimetype=mime,
                                           store=self,
                                           subtitles=True)
            hash_from_path = str(id(caption))
            mimetype = mime
            res2 = Resource(urlbase+new_id,'http-get:*:%s:%s' % (mimetype, '*'))
            self.caption = urlbase+new_id
            self.item.caption = urlbase+new_id
            if not hasattr(self.item, 'attachments'):
                self.item.attachments = {}
                if caption_smi is not None:
                    self.item.attachments[hash_from_path] = utils.StaticFile(caption_smi)
                else:
                    self.item.attachments[hash_from_path] = utils.StaticFile(caption_srt)
            return res, res1, res2
        return res, res1, None
    
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
            _,ext =  os.path.splitext(thumbnail_path)
            self.item.albumArtURI = ''.join((urlbase,str(self.id),'?cover',ext))                    #broadcast thumbnail as cover
            res = Resource(self.item.albumArtURI, "http-get:*:image/jpg:DLNA.ORG_PN=JPEG_TN;DLNA.ORG_OP=00;DLNA.ORG_CI=1;DLNA.ORG_FLAGS=00D00000000000000000000000000000")
            resolution = None
            im = Image.open(thumbnail_path)
            for i in im.size:
                if resolution is None:
                    resolution = ""
                resolution += str(i)+"x"
            resolution = resolution[:len(resolution)-1]
            res.resolution =resolution 
            return res
        except Exception as inst:
            print inst

class MediaStore(BackendStore):
    logType = 'dlna_upnp_MediaStore'
    implements = ['MediaServer']
    
    def __init__(self, server, **kwargs):
        BackendStore.__init__(self, server, **kwargs)
        self.next_id = 0
        self.warning("MediaStore init, what I got: %r", kwargs)
        self.name = kwargs.get('name', 'Media')
        self.content = kwargs.get('content',None)
        self.store = {}
        self.containers_map = {}
        self.inotify = None
        if kwargs.get('enable_inotify','yes') == 'yes':
            if haz_inotify == True:
                try:
                    self.inotify = INotify()
                except Exception,msg:
                    self.info("%s" %msg)
            else:
                self.info("%s" %no_inotify_reason)
        else:
            self.info("FSStore content auto-update disabled upon user request")
        if self.content != None:
            if(isinstance(self.content, basestring)):
                self.content = [self.content]
            l = []
            for i in self.content:
                l += i.split(',')
            self.content = l
        self.content = Set([os.path.abspath(x) for x in self.content])
        ignore_patterns = kwargs.get('ignore_patterns',[])
        self.ignore_file_pattern = re.compile('|'.join(['^\..*'] + list(ignore_patterns)))
        
        
        self.import_folder = kwargs.get('import_folder',None)
        self.import_folder = "/home/xps/Wideo"
        if self.import_folder != None:
            self.import_folder = os.path.abspath(self.import_folder)
            if not os.path.isdir(self.import_folder):
                self.import_folder = None
        self.do_mimetypes_containers = kwargs.get('do_mimetype_container', False)
        if self.do_mimetypes_containers:
            self.mimetypes_container_inited = False
            self.mimetypes_root_created = False
        self.max_child_items = kwargs.get('max_child_items', 10)
        self.hostname = self.server.coherence.hostname
        self.urlbase = kwargs.get('urlbase','')
        if( len(self.urlbase) > 0 and self.urlbase[len(self.urlbase)-1] != '/'):
            self.urlbase += '/'
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "SERVER UPNP"
        self.feature_list = {}
        self.createContainer("root",  parent = None, path="root", mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("root"))
        self.createContainer("directories",  parent = self.store[str(0)], path=_("Directories"), mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.feature_list['imageItem'] = self.createContainer("Image", parent = self.store[str(0)], path=_("Image"), mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.feature_list['audioItem'] = self.createContainer("Audio", parent = self.store[str(0)], path=_("Audio"), mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.feature_list['videoItem'] = self.createContainer("Video", parent = self.store[str(0)], path=_("Video"), mimetype="directory", urlbase = self.urlbase, hostname = self.hostname, itemClass=classChooser("directory"))
        self.update_id += 1
        self.searchInContentPath(self.content)                              #recurency search
        #self.divideAllElementsInSeparateContainers()    
        
        self.wmc_mapping.update({'14': '0',
                                 '15': '0',
                                 '16': '0',
                                 '17': '0'
                                })
        self.init_completed()

    def divideAllElementsInSeparateContainers(self):
        #divide elements if too many childs
        try:
            for container in self.containers_map.values():
                self.divideElementsFromOneContainerIfNeeded(container)
        except Exception, e:
            print e
    
    def divideElementsFromOneContainerIfNeeded(self, container):
        if self.store[container].get_name() == 'Image':
            pass
        if (
            ( self.store[container].get_mimetype() in ['directory', 'root']) and
            (container != str(0)) and 
            (container not in self.mimetypes_containers.values()) and 
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
                            new_store_children_only[i].add_other_parent(i)
                            self.store[i].add_children(new_store_children_only[i])
        
    
    def createMimetypesContainers(self, item):
        if self.do_mimetypes_containers:
            if not self.mimetypes_root_created:
                self.mimetypes_containers = {}
                self.createContainer(
                                                 "mimetypes", 
                                                 parent = self.store[str(0)], 
                                                 path="Mimetypes", 
                                                 mimetype="directory", 
                                                 urlbase = self.urlbase, 
                                                 hostname = self.hostname, 
                                                 itemClass=classChooser("directory"))
                self.mimetypes_root_created = True
            itemmimetype = item.get_mimetype()
            if itemmimetype not in ['directory','root']: 
                if itemmimetype not in self.mimetypes_containers.keys():
                    self.mimetypes_containers[itemmimetype] = self.createContainer(
                                         str(itemmimetype), 
                                         parent = self.store[str(self.containers_map['mimetypes'])], 
                                         path = str(itemmimetype).replace("x-", ""), 
                                         mimetype="directory", 
                                         urlbase = self.urlbase, 
                                         hostname = self.hostname, 
                                         itemClass=classChooser("directory"),
                                         mimetype_container = True)
                self.store[str(self.mimetypes_containers[itemmimetype])].add_child(item)
                item.add_other_parent(str(self.mimetypes_containers[itemmimetype]))
                return str(self.mimetypes_containers[itemmimetype])
    
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
        
    def remove_item(self, id):
        print 'remove id', id
        try:
            item = self.store[id]
            parent = item.get_parent()
            other_parents = item.get_other_parents()
            for i in other_parents:
                self.store[i].remove_child(item)
            for k,v in self.mimetypes_containers.items():
                if self.store[v].get_child_count() <= 0:
                    del self.store[v]
                    del self.mimetypes_containers[k]
            item.remove()
            del self.store[id]
            if hasattr(self, 'update_id'):
                self.update_id += 1
                if self.server:
                    self.server.content_directory_server.set_variable(0, 'SystemUpdateID', self.update_id)
                #value = '%d,%d' % (parent.get_id(),parent_get_update_id())
                value = (parent.get_id(),parent.get_update_id())
                if self.server:
                    self.server.content_directory_server.set_variable(0, 'ContainerUpdateIDs', value)

        except Error, e:
            print e
            pass
    
    def get_by_id(self,object_id):
        self.info("looking for id %r", object_id)
        if isinstance(object_id, basestring):
            object_id = object_id.split('@',1)
            object_id = object_id[0]
        return self.store[object_id]
    
    def get_id_by_name(self, parent=str("0"), name=''):
        self.info('get_id_by_name %r (%r) %r' % (parent, type(parent), name))
        try:
            parent = self.store[parent]
            self.debug("%r %d" % (parent,len(parent.children)))
            for child in parent.get_children():
                self.debug("%r %r %r" % (child.get_name(),child.get_path(), name == child.get_path()))
                if name == child.get_path():
                    return child.id
        except:
            self.info(traceback.format_exc())
        self.debug('get_id_by_name not found')

        return None
    
    def searchInContentPath(self, content):
        for path in content:
            if isinstance(path, (list, tuple)):
                path = path[0]
            try:
                path = path.encode('utf-8')
                self.stepInto(path, self.store[str(self.containers_map['directories'])])
            except:
                formatted_lines = traceback.format_exc().splitlines()
                print formatted_lines
        self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Video']))
        self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Audio']))
        self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Image']))
                
    
    def stepInto(self, path, parent=None):
        containers = []
        all_containers = []
        parent = self.insert(path, parent)
        if parent != None:
            containers.append(parent)
            all_containers.append(parent.get_id())
        while len(containers)>0:
            single_container = containers.pop()
            try:
                for child in single_container.location.children():
                    cache_container = self.insert(child.path, single_container)
                    if cache_container:
                        containers.append(cache_container)
                        all_containers.append(cache_container.get_id())
            except UnicodeDecodeError, e:
                print "eee" + e
        all_containers = list(set(all_containers)) 
        for id in all_containers:   
            self.divideElementsFromOneContainerIfNeeded(id)
                
     
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
                if self.inotify is not None:
                    mask = IN_CREATE | IN_DELETE | IN_MOVED_FROM | IN_MOVED_TO | IN_CHANGED
                    self.inotify.watch(path, mask=mask, auto_add=False, callbacks=(self.notify,id))
                
                return self.store[id]
        except OSError, e:
            print "eee" +e
            
    def createItem(self, path, parent, mimetype):
        itemClass = classChooser(mimetype)
        if itemClass == None:
                return None
        
        if mimetype not in ('root', 'directory') and 'video' in mimetype:                               #id will be no id +
            _,ext =  os.path.splitext(path)
            object_id = str(self.getNextID()) + ext.upper()
            self.store[object_id] = MediaItem(object_id=object_id,
                                          itemClass=itemClass,
                                          path=path,
                                          parent=parent,
                                          urlbase=self.urlbase,
                                          hostname = self.hostname,
                                          mimetype=mimetype,
                                          store=self)
            self.createMimetypesContainers(self.store[object_id])
            if 'video' in mimetype:
                self.store[str(self.containers_map['Video'])].add_child(self.store[object_id])
                self.store[object_id].add_other_parent(str(self.containers_map['Video']))
            elif 'audio' in mimetype:
                self.store[str(self.containers_map['Audio'])].add_child(self.store[object_id])
                self.store[object_id].add_other_parent(str(self.containers_map['Audio']))
            elif 'image' in mimetype:
                self.store[str(self.containers_map['Image'])].add_child(self.store[object_id])
                self.store[object_id].add_other_parent(str(self.containers_map['Image']))
        else:
            object_id = self.createContainer(
                                 name = os.path.abspath(path), 
                                 parent = parent, 
                                 path = path, 
                                 mimetype = mimetype, 
                                 urlbase = self.urlbase, 
                                 hostname = self.hostname, 
                                 itemClass = itemClass)
        return object_id
        
        
    def notify(self, iwp, filename, mask, parameter=None):
        self.info("Event %s on %s %s - parameter %r" % (', '.join(self.inotify.flag_to_human(mask)), iwp.path, filename, parameter))
        path = iwp.path
        didsomething = False
        if filename:
            path = os.path.join(path, filename)
        if mask & IN_CHANGED:
            # FIXME react maybe on access right changes, loss of read rights?
            #print '%s was changed, parent %d (%s)' % (path, parameter, iwp.path)
            pass
        if(mask & IN_DELETE or mask & IN_MOVED_FROM):
            self.info('%s was deleted, parent %r (%s)' % (path, parameter, iwp.path))
            id = self.get_id_by_name(parameter,os.path.join(iwp.path,filename))
            if id != None:
                self.remove_item(id)
        if(mask & IN_CREATE or mask & IN_MOVED_TO):
            if mask & IN_ISDIR:
                self.info('directory %s was created, parent %r (%s)' % (path, parameter, iwp.path))
            else:
                self.info('file %s was created, parent %r (%s)' % (path, parameter, iwp.path))
            if self.get_id_by_name(parameter,os.path.join(iwp.path,filename)) is None:
                if os.path.isdir(path):
                    self.stepInto(path, self.get_by_id(parameter), self.ignore_file_pattern)
                    didsomething = True
                else:
                    if self.ignore_file_pattern.match(filename) == None:
                        self.insert(path, self.get_by_id(parameter))
                        didsomething = True
        if didsomething == True:
            self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Video']))
            self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Audio']))
            self.divideElementsFromOneContainerIfNeeded(str(self.containers_map['Image']))

    def create_containers(self,containers={}):
        root = ET.Element('Features')
        root.attrib['xmlns']='urn:schemas-upnp-org:av:avs'
        root.attrib['xmlns:xsi']='http://www.w3.org/2001/XMLSchema-instance'
        root.attrib['xsi:schemaLocation']='urn:schemas-upnp-org:av:avs http://www.upnp.org/schemas/av/avs.xsd' 
        e = ET.SubElement(root, 'Feature')
        e.attrib['name'] = "somename"
        e.attrib['version'] = str(1)
        
        if (len(containers)):
            for key, container in containers.items():
                i = ET.SubElement(e, 'container')
                id = str(container)
                i.attrib['id'] = id 
                if key == "imageItem":
                    i.attrib['type'] = "object.item.imageItem"
                elif key == "audioItem":
                    i.attrib['type'] = "object.item.audioItem"
                elif key == "videoItem":
                    i.attrib['type'] = "object.item.videoItem"
        xml = """<?xml version="1.0" encoding="utf-8"?>""" + ET.tostring( root, encoding='utf-8')
        return xml
            
    def get_containers_x_children(self):
        root = ET.Element('url:X_GetFeatureListResponse')
        root.attrib['xmlns:url']='urn:schemas-upnp-org:service:ContentDirectory:1'
        e = ET.SubElement(root, 'FeatureList')
        e.text = self.create_containers(self.feature_list)
        r = """<?xml version="1.0" encoding="utf-8"?>""" + ET.tostring( root, encoding='utf-8')
        return r
    
    def get_x_containers(self):
        return self.feature_list

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