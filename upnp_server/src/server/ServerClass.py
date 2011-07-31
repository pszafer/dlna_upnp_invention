'''
Created on 05-07-2011

@author: Pawel Szafer, pszafer@gmail.com
'''

from twisted.internet import reactor
from coherence.base import Coherence 
import gnome.ui
import gnomevfs
from server import helpers

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
#header = {}
#header['user-agent'] = 'Microsoft-Windows/6.1 UPnP/1.0 Windows-Media-Player/12.0.7601.17514 DLNADOC/1.50 (MS-DeviceCaps/1024)'
#test = header['user-agent'].find('blee')
#print test

#filename = "file:///home/xps/Wideo/test/test2/Friends_S06_E20.avi"
#filename = "/home/xps/.thumbnails/normal/f1d2e7cf33db9de55a6fe49b91a63b1b.png"

#hash_from_path = str(id(filename))
#print hash_from_path

import subprocess

def getFileMetadata(filename):
  result = subprocess.Popen(["ffprobe", filename],
    stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
  duration_line = [x for x in result.stdout.readlines() if "Duration" in x]
  duration = duration_line[(duration_line.index('Duration: ',) + len('Duration: ')):duration_line.index(', start')]
  return duration

def create_thumbnail_via_gnome(uri):
    mimetype = gnomevfs.get_mime_type(uri)
    thumbFactory = gnome.ui.ThumbnailFactory(gnome.ui.THUMBNAIL_SIZE_NORMAL)
    if thumbFactory.can_thumbnail(uri, mimetype,0):
        thumbnail = thumbFactory.generate_thumbnail(uri, mimetype)
        print "here"
        if thumbnail != None:
            thumbFactory.save_thumbnail(thumbnail, uri, 0)
            print "passed"


#uri = "file:///home/xps/Wideo/test/test2/Friends_S06_E20.avi"
#create_thumbnail_via_gnome(uri)

#Duration: 00:21:55.64, start: 0.000000, bitrate: 1485 kb/s
#    print "test"

import Image
im = Image.open("/home/xps/Obrazy/toyota_public/toyota_1.jpg")
print im.size
int = "aaa"
b= None
for i in im.size:
    b += str(i)+"x"
b = b[:len(b)-1]
print b

#dur = str(getFileMetadata("/home/xps/Wideo/test/test2/Friends_S06_E20.avi"))
#ind = dur.index(', start')
#print ind
#print max(dur)
#dur1 = dur[(dur.index('Duration: ',) + len('Duration: ')):dur.index(', start')]
#print dur1
#print "stop"