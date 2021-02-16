import pytest
import webob
from rdflib import Literal, URIRef

import hypersphere


@pytest.fixture
def hello_world_resource():
    class HelloWorldResource(hypersphere.Resource):
        pass

    resource = HelloWorldResource()
    return resource


@pytest.fixture()
def request():
    r = webob.Request({"PATH_INFO": "/"})
    return r


def test_parses_json_utf8(hello_world_resource, request):
    request.headers["Content-Type"] = "application/json; charset=utf-8"
    request.body = b'{"price": "\xc2\xa3300"}'
    hello_world_resource.respond(request)
    assert request.entity == {"price": "£300"}


def test_parses_json_utf8_by_default(hello_world_resource, request):
    request.headers["Content-Type"] = "application/json"
    request.body = b'{"price": "\xc2\xa3300"}'
    hello_world_resource.respond(request)
    assert request.entity == {"price": "£300"}


def test_parses_json_windows_1252(hello_world_resource, request):
    request.headers["Content-Type"] = "application/json; charset=windows-1252"
    request.body = b'{"price": "\xa3300"}'
    hello_world_resource.respond(request)
    assert request.entity == {"price": "£300"}


def test_parses_turtle(hello_world_resource, request):
    print(hypersphere.parse.parser_map)
    request.headers["Content-Type"] = "text/turtle"
    request.body = b"""
    <http://example.com/person/1> <http://schema.org/name> "Brian Blessed" .
    """
    hello_world_resource.respond(request)
    assert len(request.entity) == 1
    assert (
        URIRef("http://example.com/person/1"),
        URIRef("http://schema.org/name"),
        Literal("Brian Blessed"),
    ) in request.entity
