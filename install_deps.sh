#!/bin/bash

ROOT_DIR=$(pwd)

# Install everything required for the parsing process
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y tzdata
ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
dpkg-reconfigure --frontend noninteractive tzdata

apt install -y python3 python3-dev python3-pip tesseract-ocr tesseract-ocr-eng texlive-full poppler-utils xorg

# Install required python modules
pip3 install --user pdf2image numpy opencv-python pytesseract Pillow pdflatex requests beautifulsoup4

# Build and install arxiv_downloader
cd arxiv_downloader && python3 -m setup install && cd ..

# Build and install ocr_pipeline
cd ocr_pipeline && python3 -m setup install && cd ..

# Build and install texparser
cd texparser && python3 -m setup install

# Go back
cd ${ROOT_DIR}
