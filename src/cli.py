import svnlog 
import sys
from typing import Callable, TextIO

__help__ =\
f"""\
Usage:
    {svnlog.__name__} logfile
"""

def main(argv=sys.argv, stdin:TextIO=sys.stdin, printer:Callable[[str], None]=print):
    if len(argv) > 1:
        stdin = open(argv[1])
    elif stdin.isatty():
        raise SystemExit(__help__)
    printer(svnlog.format(stdin))

