from typing import Union, Generator, IO, List, cast, Iterator
from io import StringIO
from xml.etree import ElementTree as ET
from datetime import datetime

PATH_SEPERATOR = '/'
_ISO_FORMAT_ = '%Y-%m-%dT%H:%M:%S.%fZ'
_DEFAULT_DATE_FORMAT_ = '%Y年%-m月%-d日 %H:%M:%S'
_DEFAULT_TEMPLATE_ = f"""\
Revision: {{revision}}
Author: {{author}}
Date: {{date.strftime('{_DEFAULT_DATE_FORMAT_}')}}
Message:
{{message}}
--------------------------------
{{crlf.join(str(path) for path in paths)}}
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
    _actions = dict(A='Added', M='Modified', R='Renamed', D='Deleted')

    def __init__(self, element, remote_path=None):
        self._element = element
        self._remote_path = remote_path

    @property
    def path(self) -> str:
        path = self._element.text
        return path[len(self._remote_path):] if self._remote_path and path.startswith(self._remote_path) else path

    @property
    def action(self) -> str:
        return self._actions.get(self._element.get('action'))

    def __str__(self) -> str:
        return ': '.join((self.action, self.path))


class LogEntry:

    def __init__(self, element: ET.Element, remote_path: str = None):
        self._element = element
        self._remote_path = remote_path

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
        return (Path(path, self._remote_path) for path in self._element.findall('paths/path'))


def format(entries: List[LogEntry], template: str = _DEFAULT_TEMPLATE_) -> str:
    def __format__(entry: LogEntry) -> str:
        props = dict(revision=entry.revision, author=entry.author, date=entry.date, message=entry.message, paths=entry.paths, crlf='\n')
        return eval(f'f"""{template}"""', props, props)

    return "\n\n".join(__format__(cast(LogEntry, entry)) for entry in entries)


def parse(source: Union[str, IO], remote_path: str = None) -> Iterator[LogEntry]:
    if not source:
        return iter(())

    if isinstance(source, str):
        source = StringIO(source)

    if remote_path and not remote_path.endswith(PATH_SEPERATOR):
        remote_path = remote_path + PATH_SEPERATOR

    return (LogEntry(entry, remote_path) for entry in ET.parse(source).getroot())
