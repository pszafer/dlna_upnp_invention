'''
Created on 18-08-2011

@copyright: 2011,
@author: Pawel Szafer
@license:  Licensed under the BSD license
 http://www.opensource.org/licenses/bsd-license.php
 
@contact: pszafer@gmail.com
@version: 0.8.5

'''

from webob import Request, Response
from webob import exc
from simplejson import loads, dumps
import traceback
import sys
import json

class JsonRpcApp(object):
    """
    Serve the given object via json-rpc (http://json-rpc.org/)
    """

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self.process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def process(self, req):
        if not req.method == 'POST':
            raise exc.HTTPMethodNotAllowed(
                "Only POST allowed",
                allowed='POST')
        try:
            json = loads(req.body)
        except ValueError, e:
            raise ValueError('Bad JSON: %s' % e)
        try:
            method = json['method']
            params = json['params']
            id = json['id']
        except KeyError, e:
            raise ValueError(
                "JSON body missing parameter: %s" % e)
        if method.startswith('_'):
            raise exc.HTTPForbidden(
                "Bad method name %s: must not start with _" % method)
        if not isinstance(params, list):
            raise ValueError(
                "Bad params %r: must be a list" % params)
        try:
            method = getattr(self.obj, method)
        except AttributeError:
            raise ValueError(
                "No such method %s" % method)
        try:
            result = method(*params)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))
        if ('settings') in method.__name__:
            result = result.getjson()
        elif ('content') in method.__name__:
            contentlist = []
            for x in result:
                contentlist.append(x.getjson())
            result = contentlist
        
        body=dumps(dict(result=result,error=None,id=id))        
        return Response(content_type='application/json',body=body)