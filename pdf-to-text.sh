# !/bin/bash

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 input_directory output_directory"
  exit 1
fi

input_dir="$1"
output_dir="$2"

if [[ ! -d "$input_dir" ]]; then
  echo "Error: Input directory $input_dir does not exist."
  exit 1
fi

mkdir -p "$output_dir"

for pdf_file in "$input_dir"/*.pdf; do
  if [[ -f "$pdf_file" ]]; then
    txt_file="$output_dir/$(basename "${pdf_file%.pdf}.txt")"
    pdftotext "$pdf_file" "$txt_file"
    echo "Converted $pdf_file to $txt_file"
  fi
done
