import mimeparse
import webob


def media_type(resource, request):
    if (
        "Accept" in request.headers
        and request.headers["Accept"] not in resource.acceptable_media_types
    ):
        return webob.Response(status=406)
    else:
        acceptable = (
            "Accept" in request.headers and request.headers["Accept"] or "*/*"
        )
        mimeparse.best_match(resource.acceptable_media_types, acceptable)


def languages(resource, request):
    if (
        "Accept-Language" in request.headers
        and request.headers["Accept-Language"]
        not in resource.acceptable_languages
    ):
        return webob.Response(status=406)


def charsets(resource, request):
    if (
        "Accept-Charset" in request.headers
        and request.headers["Accept-Charset"]
        not in resource.acceptable_charsets
    ):
        return webob.Response(status=406)


def encodings(resource, request):
    if (
        "Accept-Encoding" in request.headers
        and request.headers["Accept-Encoding"]
        not in resource.acceptable_encodings
    ):
        return webob.Response(status=406)
