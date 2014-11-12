#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''imeji

Usage:
  imeji create <what>
  imeji retrieve <what>
  imeji update <what>
  imeji delete <what>
  imeji -h | --help
  imeji --version

Options:
  -h --help     Show this screen.
  --version     Show version.
'''

from __future__ import unicode_literals, print_function
from docopt import docopt

from pyimeji.config import Config
from pyimeji.api import Imeji


__version__ = "0.1.0"
__author__ = "Robert Forkel"
__license__ = "MIT"


def main():
    '''Main entry point for the imeji CLI.'''
    cfg = Config()
    args = docopt(__doc__, version=__version__)
    api = Imeji(cfg)


if __name__ == '__main__':
    main()
