import svnlog
from io import StringIO
from svnlog import LogEntry, Path, _DEFAULT_DATE_FORMAT_

single_entry_log = """
    <log>
    <logentry revision="43657">
    <author>bob</author>
    <date>2020-04-09T01:11:44.487000Z</date>
    <paths>
    <path action="M" prop-mods="false" text-mods="true" kind="file">src/main/java/Main.java</path>
    </paths>
    <msg>fix typos</msg>
    </logentry>
    </log>
"""


def test_return_empty_generator_when_parse_empty_logs():
    assert not next(svnlog.parse(''), None)


def test_format_single_entry_log():
    assert svnlog.format(svnlog.parse(single_entry_log)) == """\
Revision: 43657
Author: bob
Date: 2020年4月9日 01:11:44
Message:
fix typos
--------------------------------
Modified: src/main/java/Main.java
"""


def test_format_single_entry_log_with_multiple_paths():
    xml = """
        <log>
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <paths>
        <path action="M" prop-mods="false" text-mods="true" kind="file">src/main/java/Main.java</path>
        <path action="D" prop-mods="false" text-mods="true" kind="file">src/main/java/package-info.java</path>
        </paths>
        <msg>fix typos</msg>
        </logentry>
        </log>
    """

    log = svnlog.format(svnlog.parse(xml))

    assert 'Modified: src/main/java/Main.java' in log
    assert 'Deleted: src/main/java/package-info.java' in log


def test_format_multiple_log_entries():
    xml = """
        <log>
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <paths>
        <path action="M" prop-mods="false" text-mods="true" kind="file">src/main/java/Main.java</path>
        </paths>
        <msg>fix typos</msg>
        </logentry>
        <logentry revision="43655">
        <author>kitty</author>
        <date>2020-04-09T00:11:44.487000Z</date>
        <paths>
        <path action="D" prop-mods="false" text-mods="true" kind="file">src/main/java/package-info.java</path>
        </paths>
        <msg>remove package-info</msg>
        </logentry>
        </log>
    """

    assert svnlog.format(svnlog.parse(xml)) == """\
Revision: 43657
Author: bob
Date: 2020年4月9日 01:11:44
Message:
fix typos
--------------------------------
Modified: src/main/java/Main.java


Revision: 43655
Author: kitty
Date: 2020年4月9日 00:11:44
Message:
remove package-info
--------------------------------
Deleted: src/main/java/package-info.java
"""


def test_format_from_iostream():
    assert 'Modified: src/main/java/Main.java' in svnlog.format(svnlog.parse(StringIO(single_entry_log)))


def test_format_with_custom_template():
    result = svnlog.format(svnlog.parse(StringIO(single_entry_log)), template="{revision}: {next(paths).path}")

    assert result == "43657: src/main/java/Main.java"


def test_log_entry_message_is_optional():
    entry = LogEntry(parse("""
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        </logentry>
    """))

    assert entry.message == ''


def test_create_log_entry_from_xml_without_paths():
    entry = LogEntry(parse("""
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <msg>fix typos</msg>
        </logentry>
    """))

    assert entry.revision == '43657'
    assert entry.author == 'bob'
    assert entry.date.strftime(_DEFAULT_DATE_FORMAT_) == '2020年4月9日 01:11:44'
    assert entry.message == 'fix typos'
    assert [*entry.paths] == []


def test_create_log_entry_with_modified_paths():
    entry = LogEntry(parse("""
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <paths>
        <path action="M" prop-mods="false" text-mods="true" kind="file">src/main/java/test.java</path>
        </paths>
        <msg>fix typos</msg>
        </logentry>
    """))

    assert [str(path) for path in entry.paths] == ['Modified: src/main/java/test.java']


def test_remove_path_prefix_that_starts_with_remote_path():
    entry = next(svnlog.parse(single_entry_log, remote_path='src/main/java/'))

    assert [str(path) for path in entry.paths] == ['Modified: Main.java']


def test_remove_remote_path_not_ends_with_slash():
    entry = next(svnlog.parse(single_entry_log, remote_path='src/main/java'))

    assert [str(path) for path in entry.paths] == ['Modified: Main.java']


def test_path_actions_translation():
    assert Path(parse('<path action="M"/>')).action == 'Modified'
    assert Path(parse('<path action="A"/>')).action == 'Added'
    assert Path(parse('<path action="R"/>')).action == 'Renamed'
    assert Path(parse('<path action="D"/>')).action == 'Deleted'


def parse(xml):
    from xml.etree import ElementTree as ET

    return ET.parse(StringIO(xml)).getroot()
