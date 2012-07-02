from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, databrowse
import dlnaupnpmanagment
from django.views.generic.simple import direct_to_template
from django.conf import settings
from dlnaupnpmanagment import dlnaupnpmanage
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic import RedirectView
admin.autodiscover()

js_info_dict = {
    'packages': ('dlnaupnpmanagment',),
}

urlpatterns = patterns('',
    # Example:
 #  url('', RedirectView.as_view(url='/dlnaupnpmanagment/status'), name='some_redirect'),
    url(r'^dlnaupnpmanagment/index', direct_to_template, {'template': 'dlnaupnpmanage/index.html'}),
    url(r'^dlnaupnpmanagment/$', redirect_to, {'url': '/dlnaupnpmanagment/status'}),
    url(r'^dlnaupnpmanagment/status', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.index'),
    url(r'^dlnaupnpmanagment/media', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_media.media'),
    url(r'^dlnaupnpmanagment/serverstatus', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.serverstatus'),
    url(r'^dlnaupnpmanagment/upnpserverstatus', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.upnpserverstatus'),
    url(r'^dlnaupnpmanagment/settings', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_settings.settings'),
    url(r'^dlnaupnpmanagment/setname', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_settings.setname'),
    url(r'^dlnaupnpmanagment/update', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.update'),
    url(r'^dlnaupnpmanagment/runserver', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.runserver'),
    url(r'^dlnaupnpmanagment/stopserver', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.stopserver'),
    url(r'^dlnaupnpmanagment/checkAddress', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.checkAddress'),
    url(r'^dlnaupnpmanagment/getuuid', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_status.getuuid'),
    url(r'^dlnaupnpmanagment/addContent', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_media.addContent'),
    url(r'^dlnaupnpmanagment/saveSettings', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_settings.saveSettings'),
    url(r'^dlnaupnpmanagment/logs', 'dlnaupnpmanagment.dlnaupnpmanage.views.views_logs.logs'),
    (r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^databrowse/(.*)', databrowse.site.root),
    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),
)