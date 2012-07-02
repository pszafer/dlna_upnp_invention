from django.db import models

class Content(models.Model):
    path = models.CharField(max_length = 400)

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
    
class DBAddress(models.Model):
    ip_address = models.CharField(max_length=20)
    port = models.IntegerField(default=0)
    
class ServiceStatus(models.Model):
    name = models.CharField(max_length=20)
    working = models.BooleanField(default=False)

class Language(models.Model):
    language = models.CharField(max_length=3)

ServiceStatus.objects.all().delete()
ServiceStatus(name="manage").save()
ServiceStatus(name="upnp").save()
DBAddress.objects.all().delete()
DBAddress(ip_address='', port=0).save()

if (Language and Language.objects.all().count() == 0):
    Language(language="en").save()