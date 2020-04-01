# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

from __future__ import print_function, unicode_literals

import os
import sys
import re
import logging
import argparse
import regex as re

logger = logging.getLogger(__name__)


def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog='texmacroexpander', add_help=False)

  parser.add_argument(
    '--input-file', dest='input_file', 
    help="The input file to work on.")
  parser.add_argument(
    '--output-file', dest='output_file',
    help="The output file to save to."
  )

  args = parser.parse_args(argv)

  cont = ""
  with open(args.input_file, 'r', encoding='utf-8') as fin:
    cont = fin.read()

  #print("cont: {}".format(cont))

  cont = re.sub(r'^\n+(?=\n)', '\n', cont)

  #print("cont: {}".format(cont))

  with open(args.output_file, 'w') as fout:
    fout.write(cont)


if __name__ == '__main__':
  main()