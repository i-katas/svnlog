import svnlog
import sys
from typing import Callable, Union, IO, Optional
from argparse import ArgumentParser, _AppendAction

STDIN = str(b'/dev/stdin')


def main(*args, stdin: Union[str, IO] = sys.stdin, write: Callable[[str], None] = print):
    try:
        args = args or sys.argv[1:]
        parser = build_parser(stdin)

        options = parser.parse_args(args)

        entries = svnlog.parse(options.file, options.remote_path)
        template = text_of(options.template, svnlog._DEFAULT_TEMPLATE_)
        write(svnlog.format(entries, template, path_matcher_of(options), options.skip_no_paths))
    except FileNotFoundError as e:
        raise SystemExit(f'{e.strerror}: {e.filename}')


def path_matcher_of(options):
    from svnlog import match
    from svnlog.predicates import both, either, negate
    matcher = None
    if options.include:
        matcher = either(matcher, match(options.include))
    if options.exclude:
        matcher = either(matcher, negate(match(options.exclude)))
    if options.text:
        matcher = both(matcher, lambda path: path.is_textmod)
    matcher = both(matcher, lambda path: path.action[0] in options.action)
    matcher = both(matcher, lambda path: path.kind in options.kind)
    return matcher


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
    parser.add_argument('-a', '--action', nargs='?', type=str, default='ARMD', help='filter logs paths by actions: [A, M, R, D], e.g: --action ARMD')
    parser.add_argument('-k', '--kind', nargs='?', type=str, default='file,dir', help='filter logs paths by kind: file, dir, e.g: --kind file,dir')
    parser.add_argument('-i', '--include', nargs='*', action=extend, help='include paths that matches regular pattern expression')
    parser.add_argument('-x', '--exclude', nargs='*', action=extend, help='exclude paths that matches regular pattern expression')
    parser.add_argument('-s', '--skip-no-paths', action='store_true', help='skip to print the log entry without any paths, default: disabled')
    parser.add_argument('--text', action='store_true', help='skip to print the non-text path')

    return parser


class extend(_AppendAction):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None)
        items = items[:] if items else []
        items.extend(values)
        setattr(namespace, self.dest, items)


def text_of(source: Optional[IO], default: str = None) -> str:
    return ''.join(source.readlines()) if source else default


if __name__ == '__main__':
    main()
