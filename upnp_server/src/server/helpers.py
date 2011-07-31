'''
Created on 30-07-2011

@author: xps
'''

import gnome.ui
import mimetypes
import gnomevfs
import re
import os

mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/x-musepack', '.mpc')
mimetypes.add_type('audio/x-wavpack', '.wv')
mimetypes.add_type('audio/x-wav', '.wav')

mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/avi', '.divx')
mimetypes.add_type('video/avi', '.avi')
mimetypes.add_type('video/ogg', '.ogv')
#mimetypes.add_type('video/x-matroska', '.mkv')
mimetypes.add_type('video/x-mkv', '.mkv')
mimetypes.add_type('text/plain', '.srt')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpg')


## Sorting helpers
NUMS = re.compile('([0-9]+)')
def _natural_key(s):
    # strip the spaces
    try:
        s = s.get_name().strip()
        return [ part.isdigit() and int(part) or part.lower() for part in NUMS.split(s) ]
    except Exception, e:
        print e

def _find_thumbnail(filename,thumbnail_folder='.thumbs'):
    """ looks for a thumbnail file of the same basename
        in a folder named '.thumbs' relative to the file

        returns the filename of the thumb, its mimetype and the correspondig DLNA PN string
        or throws an Exception otherwise
    """
    f = filename
    mimetype,_ = mimetypes.guess_type(f, strict=False)
    dlna_pn = 'DLNA.ORG_PN=PNG_TN'
    return os.path.abspath(f),mimetype,dlna_pn

def create_thumbnail(filename):
    import os, sys
    import Image
    
    # Use "ffmpeg -i <videofile>" to get total length by parsing the error message
    chout, chin, cherr = os.popen3("ffmpeg -i %s" % filename)
    out = cherr.read()
    dp = out.index("Duration: ")
    duration = out[dp+10:dp+out[dp:].index(",")]
    hh, mm, ss = map(float, duration.split(":"))
    total = (hh*60 + mm)*60 + ss
    
    # Use "ffmpeg -i <videofile> -ss <start> frame<nn>.png" to extract 9 frames
    i = 1
    t = 2
    os.system("ffmpeg -i %s -s 64x64 -ss %0.3fs frame%i.png" % (filename, t, i))
    
    # Make a full 3x3 image by pasting the snapshots
    img = Image.open("frame%i.png" % (i))
    
def create_thumbnail_via_gnome(uri):
    mimetype = mimetype = gnomevfs.get_mime_type(uri)
    thumbFactory = gnome.ui.ThumbnailFactory(gnome.ui.THUMBNAIL_SIZE_NORMAL)
    if thumbFactory.can_thumbnail(uri, mimetype,0):
        thumbnail = thumbFactory.generate_thumbnail(uri, mimetype)
        if thumbnail != None:
            thumbFactory.save_thumbnail(thumbnail, uri, 0)
            return True
        else:
            return False
    else:
        return False

  
def import_thumbnail(uri):
    import hashlib
    hash = hashlib.md5(uri).hexdigest()
    path = "/home/xps/.thumbnails/normal/"+hash+".png"
    mimetype, _ = mimetypes.guess_type(uri, strict=False)
    if not os.path.exists(path):
        result = create_thumbnail_via_gnome(uri)
        if result == False:
            pass    #TODO create thumbnail via ffmpeg or other way, different with mimetype
    return path

def getFileMetadata(filename):
    import subprocess
    information = {}
    try:
        result = subprocess.Popen(["ffprobe", filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        
        was_duration = False
        for x in result.stdout.readlines():
            if "Duration" in x:
                information['duration'] = x
                was_duration = True
                continue
            if was_duration:
                if "Video" in x:
                    information['video'] = x
                if "Audio" in x:
                    information["audio"] = x
        returned = {}
        duration_line = bitrate_line = str(information['duration'])
        duration_line = duration_line[(duration_line.index('Duration: ',) + len('Duration: ')):duration_line.index(', start')]
        returned['duration'] = duration_line[0:duration_line.index('.')]
        returned['bitrate'] = bitrate_line[(bitrate_line.index('bitrate: ',) + len('bitrate: ')):len(bitrate_line)]
        video_line = str(information['video'])
        returned['resolution'] = (", ".join(video_line.split(", ")[2:])).split(" ")[0].strip(",") #get resolution
        audio_line = str(information['audio'])
        returned['audio_channels'] = (", ".join(audio_line.split(", ")[2:])).split(" ")[0].strip(",") #get channels
    except Exception as e:
        print e
    return returned

def s2hms(t):
    # Converts seconds to a string formatted H:mm:ss
    if t > 3600:
        h = int(t/3600)
        r = t-(h*3600)
        m = int(r / 60)
        s = int(r-(m*60))
        return '{0}:{1:02n}:{2:02n}'.format(h,m,s)
    else:
        m = int(t / 60)
        s = int(t-(m*60))
        return '{0}:{1:02n}'.format(m,s)