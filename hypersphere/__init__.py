import pymonad as pymonad
import webob

import hypersphere.validate as validate


class Response(pymonad.Monad):
    def __init__(self):
        """
        Raises a NotImplementedError.
        Only crea   te ResolvedResponse or UnresolvedResponse.
        """
        raise NotImplementedError()

    @staticmethod
    def mzero():
        return UnresolvedResponse()


class ResolvedResponse(Response):
    def __init__(self, response):
        self.value = response

    def bind(self, _function):
        return self


class UnresolvedResponse(Response):
    def __init__(self, resource, request):
        self.resource = resource
        self.request = request
        self.value = webob.Response(status=500)

    def bind(self, function):
        response = function(self.resource, self.request)
        if response:
            return ResolvedResponse(response)
        else:
            return self


def blank_200(_resource, _request):
    return webob.Response(status=200)


class Resource(object):
    available = True
    known_methods = {
        'GET', 'HEAD', 'POST', 'PUT', 'DELETE',
        'TRACE', 'CONNECT', 'OPTIONS'
    }
    max_uri_length = 4096

    def respond(self, request):

        return (
            UnresolvedResponse(self, request)
            >> validate.check_available
            >> validate.method_known
            >> validate.uri_length_within_limit
            >> blank_200
        ).getValue()
