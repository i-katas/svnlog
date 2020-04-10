import sys
import pytest
from cli import main, STDIN
from io import StringIO
from os import path

class tty:
    def isatty(self): 
        return True

def test_show_usage_if_stream_is_a_tty_stream():
    with pytest.raises(SystemExit, match='usage:'):
        main(STDIN, stdin=tty())


def test_format_log_from_non_atty_stream():
    stdout = StringIO()
    xml = StringIO("""
        <log>
        <logentry revision="43657">
        <author>bob</author>
        <date>2020-04-09T01:11:44.487000Z</date>
        <msg>fix typos</msg>
        </logentry>
        </log>
    """)

    main(STDIN, stdin=xml, printer=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_format_log_from_file():
    stdout = StringIO()

    main(STDIN, stdin=path_of('log.xml'), printer=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_use_custom_template_to_format_log():
    stdout = StringIO()

    main(STDIN, '-t', path_of('template.txt'), stdin=path_of('log.xml'), printer=stdout.write)

    assert "43657: fix typos\n" == stdout.getvalue()


def test_suppress_traceback_if_file_not_exists():
    with pytest.raises(SystemExit, match='No such file'):
        main(STDIN, stdin=path_of('absent'))


def path_of(file):
    return path.join(path.dirname(__file__), file)


