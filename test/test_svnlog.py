import svnlog
from svnlog import LogEntry, Path

def test_format_empty_logs():
    assert svnlog.format('') == ''

def test_format_single_entry_log():
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
        </log>
    """

    assert svnlog.format(xml) == """\
Revision: 43657
Author: bob
Date: 2020年4月9日 01:11:44
Message:
fix typos
----
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

    assert svnlog.format(xml) == """\
Revision: 43657
Author: bob
Date: 2020年4月9日 01:11:44
Message:
fix typos
----
Modified: src/main/java/Main.java
Deleted: src/main/java/package-info.java
"""


def test_create_log_entry_from_xml_without_paths():
    entry = LogEntry.parse("""
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <msg>fix typos</msg>
        </logentry>
    """)

    assert entry.revision == '43657'
    assert entry.author == 'bob'
    assert entry.date == '2020年4月9日 01:11:44'
    assert entry.message == 'fix typos'
    assert [*entry.paths] == []


def test_create_log_entry_with_modified_paths():
    entry = LogEntry.parse("""
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <paths>
        <path action="M" prop-mods="false" text-mods="true" kind="file">src/main/java/test.java</path>
        </paths>
        <msg>fix typos</msg>
        </logentry>
    """)

    assert entry.revision == '43657'
    assert entry.author == 'bob'
    assert entry.date == '2020年4月9日 01:11:44'
    assert entry.message == 'fix typos'
    assert [str(path) for path in entry.paths] == ['Modified: src/main/java/test.java']


def test_path_actions():
   assert Path.parse('<path action="M"/>').action == 'Modified'
   assert Path.parse('<path action="A"/>').action == 'Added'
   assert Path.parse('<path action="R"/>').action == 'Renamed'
   assert Path.parse('<path action="D"/>').action == 'Deleted'
