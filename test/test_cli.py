import pytest
from svnlog.cli import main
from io import StringIO
from os import path


class tty:
    def isatty(self):
        return True


def test_show_usage_if_stream_is_a_tty_stream():
    with pytest.raises(SystemExit, match='usage:'):
        main(stdin=tty())


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

    main(stdin=xml, write=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_format_log_from_file():
    stdout = StringIO()

    main(stdin=path_of('log.xml'), write=stdout.write)

    assert "fix typos" in stdout.getvalue()


def test_use_custom_template_to_format_log():
    stdout = StringIO()

    main('-t', path_of('template.txt'), stdin=path_of('log.xml'), write=stdout.write)

    assert "43657: fix typos\n" == stdout.getvalue()


def test_suppress_traceback_if_file_not_exists():
    with pytest.raises(SystemExit, match='No such file'):
        main(stdin=path_of('absent'))


def test_run_as_script():
    log = run(path_of('../src/svnlog/cli.py'), path_of('log.xml')).communicate()[0]

    assert "Message:\nfix typos" in log


def test_fails_to_run_as_script_with_tty_stdin():
    proc = run(path_of('../src/svnlog/cli.py'), '--template', path_of('template.txt'))
    try:
        err = proc.communicate(timeout=0.5)[1]

        assert 'usage: svnlog' in err
    finally:
        proc.kill()


def run(*args):
    import sys
    from subprocess import Popen, PIPE

    return Popen([sys.executable, *args], stdout=PIPE, stderr=PIPE, text=True)


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

    main('--remote-path', '/remote/trunk', stdin=StringIO(xml), write=stdout.write)

    assert "Modified: src/main/java/Main.java" in stdout.getvalue()


def test_raise_syntax_error_when_parse_a_bad_log_file():
    bad_log = '<badlog>'

    with pytest.raises(SyntaxError):
        main(stdin=StringIO(bad_log))


def path_of(file):
    return path.join(path.dirname(__file__), file)
