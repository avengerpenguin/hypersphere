import pytest
import webob
from rdflib import Literal
from rdflib import URIRef

import hypersphere


@pytest.fixture
def hello_world_resource():
    class HelloWorldResource(hypersphere.Resource):
        pass

    resource = HelloWorldResource()
    return resource


@pytest.fixture()
def request():
    r = webob.Request({'PATH_INFO': '/'})
    return r


def test_rejects_unknown_media_type(hello_world_resource, request):
    request.headers['Accept'] = 'image/png'
    response = hello_world_resource.respond(request)
    assert response.status_code == 406


def test_rejects_unknown_languages(hello_world_resource, request):
    request.headers['Accept-Language'] = 'en-gb-norfolk'
    response = hello_world_resource.respond(request)
    assert response.status_code == 406


def test_rejects_unknown_charsets(hello_world_resource, request):
    request.headers['Accept-Charset'] = 'utf-9'
    response = hello_world_resource.respond(request)
    assert response.status_code == 406


def test_rejects_unknown_encoding(hello_world_resource, request):
    request.headers['Accept-Encoding'] = 'hzip'
    response = hello_world_resource.respond(request)
    assert response.status_code == 406
