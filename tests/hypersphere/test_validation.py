import base64
import re

import pytest
import webob

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


def test_hello_world(hello_world_resource, request):
    response = hello_world_resource.respond(request)
    assert response.status_code == 200


def test_allow_disabling_service(request):
    class DisabledResource(hypersphere.Resource):
        @property
        def available(self):
            """This could be dynamic in a real use case."""
            return False

    resource = DisabledResource()
    request = webob.Request({})
    response = resource.respond(request)
    assert response.status_code == 503


def test_responds_to_unknown_method(hello_world_resource, request):
    request.environ["REQUEST_METHOD"] = "MUNGE"
    response = hello_world_resource.respond(request)
    assert response.status_code == 501


def test_allows_nonstandard_request_methods(request):
    class MungingResource(hypersphere.Resource):
        allowed_methods = ["GET", "MUNGE"]

        @property
        def known_methods(self):
            """Extends known methods rather than overwriting"""
            return super().known_methods | {
                "MUNGE",
            }

    resource = MungingResource()
    request.environ["REQUEST_METHOD"] = "MUNGE"
    response = resource.respond(request)
    assert response.status_code == 200


def test_stupidly_long_uris_blocked_by_default(hello_world_resource, request):
    request.environ["PATH_INFO"] = "/foo" * 1025
    response = hello_world_resource.respond(request)
    assert response.status_code == 414


def test_can_extend_max_uri_length(request):
    class BigURIResource(hypersphere.Resource):
        max_uri_length = 8192

    resource = BigURIResource()
    request.environ["PATH_INFO"] = "/foo" * 1025
    response = resource.respond(request)
    assert response.status_code == 200


def test_allows_get_by_default(hello_world_resource, request):
    request.environ["REQUEST_METHOD"] = "GET"
    response = hello_world_resource.respond(request)
    assert response.status_code == 200


def test_allows_head_by_default(hello_world_resource, request):
    request.environ["REQUEST_METHOD"] = "HEAD"
    response = hello_world_resource.respond(request)
    assert response.status_code == 200


def test_disallows_post_by_default(hello_world_resource, request):
    request.environ["REQUEST_METHOD"] = "POST"
    response = hello_world_resource.respond(request)
    assert response.status_code == 405


def test_disallows_delete_by_default(hello_world_resource, request):
    request.environ["REQUEST_METHOD"] = "DELETE"
    response = hello_world_resource.respond(request)
    assert response.status_code == 405


def test_allows_request_validation(request):
    class PeopleResource(hypersphere.Resource):
        def validate_request(self, request):
            """Expects URLs such as /people/123"""
            return re.match(r"^/people/\d+$", request.path)

    resource = PeopleResource()

    # valid URI
    request.environ["PATH_INFO"] = "/people/123"
    response = resource.respond(request)
    assert response.status_code == 200

    # invalid URI
    request.environ["PATH_INFO"] = "/people/abc"
    response = resource.respond(request)
    assert response.status_code == 400


def test_allows_authentication(request):
    class SecretResource(hypersphere.Resource):
        def authenticate(self, request):
            if "Authorization" in request.headers:
                userpass = request.headers["Authorization"].split()[-1]
                userpass = base64.b64decode(userpass.encode("utf-8")).decode("utf-8")
                username, password = userpass.split(":")
                print(password)
                if password == "hunter2":
                    request.headers["REMOTE_USER"] = username
                    return True
                else:
                    return False
            else:
                return False

    resource = SecretResource()
    response = resource.respond(request)
    assert response.status_code == 401

    request.headers["Authorization"] = "Basic " + base64.b64encode(
        b"testuser:hunter1"
    ).decode("utf-8")
    response = resource.respond(request)
    assert response.status_code == 401

    request.headers["Authorization"] = "Basic " + base64.b64encode(
        b"testuser:hunter2"
    ).decode("utf-8")
    response = resource.respond(request)
    assert response.status_code == 200

    assert request.headers["REMOTE_USER"] == "testuser"


def test_allows_authorisation(request):
    class SecretResource(hypersphere.Resource):
        def authenticate(self, request):
            if "Authorization" in request.headers:
                userpass = request.headers["Authorization"].split()[-1]
                userpass = base64.b64decode(userpass.encode("utf-8")).decode("utf-8")
                username, password = userpass.split(":")
                print(password)
                if password == "hunter2":
                    request.headers["REMOTE_USER"] = username
                    return True
                else:
                    return False
            else:
                return False

        def authorise(self, request):
            if (
                "REMOTE_USER" in request.headers
                and request.headers["REMOTE_USER"] == "alice"
            ):
                return True
            else:
                return False

    resource = SecretResource()
    request.headers["Authorization"] = "Basic " + base64.b64encode(
        b"bob:hunter2"
    ).decode("utf-8")
    response = resource.respond(request)
    assert response.status_code == 403

    request.headers["Authorization"] = "Basic " + base64.b64encode(
        b"alice:hunter2"
    ).decode("utf-8")
    response = resource.respond(request)
    assert response.status_code == 200


def test_responds_415_to_bizarre_media_types(hello_world_resource, request):
    request.headers["Content-Type"] = "image/png"
    request.body = b"foobar"
    response = hello_world_resource.respond(request)
    assert response.status_code == 415
