from typing import Union, Generator, IO
from io import StringIO
from xml.etree import ElementTree as ET
import time
import datetime

_ISO_FORMAT_ = '%Y-%m-%dT%H:%M:%S.%fZ'
_DEFAULT_DATE_FORMAT_ = '%Y年%-m月%-d日 %H:%M:%S'
_DEFAULT_TEMPLATE_ = \
"""\
Revision: {revision}
Author: {author}
Date: {date}
Message:
{message}
--------------------------------
{crlf.join(str(path) for path in paths)}
"""
 

def format(file:Union[str, IO], template:str=_DEFAULT_TEMPLATE_, date_format:str=_DEFAULT_DATE_FORMAT_) -> str:
    if not file:
        return ""

    if isinstance(file, str):
        file = StringIO(file)

    log = ET.parse(file).getroot()

    return "\n\n".join(str(LogEntry(entry, template, date_format)) for entry in log)


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

    @staticmethod
    def parse(xml: str):
        return Path(ET.parse(StringIO(xml)).getroot())

    @property
    def path(self) -> str:
        return self._element.text

    @property
    def action(self) -> str:
        return self._actions.get(self._element.get('action'))

    def __str__(self) -> str:
        return f"{self.action}: {self.path}"


class LogEntry:
    def __init__(self, element: ET.Element, template:str=None, date_format=_DEFAULT_DATE_FORMAT_):
        self._element = element
        self._template = template
        self._date_format = date_format

    @staticmethod
    def parse(xml):
        return LogEntry(ET.parse(StringIO(xml)).getroot())

    @property
    def revision(self) -> str:
        return self._element.get('revision')

    @property
    def author(self) -> str:
        return self._element.find('author').text

    @property
    def date(self) -> str:
        date = self._element.find('date').text
        return time.strftime(self._date_format, time.strptime(date, _ISO_FORMAT_))

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
