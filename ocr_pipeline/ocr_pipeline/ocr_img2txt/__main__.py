# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import fileinput
import argparse
import logging

from ocr_pipeline.ocr_img2txt import Img2TxtConverter

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="ocr_img2txt", add_help=False)

  group = parser.add_argument_group("Img2Txt options")

  group.add_argument(
    "--input-directory",
    dest="input_directory",

  )

  args = parser.parse_args()

  i2t = Img2TxtConverter(
    input_directory=args.input_directory
  )


if __name__ == '__main__':
  main()