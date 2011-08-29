# Create your views here.
from dlnaupnpmanagment.dlnaupnpmanage.models import DBContainer, Content, DBAddress
from django.http import HttpResponse, HttpResponseServerError, HttpRequest
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from ccm.Settings import Setting
from django.views.generic.list_detail import object_list
from django.template import RequestContext

#DONE
def index(request):
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
        return object_list(request, all_list, template_name='dlnaupnpmanage/status.html')


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


#DONE
def serverstatus(request):
    if request.is_ajax():
        try:
            json = dict(method="echo",id=None,params=[])
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
            response['Content-Type'] = "application/json"
            response.write(dumps(all_list))
            return response
        except Exception, e:
            response = HttpResponse()
            response['Content-Type'] = "application/json"
            response.write("{\"Status\":\"Failed\"}")
            return response

#DONE
def upnpserverstatus(request):
    if request.is_ajax():
        try:
            json = dict(method="echo",id=None,params=[])
            from webob import Request as Requ
            entries = DBAddress.objects.all()[:1].values().get()
            ip = str(entries['ip_address'])
            port = str(entries['port'])
            if ip is None or port == str(0):
                checkAddress(request)
                entries = DBAddress.objects.all().values().get()
                ip = str(entries['ip_address'])
                port = str(entries['port'])
            address = "http://" + ip + ":" + port
            print "Address %s" % address
            req = Requ.blank(address)
            req.method = 'GET'
            from simplejson import loads, dumps
            from wsgiproxy.exactproxy import proxy_exact_request
            resp = req.get_response(proxy_exact_request)
            response = HttpResponse()
            response['Content-Type'] = "application/json"
            response.write("{\"Status\":\"Running\"}")
            return response
        except Exception, e:
            print "Exception %s" % str(e)
            response = HttpResponse()
            response['Content-Type'] = "application/json"
            response.write("{\"Status\":\"Failed\"}")
            return response
        
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
    json = dict(method="add_content",id=None,params=["/home/xps/Wideo/test/"])
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

def runserver(request):
    execute_on_daemon("start")
    httpResponse = HttpResponse()
    httpResponse['Content-Type'] = "text"
    httpResponse.write("OK")
    return httpResponse  

def stopserver(request):
    execute_on_daemon("stop")
    httpResponse = HttpResponse()
    httpResponse['Content-Type'] = "text"
    httpResponse.write("OK")
    return httpResponse  

def execute_on_daemon(order):
    from subprocess import Popen, PIPE, STDOUT
    import os
    new_dir, _ = os.path.split(os.path.normpath(os.path.dirname(__file__)))
    new_dir, _ = os.path.split(new_dir)
    new_dir = os.path.join(new_dir, "dlnaupnpserver/MediaDaemon.py")
    subprocess.Popen(["python", new_dir, order])

def checkAddress(request):
    try:
        json = dict(method="getaddress",id=None,params=[])
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
        if all_list is not None:
            DBAddress.objects.all().delete()
            DBAddress(ip_address=all_list['ip'],
                      port = all_list['port']).save()
        httpResponse = HttpResponse()
        httpResponse['Content-Type'] = "text"
        httpResponse.write("OK")
        return httpResponse
    except Exception:
        httpResponse = HttpResponse()
        httpResponse['Content-Type'] = "text"
        httpResponse.write("Error")
        return httpResponse