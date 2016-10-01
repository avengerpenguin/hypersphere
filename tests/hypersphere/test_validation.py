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
    r = webob.Request({'PATH_INFO': '/'})
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
    request.environ['REQUEST_METHOD'] = 'MUNGE'
    response = hello_world_resource.respond(request)
    assert response.status_code == 501


def test_allows_nonstandard_request_methods(request):
    class MungingResource(hypersphere.Resource):
        @property
        def known_methods(self):
            """Extends known methods rather than overwriting"""
            return super().known_methods | {'MUNGE',}

    resource = MungingResource()
    request.environ['REQUEST_METHOD'] = 'MUNGE'
    response = resource.respond(request)
    assert response.status_code == 200


def test_stupidly_long_uris_blocked_by_default(hello_world_resource, request):
    request.environ['PATH_INFO'] = '/foo' * 1025
    response = hello_world_resource.respond(request)
    assert response.status_code == 414


def test_can_extend_max_uri_length(request):
    class BigURIResource(hypersphere.Resource):
        max_uri_length = 8192

    resource = BigURIResource()
    request.environ['PATH_INFO'] = '/foo' * 1025
    response = resource.respond(request)
    assert response.status_code == 200
