from typing import Union, Generator, IO
from io import StringIO
from xml.etree import ElementTree as ET
import time
from datetime import datetime

_ISO_FORMAT_ = '%Y-%m-%dT%H:%M:%S.%fZ'
_DEFAULT_DATE_FORMAT_ = '%Y年%-m月%-d日 %H:%M:%S'
_DEFAULT_TEMPLATE_ = \
f"""\
Revision: {{revision}}
Author: {{author}}
Date: {{date.strftime('{_DEFAULT_DATE_FORMAT_}')}}
Message:
{{message}}
--------------------------------
{{crlf.join(str(path) for path in paths)}}
"""
 

def format(source:Union[str, IO], template:str=_DEFAULT_TEMPLATE_) -> str:
    log = parse(source, template)
    return "\n\n".join(str(entry) for entry in log)


def parse(source, template):
    if not source:
        return ()

    if isinstance(source, str):
        source = StringIO(source)

    return (LogEntry(entry, template) for entry in ET.parse(source).getroot())



class Path:
    """
    svn log uses just a handful of action codes, and they are similar to the ones the svn update command uses:

    A
    The item was added.

    D
    The item was deleted.

    M
    Properties or textual contents on the item were changed.

    R
    The item was replaced by a different one at the same location.
    """
    _actions=dict(A='Added', M='Modified', R='Renamed', D='Deleted')

    def __init__(self, element):
        self._element = element

    @property
    def path(self) -> str:
        return self._element.text

    @property
    def action(self) -> str:
        return self._actions.get(self._element.get('action'))

    def __str__(self) -> str:
        return ': '.join((self.action, self.path))


class LogEntry:
    def __init__(self, element: ET.Element, template:str=None):
        self._element = element
        self._template = template

    @property
    def revision(self) -> str:
        return self._element.get('revision')

    @property
    def author(self) -> str:
        return self._element.find('author').text

    @property
    def date(self) -> datetime:
        date = self._element.find('date').text
        return datetime.strptime(date, _ISO_FORMAT_)

    @property
    def message(self) -> str:
        msg = self._element.find('msg')
        return '' if msg is None else msg.text

    @property
    def paths(self) -> Generator[Path, None, None]:
        return (Path(path) for path in self._element.findall('paths/path'))

    def __str__(self) -> str:
            props = dict(revision=self.revision, author=self.author, date=self.date, message=self.message, paths=self.paths, crlf='\n')
            return eval(f'f"""{self._template}"""', props, props)
