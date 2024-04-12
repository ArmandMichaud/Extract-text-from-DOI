#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to extract text from PDF files and save it as TEI XML format.

Created on Thu Feb 29 14:34:28 2024

@author: amichaud
"""

import os
import requests

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file using an API.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text if successful, None otherwise.
    """
    url = "http://localhost:8070/api/processFulltextDocument"
    files = {'input': open(pdf_path, 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        return response.text
    else:
        return None

def save_text_to_file(text, output_dir, pdf_filename):
    """
    Save the extracted text to a file in TEI XML format.

    Args:
        text (str): The extracted text.
        output_dir (str): The directory to save the output file.
        pdf_filename (str): The filename of the original PDF file.

    Returns:
        None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_filename = os.path.splitext(pdf_filename)[0] + ".tei.xml"
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(text)
    print(f"Text saved to: {output_path}")





def main():
    # Directory containing PDF files to analyze
    pdf_directory = "./data_pdf"
    # Directory where you want to save the output files
    output_dir = "./data_tei_xml"
    # File to save extraction errors
    error_file = "./grobid_errors.txt"

    print(f"Starting the Grobid analysis of PDFs from : {pdf_directory}")

    # Open the error file in append mode
    with open(error_file, "a") as err_file:
        # Iterate through all files in the directory
        for filename in os.listdir(pdf_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_directory, filename)
                extracted_text = extract_text_from_pdf(pdf_path)
                if extracted_text:
                    save_text_to_file(extracted_text, output_dir, filename)
                else:
                    print(f"Failed to extract text from PDF: {pdf_path}")
                    err_file.write(f"{filename}\n")

    print(f"The extracted tei.xml files were saved as : {output_dir}")
    print(f"Extraction errors are available in the grobid_errors.txt file")
main()

