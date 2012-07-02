# Create your views here.

#from settings_app.models import MediaServerSettings as SettingsDB
from dlnaupnpmanage.models import DBContainer, Content, DBAddress, ServiceStatus, Language

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError, HttpRequest,\
    QueryDict
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from ccm.Settings import Setting
from django.views.generic.list_detail import object_list
from django.template import RequestContext



def settings(request):
    try:
        json = dict(method="get_settings",id=None,params=[])
        from webob import Request as Requ
        req = Requ.blank("http://localhost:7777/")
        req.method = 'POST'
        req.content_type = 'application/json'
        from simplejson import loads, dumps
        req.body = dumps(json)
        from wsgiproxy.exactproxy import proxy_exact_request
        resp = req.get_response(proxy_exact_request)
        json = loads(resp.body)
        all_list = json['result']
        DBContainer.objects.all().delete()
        dbContainer = DBContainer(ip_address=all_list['ip_addr'], 
                                  created=True, 
                                  session_id=request.session.session_key,
                                  port = all_list['port'],
                                  name = all_list['name'],
                                  uuid = all_list['uuid'],
                                  do_mimetype_container = all_list['do_mimetype_container'],
                                  transcoding = all_list['transcoding'],
                                  enable_inotify= all_list['enable_inotify']
                                  )
        DBAddress.objects.all().delete()
        DBAddress(ip_address=all_list['ip_addr'],
                  port = all_list['port']).save()
        dbContainer.save()
    except Exception, e:
        pass
    if request.is_ajax():
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        response.write(all_list)
        return response
    else:
        from django.utils import simplejson as simplejs
        entries = DBContainer.objects.all().values().get()
        del entries['uuid']
        del entries['created']
        
        t = 'dlnaupnpmanage/settings.html'
        return render_to_response(t, entries, context_instance=RequestContext(request))

def getuuid(request):
    entries = DBContainer.objects.all().values().get()
    response = HttpResponse()
    response['Content-Type'] = "application/json"
    response.write("{\"UUID\":\""+entries['uuid']+"\"}")
    return response
    
def setname(request):
    json = dict(method="add_content",id=None,params=["/home/xps/Wideo/test/aaa"])
    from webob import Request as Requ
    req = Requ.blank("http://localhost:7777/")
    req.method = 'POST'
    req.content_type = 'application/json'
    from simplejson import loads, dumps
    req.body = dumps(json)
    from wsgiproxy.exactproxy import proxy_exact_request
    resp = req.get_response(proxy_exact_request)
    json = loads(resp.body)
    all_list = json['result']
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(all_list)
    return response

@csrf_exempt     
def saveSettings(request):
    if request.is_ajax() and request.POST:
        import simplejson as json2
        json = json2.dumps(request.POST)
        #TODO send this json to server and load to db
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        response.write(list)
        return response
        #return HttpResponseBadRequest('Only POST accepted')
#        from webob import Request as Requ
#        req = Requ.blank("http://localhost:7777/")
#        req.method = 'POST'
#        req.content_type = 'application/json'
#        from simplejson import loads, dumps
#        req.body = dumps(json)
#        from wsgiproxy.exactproxy import proxy_exact_request
#        resp = req.get_response(proxy_exact_request)
#        json = loads(resp.body)
#        all_list = json['result']
#        if not 'False' in all_list: