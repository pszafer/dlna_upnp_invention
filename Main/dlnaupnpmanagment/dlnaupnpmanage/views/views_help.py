# Create your views here.

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseServerError, HttpRequest
from django.template.response import TemplateResponse
from django.core import serializers
from django.shortcuts import render_to_response
from twisted.internet import reactor
import subprocess
from django.views.generic.list_detail import object_list
from django.template import RequestContext


#DONE
def help(request):
    response = TemplateResponse(request, 'dlnaupnpmanage/help.html', {})
    return response