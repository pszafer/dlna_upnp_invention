# Create your views here.

#from settings_app.models import MediaServerSettings as SettingsDB
from dlnaupnpmanage.models import DBContainer, Content, DBAddress, ServiceStatus, Language

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError, HttpRequest,\
    QueryDict
from django.template.response import TemplateResponse
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from ccm.Settings import Setting
from django.views.generic.list_detail import object_list
from django.template import RequestContext
import simplejson as json2



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
                                  max_path = all_list['max_child_items'],
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
        try:
            from django.utils import simplejson as simplejs
            entries = DBContainer.objects.all().values().get()
            del entries['uuid']
            del entries['created']
            t = 'dlnaupnpmanage/settings.html'
            return render_to_response(t, entries, context_instance=RequestContext(request))
        except Exception:
            response = TemplateResponse(request, 'dlnaupnpmanage/settings.html', {})
            return response

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
def changeLanguage(request):
    if request.is_ajax() and request.POST:
        #jsona = dict(method=None,id=None,params=[])
        currentLang = Language.objects.all().values().get()
        json = str(request.POST['Language'])
        if (json == "pl" or json == "en"):
            if json is not currentLang['language']:
                Language.objects.all().delete()
                lang = Language(language=json)
                lang.save()
                currentLang = json
        response = HttpResponse()
        response['Content-Type'] = "application/json"
        response.write("{\"Language\":\""+currentLang+"\"}")
        return response

@csrf_exempt     
def saveSettings(request):
    if request.is_ajax() and request.POST:
        json = json2.dumps(request.POST)
        #TODO send this json to server and load to db
        #return HttpResponseBadRequest('Only POST accepted')
        from webob import Request as Requ
        req = Requ.blank("http://localhost:7777/")
        req.method = 'POST'
        req.content_type = 'application/json'
        #server_name, transcoding='no', ip_addr = None, port = 0, enable_inotify = True, max_child_items = 300
        lista = request.POST.lists()
        json = dict(method="set_settings",id=None,params=[lista])
        from simplejson import loads, dumps
        req.body = dumps(json)
        from wsgiproxy.exactproxy import proxy_exact_request
        resp = req.get_response(proxy_exact_request)
        json = loads(resp.body)
        all_list = json['result']
        response = HttpResponse()
        response['Content-Type'] = "application/json"
        if all_list and not 'False' in all_list:
            DBContainer.objects.all().delete()
            dbContainer = DBContainer(ip_address=all_list['ip_addr'], 
                                  created=True, 
                                  session_id=request.session.session_key,
                                  port = all_list['port'],
                                  name = all_list['name'],
                                  uuid = all_list['uuid'],
                                  do_mimetype_container = all_list['do_mimetype_container'],
                                  transcoding = all_list['transcoding'],
                                  max_path = all_list['max_child_items'],
                                  enable_inotify= all_list['enable_inotify']
                                  )
            DBAddress.objects.all().delete()
            DBAddress(ip_address=all_list['ip_addr'], port = all_list['port']).save()
            dbContainer.save()
            response.write(json2.dumps(all_list))
            return response
        response = HttpResponse()
        response['Content-Type'] = "application/json"
        response.write("false")
        return response