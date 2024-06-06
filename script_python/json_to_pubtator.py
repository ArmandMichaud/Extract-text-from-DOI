#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 09:59:44 2024

@author: amichaud
"""

import os
import json
import argparse
import logging

# Configure logging to provide information on the progress
logging.basicConfig(level=logging.INFO, format='%(message)s')

def process_json_file(input_file, output_dir):
    """
    Process a single JSON file and create a PubTator file.
    
    Args:
        input_file (str): Path to the input JSON file.
        output_dir (str): Directory where the output PubTator file will be stored.
    """
    filename = os.path.basename(input_file)
    file_base_name = os.path.splitext(filename)[0]
    output_file = os.path.join(output_dir, f"{file_base_name}.pubtator")


    # Read the JSON data from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    # Check if 'abstract' key exists and add its content to the lines
    if 'abstract' in data:
        lines.append(f"{file_base_name}|a|{data['abstract']}")
    # Check if 'body' key exists and add its content to the lines
    if 'body' in data:
        lines.append(f"{file_base_name}|b|{data['body']}")

    # If there are any lines to write, create the PubTator file
    if lines:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(lines))
    else:
        logging.info(f"No 'abstract' or 'body' found in file: {input_file}")

def process_input(input_path, output_dir):
    """
    Process the input path which can be a file or a directory of JSON files.
    
    Args:
        input_path (str): Path to the input JSON file or directory containing JSON files.
        output_dir (str): Directory where the output PubTator files will be stored.
    """
    if os.path.isfile(input_path):
        # Process a single JSON file
        process_json_file(input_path, output_dir)
    elif os.path.isdir(input_path):
        logging.info(f"Processing directory: {input_path}")
        # Process all JSON files in the directory
        for filename in os.listdir(input_path):
            if filename.endswith('.json'):
                process_json_file(os.path.join(input_path, filename), output_dir)
        logging.info(f"Finished processing directory: {input_path}")
    else:
        logging.error(f"Error: {input_path} is neither a file nor a directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process JSON files to PubTator format.')
    parser.add_argument('input_path', type=str, help='Input file or directory containing JSON files.')
    parser.add_argument('output_dir', type=str, help='Output directory to store PubTator files.')

    args = parser.parse_args()

    # Create the output directory if it does not exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        logging.info(f"Created output directory: {args.output_dir}")

    # Process the input path
    process_input(args.input_path, args.output_dir)

