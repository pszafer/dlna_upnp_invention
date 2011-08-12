# Create your views here.
from dlnaupnpmanagment.dlnaupnpmanage.models import BlogPost
from django.template import loader
from django.template.context import Context, RequestContext
from django.http import HttpResponse
from django.core import serializers
from django.shortcuts import render_to_response


def halo(request):
    if request.is_ajax():
        all_list = BlogPost.objects.all()    
        temp = 'dlnaupnpmanage/index.html'
        #cont = Context({'all_list':all_list})
        response = HttpResponse()
        response['Content-Type'] = "text/javascript"
        #response.write(serializers.serialize("json", all_list))
        return render_to_response(temp, all_list, context_instance = RequestContext(request))
    else:
        temp = loader.get_template('dlnaupnpmanage/index.html')
        all_list = BlogPost.objects.all()
        return HttpResponse(temp.render(all_list))
    
def update(request):
    response = HttpResponse()
    response['Content-Type'] = "text/javascript"
    response.write(serializers.serialize("json", BlogPost.objects.all()))
    return response

def run_server(request):
    import subprocess
    subprocess.call( "../../../../upnp_server/src/")
    subprocess.call("python", "../../../../upnp_server/src/dlnaupnpserver/MediaServer.py")




