import svnlog
import sys
from typing import Callable, Union, IO, Optional
from argparse import ArgumentParser

STDIN = str(b'/dev/stdin')


def main(*args, stdin: Union[str, IO] = sys.stdin, write: Callable[[str], None] = print):
    try:
        args = args or sys.argv[1:]
        parser = build_parser(stdin)

        options = parser.parse_args(args)

        from svnlog import match
        from svnlog.predicates import either, negate
        matcher = None
        if options.include:
            matcher = either(matcher, match(options.include))
        if options.exclude:
            matcher = either(matcher, negate(match(options.exclude)))

        write(svnlog.format(svnlog.parse(options.file, options.remote_path), text_of(options.template, svnlog._DEFAULT_TEMPLATE_), match_path=matcher))
    except FileNotFoundError as e:
        raise SystemExit(f'{e.strerror}: {e.filename}')


def build_parser(stdin: Union[str, IO]):
    parser = ArgumentParser(prog=svnlog.__name__)

    def redirect(path):
        if path is STDIN:
            if isinstance(stdin, str):
                return open(stdin)
            if stdin.isatty():
                raise SystemExit(parser.format_help())
            return stdin
        return open(path)

    parser.add_argument('file', type=redirect, nargs='?', default=STDIN, help='the svn xml format log file')
    parser.add_argument('-t', '--template', type=open, help='use custom log template file')
    parser.add_argument('-p', '--remote-path', type=str, help='remove the remote path from the path of log entry')
    parser.add_argument('-i', '--include', nargs='*', action='extend', help='include paths that matches regular pattern expression')
    parser.add_argument('-x', '--exclude', nargs='*', action='extend', help='exclude paths that matches regular pattern expression')

    return parser


def text_of(source: Optional[IO], default: str = None) -> str:
    return ''.join(source.readlines()) if source else default


if __name__ == '__main__':
    main()
