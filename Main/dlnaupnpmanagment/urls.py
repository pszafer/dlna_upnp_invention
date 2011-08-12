from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, databrowse
import dlnaupnpmanagment
from django.views.generic.simple import direct_to_template
from django.conf import settings
from dlnaupnpmanagment import dlnaupnpmanage
from dlnaupnpmanagment.dlnaupnpmanage.models import BlogPost
from django.views.generic import list_detail
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    url(r'^dlnaupnpmanagment/index', direct_to_template, {'template': 'dlnaupnpmanage/index.html'}),
    url(r'^dlnaupnpmanagment/halo', 'dlnaupnpmanagment.dlnaupnpmanage.views.halo'),
    url(r'^dlnaupnpmanagment/update', 'dlnaupnpmanagment.dlnaupnpmanage.views.update'),
    url(r'^dlnaupnpmanagment/iii', list_detail.object_list, {'queryset' : BlogPost.objects.all()}),
    (r'^databrowse/(.*)', databrowse.site.root),
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)