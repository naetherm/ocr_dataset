# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import fileinput
import argparse
import logging

from ocr_pipeline.ocr_pdf2img import PDF2ImgConverter

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="ocr_pdf2img", add_help=False)

  group = parser.add_argument_group("PDF2Img options")

  group.add_argument(
    '--input-file', type=str, 
    dest="input_file",
    help="Defines the input pdf file to convert"
  )

  group.add_argument(
    '--output-dir', type=str, 
    dest="output_dir",
    help="The output directory where to save all images"
  )

  args = parser.parse_args()

  pdf2img = PDF2ImgConverter(
    input_file=args.input_file,
    output_directory=args.output_dir
  )

if __name__ == '__main__':
  main()