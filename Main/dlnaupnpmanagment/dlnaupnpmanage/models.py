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
    
admin.site.register(BlogPost)