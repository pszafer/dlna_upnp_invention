'''
Created on 08-07-2011

@author: xps
'''
import Database
from server.Database import DBCursor, DBMedia
from coherence.upnp.core import DIDLLite

parameters = {
              'port' : 0,
              'ip_addr': None,
              }

from coherence import log

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
        from coherence.upnp.devices.media_server import MediaServer
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
        content = ["/home/xps/Wideo/test/", "/home/xps/Obrazy/majowka2011/connect", "/home/xps/Muzyka/mp3"]
        kwargs['content']= content
        kwargs['urlbase'] = coherence.hostname
        kwargs['transcoding'] = 'no'
        kwargs['do_mimetype_container'] =  True
        kwargs['max_child_items'] = 4
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

#from coherence.extern.et import ET, ElementInterface
#from coherence.upnp.core import DIDLLite
#class Child(object):
#    def __init__(self):
#        self.anything = "test"
#class Element(ElementInterface):
#    def __init__(self):
#        ElementInterface.__init__(self, 'DIDL-Lite', {})
#        self.attrib['xmlns'] = 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/'
#        self.attrib['xmlns:dc'] = 'http://purl.org/dc/elements/1.1/'
#        self.attrib['xmlns:upnp'] = 'urn:schemas-upnp-org:metadata-1-0/upnp/'
#        self.attrib['xmlns:dlna'] = 'urn:schemas-dlna-org:metadata-1-0'
#        self.attrib['xmlns:pv'] = 'http://www.pv.com/pvns/'
#        self._items = []
#        self._items.append("aaa")
#        self._children = []
#        #self._children.append(5)
#
#did = DIDLLite.VideoItem()
##didd.addItem(did)
#aaa = did.toString()
#
#print "t" + aaa