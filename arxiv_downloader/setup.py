# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os
import os.path

from setuptools import setup, find_packages

from arxiv_downloader.version import version_str

def read(*paths):
  """Build a file path from *paths* and return the contents."""
  with open(os.path.join(*paths), 'r') as f:
    return f.read()

setup(
  name="arxiv_downloader",
  version=version_str,

  # metadata for upload to pypi
  author="Markus Näther",
  author_email="naetherm@informatik.uni-freiburg.de",
  description="",
  long_description=read("README.md"),
  license="",
  keywords="latex ocr parse noise",
  url="https://github.com/naetherm/arxiv_downloader",
  classifiers=[
    'Development Status :: 5 - Production/Stable',
  ],
  
  # files
  packages=find_packages(),
  entry_points= {
    "console_scripts": [
      "arxiv_downloader=arxiv_downloader.__main__:main",
      "arxiv_fetcher=arxiv_downloader.__main__:fetch_main"
      "arxiv_autoload=arxiv_downloader.__main__:autoload_main"
    ]

  },
  install_requires=[],
  package_data={}
)