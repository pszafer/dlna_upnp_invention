# Create your views here.
from dlnaupnpmanagment.dlnaupnpmanage.models import DBContainer, BlogPost
from django.http import HttpResponse, HttpResponseServerError, HttpRequest
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from ccm.Settings import Setting
from django.views.generic.list_detail import object_list
from django.template import RequestContext

def index(request):
    if request.is_ajax():
        print "index"
    else:
        from django.views.generic import list_detail
        all_list = BlogPost.objects.all()
        list_db = DBContainer.objects.all()
        return object_list(request, all_list, template_name='dlnaupnpmanage/status.html')

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

def run_server(request):
    from subprocess import Popen, PIPE, STDOUT
    import os
    new_dir, _ = os.path.split(os.path.normpath(os.path.dirname(__file__)))
    new_dir, _ = os.path.split(new_dir)
    new_dir = os.path.join(new_dir, "dlnaupnpserver/MediaServer.py")
    subprocess.Popen(["python", new_dir])
    #print p.stdout.read()
    httpResponse = HttpResponse()
    httpResponse['Content-Type'] = "text"
    httpResponse.write("text")
    return httpResponse  

def database(request):
    from django.utils import simplejson
    if request.is_ajax() and request.method == 'POST':
        json_data = simplejson.loads(request.raw_post_data)
        try:
            data = json_data['data']
        except KeyError:
            return HttpResponseServerError("Malformed data")
        return HttpResponse("Got json data")

def search_for_db(session_id):
        import os.path
        path, _ = os.path.split(os.path.normpath(os.path.dirname(__file__)))
        path, _ = os.path.split(path)
        path = os.path.join(path, "dlnaupnpserver/.settings.dat")
        if os.path.exists(path):
            DBContainer.objects.all().delete()
            file = open(path)
            file.readline()
            ip_address = str(file.readline()).replace("\n","").decode("hex")
            db_path = str(file.readline()).decode("hex")
            dbContainer = DBContainer(ip_address=ip_address, db_path = db_path, created=True, session_id=session_id)
            dbContainer.save()
