#!/bin/bash

#This bash script is used to download PDF files corresponding to DOIs listed in a text file. 
#It checks if the necessary argument is passed and verifies the existence of the input file. 
#Then, it iterates through each DOI, downloads the corresponding page from Scihub, extracts the URL of the PDF file using a Python script, and downloads the PDF file. 
#If any error occurs during this process, it logs the DOI into an error file. 
#Finally, it prints a message indicating the completion of the download process.


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

# Create the "dl_publis" folder if it does not exist
mkdir -p dl_publis

# Initialize the publication number
publication_num=1

# Iterate over each DOI in the file
while IFS= read -r doi; do

  # Download the corresponding page
  wget -O temppage "https://sci-hub.3800808.com/$doi"

  # Execute the Python script to extract the URL
  url=$(python3 script_python/extract_publi.py temppage)

  # Check if the URL was extracted
  if [ -z "$url" ] || [[ "$url" == "err"* ]]; then
    echo "**ERROR:** Unable to extract the URL for DOI $doi."
    echo "$doi" >> error_extract_scihub.txt
    continue
  fi

  # Modify the DOI
  modified_doi="${doi//\//%2F}"

  # Download the PDF file
  filename="${modified_doi}.pdf"
  wget -O "data_pdf/$filename" "$url"

  # Increment the publication number
  ((publication_num++))

  # Clean up temporary files
  rm temppage

done < "$file"

echo "**PDF file download completed. Files are stored in the data_pdf folder.**"

