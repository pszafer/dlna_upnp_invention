'''
Created on 30-07-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8

'''

from gnome import ui
import mimetypes
import gnomevfs
import re
import os, gio
import Image
from urllib2 import quote

mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/x-musepack', '.mpc')
mimetypes.add_type('audio/x-wavpack', '.wv')
mimetypes.add_type('audio/x-wav', '.wav')
mimetypes.add_type('audio/mpeg', '.flac')

mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/avi', '.divx')
mimetypes.add_type('video/avi', '.avi')
mimetypes.add_type('video/ogg', '.ogv')
mimetypes.add_type('video/avi', '.mkv')
mimetypes.add_type('text/plain', '.srt')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpg')
#TODO MP3 SUPPORT LG

#mimetypes.add_type('video/x-matroska', '.mkv')
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
    f = None
    if filename is not None:
        f = os.path.abspath(filename)
        mimetype,_ = mimetypes.guess_type(f, strict=False)
        dlna_pn = 'DLNA.ORG_PN=JPEG_TN'
        return f,mimetype,dlna_pn
    return None,None,None

'''
Creating thumbnails with other tools like Image, ffmpegthumbnailer
@param uri: URI to file like file:///path/fiile.jpg
@param hash: filename for thumbnail
@param mimetype: mimetype of main file
'''
def create_thumbnail(uri, hash, mimetype):
    directory = os.path.expanduser('~')+"/.thumbnails/dlna"
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)
    else:
        os.mkdir(directory)
    if os.path.exists(directory) and os.path.isdir(directory):
        new_path = directory + "/" + hash + ".jpg"
    _, path = uri.split("file://") 
    #ffmpegthumbnailer -i Friends_S06_E20.avi -a -s 120 -t 33% -o out.jpg
    if os.path.exists(new_path):
        return new_path
    if 'video' in mimetype:
        os.system("ffmpegthumbnailer -i \"%s\" -a -t %s -s 120x120 -o %s" % (path, "33%", new_path))
    elif 'image' in mimetype:
        size = 120, 120
        im = Image.open(path)
        im.thumbnails(size, Image.ANTIALIAS)
        im.save(new_path, "JPEG")
    if not os.path.exists(new_path):
        return None 
    else:
        return new_path
    
    
def create_thumbnail_via_gnome(mimetype, uri):
    #return False #Orepair it
    try:
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
    except:
        return False
'''
Copy file from ~/.thumbnail/normal/*.png to ~/.thumbnail/dlna/*.jpg
ONLY IF NOT EXISTS
@param path:full path to png file
@param hash: only name of file
'''
def copy_file_and_change_path(path, hash):
    directory = os.path.expanduser('~')+"/.thumbnails/dlna"
    if os.path.exists(directory):
        if not os.path.isdir(directory):
            os.mkdir(directory)
    else:
        os.mkdir(directory)
    if os.path.exists(directory) and os.path.isdir(directory):
        new_path = directory + "/" + hash + ".jpg"
        if not os.path.exists(new_path):
            im = Image.open(path)
            im.save(new_path)
        return new_path
  
def import_thumbnail(filepath):
    uriUTF = "file://" + quote(filepath).encode('utf-8')#quote(path).encode('utf-8')              #change path to utf-8 path
    uri = "file://" + filepath
    import hashlib
    hash = hashlib.md5(uriUTF).hexdigest()
    thumbFactory = ui.ThumbnailFactory(ui.THUMBNAIL_SIZE_NORMAL)
    path = os.path.expanduser('~') + "/.thumbnails/normal/"+hash+".png"
    if path is None or not os.path.exists(path):
        path = ui.thumbnail_path_for_uri(gnomevfs.get_uri_from_local_path(os.path.abspath(uri)), 'normal')
    if path is None or not os.path.exists(path):
        path = thumbFactory.lookup(uri,0)
    if path is None or not os.path.exists(path):
        #create thumbnail
        mimetype, _ = mimetypes.guess_type(uri, strict=False)
        result = create_thumbnail_via_gnome(mimetype, uri)
        if result == False:
            return create_thumbnail(uri, hash, mimetype)
        #TODO prepare for not exist file after create thumbnail
    new_path = copy_file_and_change_path(path, os.path.basename(path))
    return new_path



def getFileMetadata(filename):#TODO repair time!! music/flac
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
        if information.has_key('duration'):
            duration_line = bitrate_line = str(information['duration'])
            duration_line = duration_line[(duration_line.index('Duration: ',) + len('Duration: ')):duration_line.index(', start')]
            returned['duration'] = duration_line[0:duration_line.index('.')]
            returned['bitrate'] = bitrate_line[(bitrate_line.index('bitrate: ',) + len('bitrate: ')):len(bitrate_line)]
        if information.has_key('video'):
            video_line = str(information['video'])
            returned['resolution'] = (", ".join(video_line.split(", ")[2:])).split(" ")[0].strip(",") #get resolution
        if information.has_key('audio'):
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