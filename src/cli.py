import svnlog
import sys
from typing import Callable, Union, IO, Optional
from argparse import ArgumentParser

STDIN = str(b'/dev/stdin')


def main(*args, stdin: Union[str, IO] = sys.stdin, write: Callable[[str], None] = print):
    try:
        parser = build_parser(stdin)

        options = parser.parse_args(args or sys.argv[1:])

        write(svnlog.format(svnlog.parse(options.file, remote_path=options.remote_path), template=load_template(options.template)))
    except FileNotFoundError as e:
        raise SystemExit(f'{e.strerror}: {e.filename}')
    except IOError:
        raise SystemExit(parser.format_help())


def build_parser(stdin):
    def vfile(path):
        if path is STDIN:
            if isinstance(stdin, str):
                return open(stdin)
            elif stdin.isatty():
                raise IOError("Unsupported tty")
            else:
                return stdin
        return open(path)

    parser = ArgumentParser()
    parser.add_argument('file', type=vfile, nargs='?', default=STDIN, help='the svn xml format log file')
    parser.add_argument('-t', '--template', type=open, help='svn log template file')
    parser.add_argument('-p', '--remote-path', type=str, help='remote path relative to current working directory')
    return parser


def load_template(tpl: Optional[IO]) -> str:
    return ''.join(tpl.readlines()) if tpl else svnlog._DEFAULT_TEMPLATE_


if __name__ == '__main__':
    main()
