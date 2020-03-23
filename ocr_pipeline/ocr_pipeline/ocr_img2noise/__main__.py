# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

import sys
import fileinput
import argparse
import logging

from ocr_pipeline.ocr_img2noise import Img2NoiseConverter

def main(argv=None):

  if argv is None:
    argv = sys.argv[1:]

  parser = argparse.ArgumentParser(prog="ocr_img2noise", add_help=False)

  group = parser.add_argument_group("Img2Noise options")

  group.add_argument(
    "--input-directory",
    type=str,
    dest="input_directory",
    help="The input directory containing all image files."
  )

  group.add_argument(
    "--noise-types",
    action='store',
    dest='noise_types',
    choices=['gauss', 'sp', 'poisson', 'speckle', 'erode', 'rotate'],
    nargs='+',
    help="The different supported nosie types. During the executing the types for the current document will be choosen randomly."
  )

  group.add_argument(
    "--num_trials",
    dest='num_trials',
    type=int,
    default=1,
    help='The number of noise generation, default: 1.'
  )

  group.add_argument(
    "--gauss-mean",
    dest="gauss_mean",
    type=int,
    default=80,
    help="Mean for gauss noiser"
  )
  group.add_argument(
    "--gauss-variance",
    dest="gauss_variance",
    type=int,
    default=4000,
    help="Variance for gauss noiser"
  )

  group.add_argument(
    "--sp-ratio",
    dest="sp_ratio",
    type=float,
    default=0.5,
    help="The ration between salt and pepper"
  )
  group.add_argument(
    "--sp-amount",
    dest="sp_amount",
    type=float,
    default=0.04,
    help="The amount of salt and pepper to add."
  )

  group.add_argument(
    "--erose-kernel-size",
    dest="erose_kernel_size",
    type=int,
    default=1,
    help="The kernel size for the erose filter"
  )
  group.add_argument(
    "--erose-iterations",
    dest="erose_iterations",
    type=int,
    default=1,
    help="The number of iterations to performace for erose profile"
  )

  group.add_argument(
    "--rotate-angle",
    dest="rotate_angle",
    type=int,
    default=0,
    help="The amount of degree to rotate an image."
  )

  args = parser.parse_args()

  img2n = Img2NoiseConverter(
    input_directory=args.input_directory,
    noise_types=args.noise_types,
    num_trials=args.num_trials,
    gauss_mean=args.gauss_mean,
    gauss_variance=args.gauss_variance,
    sp_ratio=args.sp_ratio,
    sp_amount=args.sp_amount,
    erose_kernel_size=args.erose_kernel_size,
    erose_iterations=args.erose_iterations,
    rotate_angle=args.rotate_angle
  )

if __name__ == '__main__':
  main()