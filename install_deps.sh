#!/bin/bash

ROOT_DIR=$(pwd)

# Install everything required for the parsing process
apt update && apt install -y python3 python3-dev python3-pip tesseract-ocr tesseract-ocr-eng texlive-full

# Install required python modules
pip3 install --user pdf2image numpy opencv-python pytesseract Pillow pdflatex

# Build and install arxiv_downloader
cd arxiv_downloader && python3 -m setup install --user && cd ..

# Build and install ocr_pipeline
cd ocr_pipeline && python3 -m setup install --user && cd ..

# Build and install texparser
cd texparser && python3 -m setup install --user

# Go back
cd ${ROOT_DIR}