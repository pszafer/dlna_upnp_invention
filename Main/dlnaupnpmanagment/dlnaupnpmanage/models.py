from django.db import models
from django.contrib import admin

class BlogPost(models.Model):
    #title = models.CharField(max_length = 150)
    body = models.TextField()
    timestamp = models.DateTimeField()
    
    def __unicode__(self):
        return "[%s] %s" % (
                            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            self.body
                            )
    
    

class DBContainer(models.Model):
    ip_address = models.CharField(max_length=20)
    port = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    uuid = models.CharField(max_length=200)
    created = models.BooleanField(default=False)
    session_id = models.CharField(max_length=300)
    do_mimetype_container = models.CharField(max_length=200)
    transcoding = models.CharField(max_length=10)
    enable_inotify = models.BooleanField(default=True)
    
    
            
admin.site.register(BlogPost)