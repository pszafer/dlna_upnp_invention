'''
Created on 05-07-2011

@author: Pawel Szafer, pszafer@gmail.com
'''

from twisted.internet import reactor
from coherence.base import Coherence 

class ServerClass(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print "initek"
        
    def check_device(self, device):
        print "check device"
        print "found device %s of type %s - %r" %(device.get_friendly_name(),
                                              device.get_device_type(),
                                              device.client)
                
    def start(self):
        print "I'm started"
        config = {'logmode':'warning'}
        c = Coherence(config)
        print "to connect"
        c.connect(self.check_device, 'Coherence.UPnP.Device.detection_completed')
        
print "start"
#myClass =  ServerClass()
#reactor.callWhenRunning(ServerClass().start)
#reactor.run()
header = {}
header['user-agent'] = 'Microsoft-Windows/6.1 UPnP/1.0 Windows-Media-Player/12.0.7601.17514 DLNADOC/1.50 (MS-DeviceCaps/1024)'
test = header['user-agent'].find('blee')
print test

filename = "file:///home/xps/Wideo/test/test2/Friends_S06_E20.avi"
filename = "/home/xps/.thumbnails/normal/f1d2e7cf33db9de55a6fe49b91a63b1b.png"

hash_from_path = str(id(filename))
print hash_from_path

print "stop"