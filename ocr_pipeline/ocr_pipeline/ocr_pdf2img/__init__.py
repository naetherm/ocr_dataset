# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os
import sys

from pdf2image import convert_from_path
from pdf2image.generators import counter_generator
from pdf2image.exceptions import (
  PDFInfoNotInstalledError,
  PDFPageCountError,
  PDFSyntaxError
)
import cv2
import numpy as np

class PDF2ImgConverter(object):

  def __init__(
    self,
    input_file,
    output_directory
  ):
    super(PDF2ImgConverter, self).__init__()

    self.input_file = input_file
    self.output_directory = output_directory

    images_from_path = convert_from_path(
      self.input_file, 
      output_folder=self.output_directory,
      output_file=counter_generator(),
      first_page=2,
      fmt="jpg"
    )

    #for idx, img in enumerate(images_from_path):
    #  print("idx: {}".format(idx))
    #  cv2.imwrite(os.path.join(self.output_directory, str(idx) + ".ppm"), np.array(img))