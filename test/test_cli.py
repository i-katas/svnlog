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
        log, err = proc.communicate()

        assert not err
        assert "fix typos" in str(log, encoding='utf8')


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
    stdout = StringIO()

    main('--remote-path', 'src', stdin=path_of('log.xml'), write=stdout.write)

    assert ": main/java/Main.java" in stdout.getvalue()
    assert ": test/java/TestMain.java" in stdout.getvalue()


def test_print_included_paths_only():
    stdout = StringIO()

    main('--include', 'src/main', '--include', 'package-info.java', stdin=path_of('log.xml'), write=stdout.write)

    assert "/Main.java" in stdout.getvalue()
    assert "/package-info.java" in stdout.getvalue()
    assert "/TestMain.java" not in stdout.getvalue()


def test_skip_exclude_paths():
    stdout = StringIO()

    main('--exclude', 'src/main', '--exclude', 'package-info.java', stdin=path_of('log.xml'), write=stdout.write)

    assert "/Main.java" not in stdout.getvalue()
    assert "/package-info.java" not in stdout.getvalue()
    assert "/TestMain.java" in stdout.getvalue()


def test_use_composed_filters_to_filter_paths():
    stdout = StringIO()

    main('--exclude', 'src/test', '--include', 'package-info.java', stdin=path_of('log.xml'), write=stdout.write)

    assert "/Main.java" in stdout.getvalue()
    assert "/package-info.java" in stdout.getvalue()
    assert "/TestMain.java" not in stdout.getvalue()


def test_filter_path_by_action():
    stdout = StringIO()

    main('--action', 'AM', stdin=path_of('log.xml'), write=stdout.write)

    assert "/Main.java" in stdout.getvalue()
    assert "/TestMain.java" in stdout.getvalue()
    assert "/package-info.java" not in stdout.getvalue()


def test_raise_syntax_error_when_format_a_bad_formatted_log():
    bad_log = '<badlog>'

    with pytest.raises(SyntaxError):
        main(stdin=StringIO(bad_log))


def path_of(file):
    return path.join(path.dirname(__file__), file)
