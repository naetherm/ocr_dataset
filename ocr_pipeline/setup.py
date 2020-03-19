# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os
import os.path

from setuptools import setup, find_packages

from ocr_pipeline.version import version_str

def read(*paths):
  """Build a file path from *paths* and return the contents."""
  with open(os.path.join(*paths), 'r') as f:
    return f.read()

setup(
  name="ocr_pipeline",
  version=version_str,

  # metadata for upload to pypi
  author="Markus Näther",
  author_email="naetherm@informatik.uni-freiburg.de",
  description="Simple OCR pipeline for compiling TeX to PDF, extracting those to images, noising them, and recognizing the text.",
  long_description=read("README.md"),
  license="",
  keywords="latex ocr parse noise",
  url="https://github.com/naetherm/ocr_pipeline",
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Markup :: LaTeX',
  ],
  
  # files
  packages=find_packages(),
  entry_points= {
    "console_scripts": [
      "ocr_tex2pdf=ocr_pipeline.ocr_tex2pdf.__main__:main",
      "ocr_pdf2img=ocr_pipeline.ocr_pdf2img.__main__:main",
      "ocr_img2noise=ocr_pipeline.ocr_img2noise.__main__:main",
      "ocr_img2txt=ocr_pipeline.ocr_img2txt.__main__:main"
    ]

  },
  install_requires=[],
  package_data={}
)