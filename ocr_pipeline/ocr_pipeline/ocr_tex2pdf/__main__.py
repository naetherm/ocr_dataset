# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import fileinput
import argparse
import logging

from ocr_pipeline.ocr_tex2pdf import TeX2PDFConverter

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="ocr_tex2pdf", add_help=False)

  group = parser.add_argument_group("TeX2PDF options")

  group.add_argument(
    '--input-file', type=str,
    dest='input_file',
    help="The TeX file to compile via pdflatex."
  )
  group.add_argument(
    '--output-file', type=str,
    dest='output_file',
    help="The filename of the pdf file to save."
  )

  args = parser.parse_args()

  # Create the tex2pdf converter instance, this means that it will also 
  # create the pdf and save it to disk (including the log for debugging purposes)
  tex2pdf = TeX2PDFConverter(
    input_file=args.input_file,
    output_file=args.output_file
  )

if __name__ == '__main__':
  main()