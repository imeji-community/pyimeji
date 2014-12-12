#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''imeji

Usage:
  imeji create <what>
  imeji [options] list <what>
  imeji [options] retrieve <what> <id>
  imeji update <what>
  imeji delete <what>
  imeji -h | --help
  imeji --version

Options:
  -h --help        Show this screen.
  --version        Show version.
  --service=<URL>  URL of the imeji service
'''

from __future__ import unicode_literals, print_function
from docopt import docopt

from pyimeji.config import Config
from pyimeji.api import Imeji


__version__ = "0.1.0"
__author__ = "Robert Forkel"
__license__ = "MIT"


def main(argv=None):  # pragma: no cover
    '''Main entry point for the imeji CLI.'''
    cfg = Config()
    args = docopt(__doc__, version=__version__, argv=argv)
    api = Imeji(cfg, service_url=args['--service'])
    if args['list']:
        return getattr(api, args['<what>'])()
    elif args['retrieve']:
        return getattr(api, args['<what>'])(id=args['<id>'])


if __name__ == '__main__':  # pragma: no cover
    print(main())
