import re
import xml.etree.ElementTree
import requests


_NAMESPACES = {
    't': 'http://www.tivo.com/developer/calypso-protocol-1.6/'
    }


def xml_iterfind(element, match):
    return element.iterfind(match, namespaces=_NAMESPACES)

def xml_findall(element, match):
    return element.findall(match, namespaces=_NAMESPACES)

def xml_bare_tag(element):
    return re.sub(r'^{[^}]+}', '', element.tag)

def underscore_to_camel(identifier):
    return re.sub(r'(?:^|_)([a-z])', lambda m: m.group(1).upper(), identifier)

def camel_to_underscore(identifier):
    return (identifier[0].lower()
            + re.sub(r'[A-Z]', lambda m: '_' + m.group().lower(), identifier[1:]))

def parse_item(item_element):
    item = Item()
    for element in xml_iterfind(item_element, 't:Details/'):
        attr = camel_to_underscore(xml_bare_tag(element))
        setattr(item, attr, element.text)
    return item


class Client(object):

    def __init__(self, ip, mak):
        self.ip = ip
        self.mak = mak

    def get(self, path, secure=True, params={}):
        scheme = 'https' if secure else 'http'
        url = '%s://%s/%s' % (scheme, self.ip, path)
        auth = requests.auth.HTTPDigestAuth('tivo', self.mak)
        r = requests.get(url, params=params, auth=auth, verify=False)
        return r

    def list(self, container_path):
        params = {
            'Command': 'QueryContainer',
            'Container': container_path,
            }
        r = self.get('TiVoConnect', params=params)
        xml_root = xml.etree.ElementTree.fromstring(r.content)
        item_elements = xml_iterfind(xml_root, 't:Item')
        return map(parse_item, item_elements)


class Item(object):

    def __init__(self):
        self.content_type = None
        self.source_format = None
        self.title = None
        self.links = None


class Folder(Item):

    def __init__(self):
        super(Folder, self).__init__()
        self.last_change_date = None
        self.total_items = None
        self.last_capture_date = None
        self.unique_id = None


class Video(Item):

    def __init__(self):
        super(Video, self).__init__()
        self.source_size = None
        self.duration = None
        self.capture_date = None
        self.source_channel = None
        self.source_station = None
        self.in_progress = None
        self.high_definition = None
        self.program_id = None
        self.series_id = None
        self.byte_offset = None


class Link(object):

    def __init__(self):
        self.url = None
        self.content_type = None
        self.icon = None
