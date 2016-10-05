import json
import rdflib
from rdflib.parser import Parser


def choose(mime, **kwargs):
    return parser_map[mime](mime, **kwargs)


class BaseParser(object):
    def __init__(self, mime, charset='utf-8', **kwargs):
        self.mime = mime
        self.charset = charset
        self.options = kwargs


class JsonParser(BaseParser):
    def parse(self, request):
        return json.loads(request.body.decode(self.charset))


class RDFParser(BaseParser):
    def parse(self, request):
        g = rdflib.Graph()
        g.parse(data=request.body, format=self.mime)
        return g


parser_map = {'application/json': JsonParser}


for plugin in rdflib.plugin.plugins(kind=Parser):
    if '/' in plugin.name:
        parser_map[plugin.name] = RDFParser
