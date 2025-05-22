#!/bin/bash

# This bash script is used to download PDF files corresponding to DOIs listed in a text file.
# It checks if the necessary argument is passed and verifies the existence of the input file.
# Then, it iterates through each DOI, downloads the corresponding page from Scihub, extracts the URL of the PDF file using a Python script, and downloads the PDF file.
# If any error occurs during this process, it logs the DOI into an error file.
# Finally, it checks for 0-byte PDF files, deletes them, and logs the corresponding DOIs.

mkdir -p data_pdf
mkdir -p logs

# Check if an argument is passed
if [ $# -ne 1 ]; then
  echo "Usage: $0 doi_file.txt"
  exit 1
fi

# Read the DOI file passed as argument
file=$1

# Check if the file exists
if [ ! -f "$file" ]; then
  echo "The file $file does not exist."
  exit 1
fi

# Initialize the publication number
publication_num=1

# Iterate over each DOI in the file
while IFS= read -r doi; do

  # Download the corresponding page
  wget -O temppage --header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" "https://sci-hub.ru/$doi"

  # Execute the Python script to extract the URL
  url=$(python3 script_python/extract_publi.py temppage)

  # Check if the URL was extracted
  if [ -z "$url" ] || [[ "$url" == "err"* ]]; then
    echo "**ERROR:** Unable to extract the URL for DOI $doi."
    echo "$doi" >> ./logs/errors_extract_scihub.txt
    continue
  fi

  # Modify the DOI
  modified_doi=$(echo "$doi" | sed -e 's/</%3C/g' -e 's/>/%3E/g' -e 's/:/%3A/g' -e 's/;/%3B/g' -e 's/\//%2F/g')

  # Download the PDF file
  filename="${modified_doi}.pdf"
  wget -O "data_pdf/$filename" "$url"

  # Increment the publication number
  ((publication_num++))

  # Clean up temporary files
  rm temppage

done < "$file"

# Check for 0-byte files and log DOIs for deletion
for pdf_file in data_pdf/*.pdf; do
  if [ ! -s "$pdf_file" ]; then
    # Convert the filename back to the DOI
    base_name=$(basename "$pdf_file" .pdf)
    original_doi=$(echo "$base_name" | sed -e 's/%3C/</g' -e 's/%3E/>/g' -e 's/%3A/:/g' -e 's/%3B/;/g' -e 's/%2F/\//g')

    # Log the DOI
    echo "$original_doi" >> ./logs/errors_extract_scihub.txt

    # Delete the empty file
    rm "$pdf_file"
  fi

done

echo "**PDF file download completed. Files are stored in the data_pdf folder.**"
if [ -f temppage ] ; then
    rm temppage
fi
