import pytest
import sys
from svnlog.__main__ import main
from io import StringIO
from os import path


class tty:
    def isatty(self):
        return True


def test_format_from_tty_stream_will_show_usage_and_exit_immediately():
    with pytest.raises(SystemExit, match='usage: svnlog'):
        main(stdin=tty())


def test_format_log_from_pipe_stream():
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
    with pytest.raises(SystemExit, match='^No such file or directory: .*?/absent$'):
        main(stdin=path_of('absent'))


def test_run_as_script():
    with svnlog(path_of('log.xml')) as proc:
        log = str(proc.communicate()[0], encoding='utf8')
        assert "Message:\nfix typos" in log


@pytest.mark.skipif(not sys.stdin.isatty(), reason='stdin is non-tty stream')
def test_fails_to_run_as_script_from_tty():
    proc = svnlog('--template', path_of('template.txt'))
    try:
        err = str(proc.communicate(timeout=0.5)[1], encoding='utf8')

        assert 'usage: svnlog' in err
    finally:
        proc.kill()


def svnlog(*args):
    from subprocess import Popen, PIPE

    return Popen([sys.executable, path_of('../svnlog'), *args], stdout=PIPE, stderr=PIPE)


def test_print_paths_relative_to_remote_path():
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


def test_raise_syntax_error_when_format_a_bad_formatted_log():
    bad_log = '<badlog>'

    with pytest.raises(SyntaxError):
        main(stdin=StringIO(bad_log))


def path_of(file):
    return path.join(path.dirname(__file__), file)
