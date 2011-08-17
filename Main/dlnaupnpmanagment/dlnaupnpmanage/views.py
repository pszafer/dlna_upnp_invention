# Create your views here.
from dlnaupnpmanagment.dlnaupnpmanage.models import BlogPost, DBContainer
from django.template import loader
from django.template.context import Context, RequestContext
from django.http import HttpResponse, HttpResponseServerError
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from ccm.Settings import Setting
from django.views.generic.list_detail import object_list

def index(request):
    if request.is_ajax():
        print "index"
    else:
        
        from django.views.generic import list_detail
        all_list = BlogPost.objects.all()
        list_db = DBContainer.objects.all()
        if len(list_db) == 0:
            search_for_db(request.session.session_key)
        elif list_db[0].session_id != request.session.session_key:
            search_for_db(request.session.session_key)
        return object_list(request, all_list, template_name='dlnaupnpmanage/blogpost_list.html')
        #temp = 'dlnaupnpmanage/blogpost_list.html'
        
        #return render_to_response(temp, all_list, context_instance = RequestContext(request))
    
def update(request):
    print "update"
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(serializers.serialize("json", BlogPost.objects.all()))
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
