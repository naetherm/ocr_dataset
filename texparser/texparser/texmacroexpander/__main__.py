# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os
import sys
import argparse
import json
import logging

from texparser.texmacroexpander import TexMacroExpander
from texparser.version import version_str

logger = logging.getLogger(__name__)

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog='texmacroexpander', add_help=False)

  parser.add_argument(
    'input-file', dest='input_file', 
    help="The input file to work on.")
  parser.add_argument(
    'output-file', dest='output_file',
    help="The output file to save to."
  )

  args = parser.parse_args(argv)

  tme = TexMacroExpander(
    input_file=args.input_file,
    output_file=args.output_file
  )