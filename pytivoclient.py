import re
import datetime
import xml.etree.ElementTree
import requests


XML_NAMESPACES = {
    't': 'http://www.tivo.com/developer/calypso-protocol-1.6/'
    }


def xml_iterfind(element, match):
    return element.iterfind(match, namespaces=XML_NAMESPACES)

def xml_findall(element, match):
    return element.findall(match, namespaces=XML_NAMESPACES)

def xml_bare_tag(element):
    return re.sub(r'^{[^}]+}', '', element.tag)

def underscore_to_camel(identifier):
    return re.sub(r'(?:^|_)([a-z])', lambda m: m.group(1).upper(), identifier)

def camel_to_underscore(identifier):
    ret = (identifier[0].lower()
           + re.sub(r'[A-Z]', lambda m: '_' + m.group().lower(), identifier[1:]))
    ret = re.sub(r'(^|_)ti_vo(?=$|_)', r'\1tivo', ret)
    return ret

def parse_item(item_element):
    data = {}
    for element in xml_iterfind(item_element, 't:Details/'):
        attr = camel_to_underscore(xml_bare_tag(element))
        data[attr] = element.text
    item = TYPE_MAP[data['content_type']]()
    for attr, value in data.items():
        setattr(item, attr, value)
    link_elements = xml_iterfind(item_element, 't:Links/')
    item.links = dict(map(parse_link, link_elements))
    return item

def parse_link(link_element):
    link = Link()
    link_name = camel_to_underscore(xml_bare_tag(link_element))
    for element in link_element:
        attr = camel_to_underscore(xml_bare_tag(element))
        setattr(link, attr, element.text)
    return link_name, link


class Client(object):

    def __init__(self, ip, mak):
        self.ip = ip
        self.mak = mak

    def get(self, url, **kwargs):
        auth = requests.auth.HTTPDigestAuth('tivo', self.mak)                                      
        r = requests.get(url, auth=auth, verify=False, **kwargs)
        return r

    def list(self, folder=None):
        if folder:
            if not isinstance(folder, Folder):
                raise ValueError("can only list folders")
            url = folder.links['content'].url
        else:
            url = ('https://%s/TiVoConnect?Command=QueryContainer&'
                   'Container=%%2FNowPlaying') % self.ip
        r = self.get(url)
        xml_root = xml.etree.ElementTree.fromstring(r.content)
        item_elements = xml_iterfind(xml_root, 't:Item')
        return map(parse_item, item_elements)

    def download(self, video, filename=None):
        if not isinstance(video, Video):
            raise ValueError("can only download videos")
        url = video.links['content'].url
        filename = '%s.tivo' % video.display_title
        r = self.get(url, stream=True)
        with open(filename, 'wb') as file:
            for chunk in r.iter_content(8192):
                file.write(chunk)



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

    def __repr__(self):
        return "<Folder: %s (%s) ID=%s>" % (self.title, self.total_items,
                                            self.unique_id)


class Video(Item):

    def __init__(self):
        super(Video, self).__init__()
        self.description = None
        self.episode_title = None
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

    @property
    def display_title(self):
        try:
            return '%s - %s' % (self.title, self.episode_title)
        except AttributeError:
            return self.title

    @property
    def display_capture_date(self):
        date_seconds = int(self.capture_date, 16)
        return datetime.datetime.fromtimestamp(date_seconds).isoformat()

    @property
    def display_duration(self):
        hours, minutes = divmod(int(round(float(self.duration)/60000)), 60)
        return '%d:%02d' % (hours, minutes)

    def __repr__(self):
        return ("<Video: %s (%s / %s)>" %
                (self.display_title, self.display_capture_date,
                 self.display_duration)
                )


class Link(object):

    def __init__(self):
        self.url = None
        self.content_type = None
        self.accepts_params = None

    def __repr__(self):
        return '"%s"' % self.url


TYPE_MAP = {
    'video/x-tivo-raw-tts': Video,
    'x-tivo-container/folder': Folder,
    #'x-tivo-container/tivo-videos': 
    }
