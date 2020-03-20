#!/bin/bash

# Everything is installed now

# Define the data and output directories
DATA="/data"
OUT="/output"

mkdir -p ${OUT}/arxiv/tars

TAR_OUT=${OUT}/arxiv/tars

# Is there a paper_ids.txt?
if [ ! -r ${DATA}/arxiv/paper_ids.txt ]
then
  arxiv_fetcher
fi

# Download everything
arxiv_autoload --paper-ids=${DATA}/arxiv/paper_ids.txt --download-dir=${TAR_OUT}/

# Extract all files
cd ${TAR_OUT}
for entry in "${TAR_OUT}/*"
do
  FILENAME=$(basename -- "$entry")
  FILENAME="${FILENAME%.*}"

  mkdir -p ${FILENAME}
  tar xf ${entry} --directory=${FILENAME}
done

# Now start the simplification process, loop through all entries in $TAR_OUT
for entry in "${TAR_OUT}/*"
do
  # If entry is a directory
  if [ -d ${entry} ]
  then
    cd ${entry}
    
    # Find the tex file
    TEX_LIST=$(find -name "*.tex")
    #TEX_FILES=$(echo ${TEX_LIST} | cut -d$'\n' -f1-)
    # And create a simplified version
    texsimplifier ${TEX_LIST} > simplified.tex

    # Compile PDF
    ocr_tex2pdf --input-file=./simplified.tex --output-file=./simplified.pdf

    # Extract PDF to PPM
    ocr_pdf2img --input-file=./simplified.pdf --output-dir=./

    # Generate noise
    ocr_img2noise --input-directory=./ --noise-types gauss erode sp

    # And generate the text
    ocr_img2txt --input-directory=./
    cd ..
  fi
done