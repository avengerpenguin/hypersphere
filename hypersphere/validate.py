import webob


def check_available(resource, _request):
    if not resource.available:
        return webob.Response(status=503)


def method_known(resource, request):
    if request.method not in resource.known_methods:
        return webob.Response(status=501)


def uri_length_within_limit(resource, request):
    if len(request.path) > resource.max_uri_length:
        return webob.Response(status=414)