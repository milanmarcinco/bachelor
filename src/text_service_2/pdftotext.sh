#! /bin/bash

mkdir -p output

files=$(echo ../../dataset/*.pdf)

for file in $files; do
  pdf_file=$(basename $file)
  txt_file=${pdf_file%.pdf}.txt

  pdftotext $file output/$txt_file
done
