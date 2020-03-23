#!/bin/bash

# Everything is installed now

# Define the data and output directories
#DATA="/data"
#OUT="/output"
DATA="/home/naetherm/Uni/datasets/segmentation"
OUT="/home/naetherm/Uni/datasets/segmentation"

mkdir -p ${OUT}/arxiv/tars
mkdir -p ${OUT}/arxiv/out

SIM_OUT=${OUT}/arxiv/out
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

  #mkdir -p ${FILENAME}
  #tar xzf ${entry} --directory=${FILENAME}

  #if [ $? -eq 0 ]
  #then 
  #  # None
  #  
  #else
  #  rm -rf ${FILENAME}
  #fi
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
        pdflatex -halt-on-error -interaction=nonstopmode ${TEX_LIST[0]}
      } && {

        mkdir -p ${SIM_OUT}/${FILENAME}
        OUT_DIR=${SIM_OUT}/${FILENAME}
        timeout 10 texsimplifier ${TEX_LIST[0]} > ${OUT_DIR}/simplified.tex

        # Extract PDF to PPM
        tex2text ${OUT_DIR}/simplified.tex > ${OUT_DIR}/simplified.txt
      } && {

        # Compile PDF
        ocr_tex2pdf --input-file=${OUT_DIR}/simplified.tex --output-file=${OUT_DIR}/simplified.pdf
      } && {

        # Extract PDF to PPM
        ocr_pdf2img --input-file=${OUT_DIR}/simplified.pdf --output-dir=${OUT_DIR}/
      } && {

        # Generate noise
        ocr_img2noise --input-directory=${OUT_DIR}/
      } && {

        # And generate the text
        ocr_img2txt --input-directory=${OUT_DIR}/
        ((GCount++))
        echo "Generated the output for ${GCount} now"

        cp ${TEX_LIST[0]}.pdf ${OUT_DIR}/original.pdf
      }
      cd ..
    fi
  fi
done
