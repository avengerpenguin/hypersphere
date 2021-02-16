import cgi

import pymonad as pymonad
import webob

from . import accept, parse, validate


class Response(pymonad.Monad):
    def __init__(self):
        """
        Raises a NotImplementedError.
        Only create ResolvedResponse or UnresolvedResponse.
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


class Resource:

    available = True
    known_methods = {
        "GET",
        "HEAD",
        "POST",
        "PUT",
        "DELETE",
        "TRACE",
        "CONNECT",
        "OPTIONS",
    }
    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    max_uri_length = 4096
    max_request_body_length = 10 * 1014 * 1024
    acceptable_media_types = ["text/turtle"]
    acceptable_languages = {
        "en",
    }
    acceptable_charsets = {
        "utf-8",
    }
    acceptable_encodings = {
        "identity",
    }

    def validate_request(self, request):
        return True

    def authenticate(self, request):
        return True

    def authorise(self, request):
        return True

    def request_body_parser(self):
        return parse.choose

    def process_request_entity(self, request):
        if len(request.body) > 0:
            if "Content-Type" not in request.headers:
                return webob.Response(status=415)

            if len(request.body) > self.max_request_body_length:
                return webob.Response(status=413)

            mime = cgi.parse_header(request.headers["Content-Type"])
            try:
                resolver = self.request_body_parser()
                entity = resolver(mime[0], **mime[1]).parse(request)
                request.entity = entity
            except KeyError:
                return webob.Response(status=415)

    def respond(self, request):
        return (
            UnresolvedResponse(self, request)
            >> validate.check_available
            >> validate.method_known
            >> validate.uri_length_within_limit
            >> validate.method_allowed
            >> validate.request_valid
            >> validate.authenticate
            >> validate.authorise
            # TODO: Validate Content-* headers?
            >> Resource.process_request_entity
            >> accept.media_type
            >> accept.languages
            >> accept.charsets
            >> accept.encodings
            >> blank_200
        ).getValue()
