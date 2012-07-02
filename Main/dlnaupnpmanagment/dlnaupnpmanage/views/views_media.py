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


#DONE
def media(request):
    if request.is_ajax():
        print "index"
    else:
        from django.views.generic import list_detail
        all_list = Content.objects.all()
        if len(all_list) == 0:
            list = update_content()
            if list is not None:
                for item in list:
                    Content(path = item['content']).save()
                    all_list = Content.objects.all()
        return object_list(request, all_list, template_name='dlnaupnpmanage/media.html')
  
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


def update_content():
    try:
        json = dict(method="get_content",id=None,params=[])
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
        return all_list
    except Exception, e:
        return None
#get_content

def update(request):
    print "update"
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    json = serializers.serialize("json", BlogPost.objects.all())
    #from JSONRPCServer import JsonClient
    #client = JsonClient()
    #client.connect()
    #client.sendObject(json)
    response.write(json)
    all_list = DBContainer.objects.all()
    if len(all_list) == 0:
        DBContainer.create()
    all_list = DBContainer.objects.all()    
    print all_list
    return response

@csrf_exempt
def addContent(request):
    if request.is_ajax() and request.POST:
        json = dict(method="add_new_path",id=None,params=[request.POST.get('content')])
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
        if not 'False' in all_list:
            list = update_content()
            response = HttpResponse()
            response['Content-Type'] = "text/javascript"
            response.write(list)
            return response
        #return HttpResponseBadRequest('Only POST accepted')

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