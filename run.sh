#!/bin/bash

# Everything is installed now

# Define the data and output directories
#DATA="/data"
#OUT="/output"
DATA="/home/naetherm/Uni/datasets/segmentation"
OUT="/home/naetherm/Uni/datasets/segmentation"

mkdir -p ${OUT}/arxiv/tars
mkdir -p ${OUT}/arxiv/noise

SIM_OUT=${OUT}/arxiv/noise
TAR_OUT=${OUT}/arxiv/tars

# If there is already a paper_ids.txt we don't fetch the list of all papers
if [ ! -r ${DATA}/arxiv/paper_ids.txt ]
then
  arxiv_fetcher
fi

echo "Downloading the tex sources ..."
# Download everything
#arxiv_autoload --paper-ids=${DATA}/arxiv/paper_ids.txt --download-dir=${TAR_OUT}/

echo "Extracting everything ..."
# Extract all files
cd ${TAR_OUT}
for entry in $(find ${TAR_OUT} -name "*tar.gz" -mindepth 1 -maxdepth 1 -type f)
do
  echo "Processing ${entry}"
  FILENAME=$(basename -- "$entry")
  FILENAME="${FILENAME%.*}"

  if [ ! -d ${FILENAME} ]
  then
    mkdir -p ${FILENAME}
    tar xzf ${entry} --directory=${FILENAME}
  fi
done

# Now start the simplification process, loop through all entries in $TAR_OUT
GCount=0
for entry in $(find ${TAR_OUT} -mindepth 1 -maxdepth 1 -type d)
do
  # If entry is a directory
  if [ -d ${entry} ]
  then
    cd ${entry}
    echo "The entry var is : ${entry}"
    FILENAME=$(basename -- "$entry")
    FILENAME="${FILENAME%.*}"
    
    # Find the tex file
    i=0
    while read line
    do
      array[ $i ]="$line"
      ((i++))
    done < <(find -name "*.tex")
    TEX_LIST=$array #$(find -name "*.tex")

    echo "LENGTH: ${#TEX_LIST[@]} -> ${TEX_LIST}"

    # TODO(naetherm): Find *.tex file that contains documentclass

    if [[ ${i} == 1 ]]
    then
      echo "For directory '${entry}' will compile the file '${TEX_LIST[0]}'"
      #TEX_FILES=$(echo ${TEX_LIST} | cut -d$'\n' -f1-)
      # And create a simplified version
      {
        {
        mkdir -p ${SIM_OUT}/${FILENAME}
        OUT_DIR=${SIM_OUT}/${FILENAME}

        iconv -t UTF-8 ${TEX_LIST[0]} > ${OUT_DIR}/original.tex

        pdflatex -halt-on-error -interaction=nonstopmode -output-directory=${OUT_DIR}  ${TEX_LIST[0]}

        #cp ${TEX_LIST[0]} ${OUT_DIR}/original.tex
      } && {
        timeout 10 texsimplifier --letter-spacing 56 ${OUT_DIR}/original.tex > ${OUT_DIR}/simplified.tex

        # Extract PDF to PPM
        tex2text ${OUT_DIR}/simplified.tex > ${OUT_DIR}/original_asd.txt
        textpostwork --input-file=${OUT_DIR}/original_asd.txt --output-file=${OUT_DIR}/original.txt
      } && {

        # Compile PDF
        ocr_tex2pdf --input-file=${OUT_DIR}/simplified.tex --output-file=${OUT_DIR}/simplified.pdf
      } && {

        # Extract PDF to PPM
        ocr_pdf2img --input-file=${OUT_DIR}/simplified.pdf --output-dir=${OUT_DIR}/
      } && {

        # Generate noise
        ocr_img2noise --input-directory=${OUT_DIR}/ --noise-types gauss erode sp rotate
      } && {

        # And generate the text
        ocr_img2txt --input-directory=${OUT_DIR}/
        ((GCount++))
      }
      } || {
        rm -rf ${OUT_DIR}
      }
      cd ..
    fi
  fi
done

echo "Generated the output for ${GCount} now"