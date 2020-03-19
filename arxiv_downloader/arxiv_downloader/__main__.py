# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import argparse

from arxiv_downloader import ArXiv, ArXivPaper


def main(argv=None):

  if argv == None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="arxiv_downloader", add_help=False)

  parser.add_argument(
    "--paper-id",
    dest="paper_id",
    type=str,
    required=True,
    help="The ID of the paper to download"
  )
  parser.add_argument(
    "--download-dir",
    dest="download_dir",
    type=str,
    required=True,
    help="The directory where to download the file."
  )

  args = parser.parse_args()

  ArXiv.download_by_pid(args.paper_id, args.download_dir)

def fetch_main():
  ArXiv.fetch_papers()

def autoload_main(argv=None):

  if argv == None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="arxiv_autoload", add_help=False)
  parser.add_argument(
    "--paper-ids",
    dest="paper_ids",
    type=str,
    required=True,
    help="Path to the file holding all paper ids to download."
  )
  parser.add_argument(
    "--download-dir",
    dest="download_dir",
    type=str,
    required=True,
    help="The directory where to download the file."
  )

  args = parser.parse_args()

  with open(args.paper_ids, 'r') as fin:
    for lin in fin:
      lin = lin.replace('\n', '')
      ArXiv.download_by_pid(lin, args.download_dir)

if __name__ == '__main__':
  main()