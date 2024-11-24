#!/bin/bash

# Check if the user has provided a root directory
if [ -z "$1" ]; then
    echo "Usage: $0 <root-directory>"
    exit 1
fi

# Set the root directory
ROOT_DIR="$1"

# Check if the root directory exists
if [ ! -d "$ROOT_DIR" ]; then
    echo "Error: Root directory '$ROOT_DIR' does not exist."
    exit 1
fi

# Loop through all subdirectories in the root directory
for subdir in "$ROOT_DIR"/*/; do
    # Check if the subdirectory exists (safety check in case no directories are present)
    if [ ! -d "$subdir" ]; then
        continue
    fi

    # Find .pdf files in the subdirectory
    pdf_file=$(find "$subdir" -maxdepth 1 -type f -name "*.pdf")
    
    # If a PDF file exists, move it to the root directory
    if [ -n "$pdf_file" ]; then
        mv "$pdf_file" "$ROOT_DIR"
        echo "Moved: $pdf_file to $ROOT_DIR."
    else
        echo "No .pdf file found in $subdir."
    fi

    # Delete the subdirectory and its contents
    rm -rf "$subdir"
    echo "Deleted directory: $subdir"
done
