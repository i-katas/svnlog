from io import StringIO
from xml.etree import ElementTree as ET
import time
import datetime

_ISO_FORMAT_ = '%Y-%m-%dT%H:%M:%S.%fZ'

def format(xml:str) -> str:
    if not xml:
        return ""

    log = ET.parse(StringIO(xml)).getroot()


    return "\n\n".join(str(LogEntry(entry)) for entry in log)

class LogEntry:
    def __init__(self, element: ET.Element, date_format='%Y年%-m月%-d日 %H:%M:%S'):
        self._element = element
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
        return self._element.find('msg').text

    @property
    def paths(self):
        return (Path(path) for path in self._element.findall('paths/path'))

    def __str__(self):
        paths = '\n'.join(str(path) for path in self.paths)
        return f"""\
Revision: {self.revision}
Author: {self.author}
Date: {self.date}
Message:
{self.message}
----
{paths}
"""



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
    def path(self):
        return self._element.text

    @property
    def action(self):
        return self._actions.get(self._element.get('action'))

    def __str__(self):
        return f"{self.action}: {self.path}"



