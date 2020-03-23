# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os

import requests
import urllib.request
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ArXivPaperIDFetcher(object):

  def __init__(self):
    super(ArXivPaperIDFetcher, self).__init__()

class ArXivPaper(object):

  def __init__(
    self,
    pid,
    download_dir
  ):
    super(ArXivPaper, self).__init__()

    self.pid = pid
    self.download_dir = download_dir

  def download(self):
    url = "https://export.arxiv.org/e-print/" + self.pid

    try:
      urllib.request.urlretrieve(url, os.path.join(self.download_dir, "{}.tar.gz".format(self.pid)))
    except:
      logger.warning(
        "Unable to download the file '{}' - skipping.".format(
          os.path.join(self.download_dir, "{}.tar.gz".format(self.pid))))

class ArXiv(object):

  def __init__(self):
    super(ArXiv, self).__init__()

  @staticmethod
  def download(paper):
    paper.download()

  @staticmethod
  def download_by_pid(pid, download_dir):
    paper = ArXivPaper(pid, download_dir)
    ArXiv.download(paper)

  @staticmethod
  def fetch_papers():
    # TODO(naetherm): Implement this
    # This is super simple ...
    small_y_range = ["08", "09", "10", "11", "12", "13", "14"]
    large_y_range = ["15", "16", "17", "18", "19", "20"]
    month_range = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

    with open ("./paper_ids.txt", 'w') as fout:
      for y in small_y_range:
        for m in month_range:
          for p in ["%04d" % i for i in range(1, 9999)]:
            try:
              urllib.request.urlopen("https://export.arxiv.org/abs/{}{}.{}".format(y, m, p))
              fout.write("{}{}.{}\n".format(y, m, p))
            except:
              break
      for y in large_y_range:
        for m in month_range:
          for p in ["%05d" % i for i in range(1, 99999)]:
            try:
              urllib.request.urlopen("https://export.arxiv.org/abs/{}{}.{}".format(y, m, p))
              fout.write("{}{}.{}\n".format(y, m, p))
            except:
              break
