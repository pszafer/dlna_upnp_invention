'''
Created on 30-07-2011

@author: xps
'''

from gnome import ui
import mimetypes
import gnomevfs
import re
import os
import Image

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
mimetypes.add_type('video/avi', '.mkv')
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
    dlna_pn = 'DLNA.ORG_PN=JPEG_TN'
    return os.path.abspath(f),mimetype,dlna_pn

def create_thumbnail(uri):
    directory = os.path.expanduser('~')+"/.thumbnails/dlna"
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)
    else:
        os.mkdir(directory)
    if os.path.exists(directory) and os.path.isdir(directory):
        import hashlib
        hash = hashlib.md5(uri).hexdigest()
        new_path = directory + "/" + hash + ".jpg"
    _, path = uri.split("file://") 
    #ffmpegthumbnailer -i Friends_S06_E20.avi -a -s 120 -t 33% -o out.jpg
    os.system("ffmpegthumbnailer -i %s -a -t %s -s 120x120 -o %s" % (path, "33%", new_path))
    return new_path
    
    
def create_thumbnail_via_gnome(uri):
    mimetype = mimetype = gnomevfs.get_mime_type(uri)
    thumbFactory = ui.ThumbnailFactory(ui.THUMBNAIL_SIZE_NORMAL)
    if thumbFactory.can_thumbnail(uri, mimetype,0):
        thumbnail = thumbFactory.generate_thumbnail(uri, mimetype)
        if thumbnail != None:
            thumbFactory.save_thumbnail(thumbnail, uri, 0)
            return True
        else:
            return False
    else:
        return False

def copy_file_and_change_path(path, hash):
    directory = os.path.expanduser('~')+"/.thumbnails/dlna"
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)
    else:
        os.mkdir(directory)
    if os.path.exists(directory) and os.path.isdir(directory):
        new_path = directory + "/" + hash + ".jpg"
        im = Image.open(path)
        im.save(new_path)
        return new_path
  
def import_thumbnail(uri):
    import hashlib
    hash = hashlib.md5(uri).hexdigest()
    
    path = os.path.expanduser('~') + "/.thumbnails/normal/"+hash+".png"
    mimetype, _ = mimetypes.guess_type(uri, strict=False)
    if not os.path.exists(path):
        result = create_thumbnail_via_gnome(uri)
        if result == False:
            return create_thumbnail(uri)
    new_path = copy_file_and_change_path(path, hash)
    return new_path



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