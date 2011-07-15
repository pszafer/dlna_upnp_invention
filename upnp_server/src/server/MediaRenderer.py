'''
Created on 07-07-2011

@author: xps
'''

from twisted.internet import reactor
from coherence.base import Coherence
from coherence.upnp.devices.control_point import ControlPoint

def state_variable_change(variable):
    if variable.name == 'CurrentTrackMetaData':

        if variable.value != None and len(variable.value)>0:
            try:
                from coherence.upnp.core import DIDLLite
                elt = DIDLLite.DIDLElement.fromString(variable.value)
                for item in elt.getItems():
                    print "now playing: %r - %r (%s/%r)" % (item.artist, item.title, item.id, item.upnp_class)
            except SyntaxError:
                #print "seems we haven't got an XML string"
                return
    elif variable.name == 'TransportState':
        print variable.name, 'changed from', variable.old_value, 'to', variable.value

def media_renderer_found(client,udn):
    print "media_renderer_found", client
    print "media_renderer_found", client.device.get_friendly_name()
    client.av_transport.subscribe_for_variable('CurrentTrackMetaData', state_variable_change)
    client.av_transport.subscribe_for_variable('TransportState', state_variable_change)

def media_renderer_removed(udn):
    print "media_renderer_removed", udn

def start():
    control_point = ControlPoint(Coherence({'logmode':'warning'}),
                                 auto_client=['MediaRenderer'])
    control_point.connect(media_renderer_found, 'Coherence.UPnP.ControlPoint.MediaRenderer.detected')
    control_point.connect(media_renderer_removed, 'Coherence.UPnP.ControlPoint.MediaRenderer.removed')


reactor.callWhenRunning(start)
reactor.run()