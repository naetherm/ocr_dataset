# -*- coding: utf-8 -*-
# Copyright 2019-2020, University of Freiburg.
# Chair of Algorithms and Data Structures.
# Markus Näther <naetherm@informatik.uni-freiburg.de>

from pdflatex import PDFLaTeX

class TeX2PDFConverter(object):

  def __init__(
    self,
    input_file,
    output_file
  ):
    super(TeX2PDFConverter, self).__init__()

    self.input_file = input_file
    self.output_file = output_file

    print("Writing to output file: {}".format(self.output_file))

    # Create the pdf file
    pdfl = PDFLaTeX.from_texfile(self.input_file)
    pdf, log, _ = pdfl.create_pdf(keep_pdf_file=True)

    # Save the log file
    #with open(self.output_file + ".log", "w") as fout:
    #  fout.write(log)
    # Save the pdf file to disk
    with open(self.output_file, 'wb') as fout:
      fout.write(pdf)