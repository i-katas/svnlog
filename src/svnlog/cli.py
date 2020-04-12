import svnlog
import sys
from typing import Callable, Union, IO, Optional
from argparse import ArgumentParser

STDIN = str(b'/dev/stdin')


def main(*args, stdin: Union[str, IO] = sys.stdin, write: Callable[[str], None] = print):
    try:
        args = args or sys.argv[1:]
        parser = build_parser(redirect(stdin))
        if not args and not isinstance(stdin, str) and stdin.isatty():
            raise SystemExit(parser.format_help())

        options = parser.parse_args(args)

        write(svnlog.format(svnlog.parse(options.file, options.remote_path), text_of(options.template, svnlog._DEFAULT_TEMPLATE_)))
    except FileNotFoundError as e:
        raise SystemExit(f'{e.strerror}: {e.filename}')


def redirect(stdin):
    def wrap(path):
        if path is STDIN:
            if isinstance(stdin, str):
                return open(stdin)
            else:
                return stdin
        return open(path)
    return wrap


def build_parser(source):
    parser = ArgumentParser()
    parser.add_argument('file', type=source, nargs='?', default=STDIN, help='the svn xml format log file')
    parser.add_argument('-t', '--template', type=open, help='use custom log template file')
    parser.add_argument('-p', '--remote-path', type=str, help='remove the remote path from the path of log entry')
    return parser


def text_of(source: Optional[IO], default: str = None) -> str:
    return ''.join(source.readlines()) if source else default


if __name__ == '__main__':
    main()
