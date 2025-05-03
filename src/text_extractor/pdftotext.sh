#! /bin/bash

# This script converts all .pdf files in the specified directory to .txt files using pdftotext.
# It assumes that pdftotext is installed and available in the PATH.

mkdir -p output

files=$(echo ../../dataset/*.pdf)

for file in $files; do
  pdf_file=$(basename $file)
  txt_file=${pdf_file%.pdf}.txt

  pdftotext $file output/$txt_file
done
