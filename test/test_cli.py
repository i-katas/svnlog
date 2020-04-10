import sys
import pytest
from cli import main
from io import StringIO
from os import path

def test_raise_exception_if_stream_is_not_tty():
    try:
        main(stdin=sys.stdin)
        pytest.fail()
    except SystemExit:
        pass


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

    main(stdin=xml, printer=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_format_log_from_non_atty_stream():
    stdout = StringIO()
    args=[None, path.join(path.dirname(__file__), 'log.xml')]

    main(args, printer=stdout.write)

    assert "fix typos" in stdout.getvalue()
