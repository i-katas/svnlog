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

    main(STDIN, stdin=xml, write=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_format_log_from_file():
    stdout = StringIO()

    main(STDIN, stdin=path_of('log.xml'), write=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_use_custom_template_to_format_log():
    stdout = StringIO()

    main(STDIN, '-t', path_of('template.txt'), stdin=path_of('log.xml'), write=stdout.write)

    assert "43657: fix typos\n" == stdout.getvalue()


def test_suppress_traceback_if_file_not_exists():
    with pytest.raises(SystemExit, match='No such file'):
        main(STDIN, stdin=path_of('absent'))


def test_run_as_script():
    import sys
    from subprocess import check_output

    log = str(check_output([sys.executable, path_of('../src/cli.py'), path_of('log.xml')]), encoding='utf8')

    assert "Message:\nfix typos" in log


def test_print_paths_relative_to_current_working_dir():
    xml = """
        <log>
        <logentry revision="43655">
        <author>kitty</author>
        <date>2020-04-09T00:11:44.487000Z</date>
        <paths>
        <path action="M" prop-mods="false" text-mods="true" kind="file">/remote/trunk/src/main/java/Main.java</path>
        </paths>
        <msg>remove package-info</msg>
        </logentry>
        </log>
    """

    stdout = StringIO()

    main(STDIN, '--remote-path', '/remote/trunk', stdin=StringIO(xml), write=stdout.write)

    assert "Modified: src/main/java/Main.java" in stdout.getvalue()


def path_of(file):
    return path.join(path.dirname(__file__), file)
