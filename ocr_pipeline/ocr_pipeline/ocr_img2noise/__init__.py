# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import os

import cv2
try:
  from PIL import Image
except ImportError:
  import Image

import numpy as np
import numpy.random as rnd

class Img2NoiseConverter(object):

  def __init__(
    self,
    input_directory,
    noise_types,
    num_trials,
    gauss_mean,
    gauss_variance,
    sp_ratio,
    sp_amount,
    erose_kernel_size,
    erose_iterations,
    rotate_angle
  ):
    super(Img2NoiseConverter, self).__init__()

    # Fetch parameters
    self.input_directory = input_directory
    self.noise_types = noise_types
    self.num_trials = num_trials
    self.num_noise_types = len(self.noise_types)
    self.gauss_mean = gauss_mean
    self.gauss_variance = gauss_variance
    self.sp_ratio = sp_ratio
    self.sp_amount = sp_amount
    self.erose_kernel_size = erose_kernel_size
    self.erose_iterations = erose_iterations
    self.rotate_angle = rotate_angle

    # Get all images located within the file
    img_files_ = self._fetch_all_images()

    for _, img_fn in enumerate(img_files_):
      # Read the image file
      noised_ = cv2.imread(img_fn)

      for _ in range(self.num_trials):
        # Choose an noiser
        rnd_noiser_ = self._choose_noise_type()

        if rnd_noiser_ == 'gauss':
          noised_ = self._gauss(noised_)
        if rnd_noiser_ == 'sp':
          noised_ = self._salt_n_pepper(noised_)
        if rnd_noiser_ == 'poisson':
          noised_ = self._poisson(noised_)
        if rnd_noiser_ == 'speckle':
          noised_ = self._speckle(noised_)
        if rnd_noiser_ == 'erode':
          noised_ = self._erode(noised_)
        if rnd_noiser_ == 'rotate':
          noised_ = self._rotate(noised_)

      # Done, write image to file
      cv2.imwrite(img_fn)



  def _fetch_all_images(self):
    files = []
    for file in os.listdir(self.input_directory):
      if file.endswith(".ppm"):
        files.append(os.path.join(self.input_directory, file))
    return files

  def _choose_noise_type(self):
    choice = rnd.choice(self.noise_types, 1)

    return choice[0]

  def _gauss(self, img):
    row, col, ch = img.shape
    sigma = self.gauss_variance**0.5
    gauss = rnd.normal(self.gauss_mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noised = img + gauss
    return noised

  def _salt_n_pepper(self, img):
    row, col, ch = img.shape
    noised = np.copy(img)
    # Salt mode
    num_salt = np.ceil(self.sp_amount * img.size * self.sp_ratio)
    coords = [rnd.randint(0, i - 1, int(num_salt)) for i in image.shape]
    noised[coords] = 255
    # Pepper mode
    num_pepper = np.ceil(self.sp_amount * img.size * (1. - self.sp_ratio))
    coords = [rnd.randint(0, i - 1, int(num_pepper)) for i in image.shape]
    noised[coords] = 0

    return noised

  def _poisson(self, img):
    vals = len(np.unique(img))
    vals = 2 ** np.ceil(np.log2(vals))

    noised = rnd.poisson(img * vals) / float(vals)

    return noised

  def _speckle(self, img):
    row, col, ch = img.shape
    gauss = rnd.randn(row, col, ch)
    gauss = gauss.reshape(row, col, ch)

    noised = img + img * gauss

    return noised

  def _erode(self, img):
    kernel = np.ones((self.erose_kernel_size, self.erose_kernel_size), np.uint8)

    noised = cv2.erode(img, kernel, iterations=self.erose_iterations)

    return noised

  def _rotate(self, img):
    noised = img.rotate(self.rotate_angle)

    return noised