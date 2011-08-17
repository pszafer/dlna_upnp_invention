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
    db_path = models.CharField(max_length=200)
    created = models.BooleanField(default=False)
    session_id = models.CharField(max_length=300)
    
    
            
admin.site.register(BlogPost)