# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os

try:
  from PIL import Image
except ImportError:
  import Image
import pytesseract

class Img2TxtConverter(object):

  def __init__(
    self,
    input_directory
  ):
    super(Img2TxtConverter, self).__init__()

    self.input_directory = input_directory

    # The combined text
    self.combined_text = ""

    # Fetch all images
    files_ = self._fetch_all_images()

    for _, img_fn in enumerate(files_):
      with open(img_fn + ".txt", 'w') as fout:
        text_ = pytesseract.image_to_string(img_fn)
        fout.write(text_)
        self.combined_text += "\n" + text_

    dir_name_ = os.path.dirname(os.path.abspath(files_[0]))

    with open(os.path.join(dir_name_, "output.txt"), 'w') as fout:
      fout.write(self.combined_text)

  
  def _fetch_all_images(self):
    files = []
    for file in os.listdir(self.input_directory):
      if file.endswith(".jpg"):
        files.append(os.path.join(self.input_directory, file))
    files.sort()
    return files