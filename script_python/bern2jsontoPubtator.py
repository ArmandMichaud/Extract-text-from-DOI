#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 15:49:34 2024

@author: amichaud
"""

import json
import sys
import os

def read_json_file(file_path):
    """Read JSON data from a file."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_pubtator_format(json_data, file_name, text_part):
    """Generate PubTator format content from JSON data."""
    output_lines = []

    # Extract the text data from the specified part (e.g., 'abstract' or 'data')
    text_data = json_data[text_part]['text']
    if text_part == 'abstract' :
        output_lines.append(f"{file_name}|t|{text_data}")
    
    if text_part == 'body' or text_part == 'data':
        output_lines.append(f"{file_name}|a|{text_data}")
    
    #elif text_part == 'title':
    #    output_lines.append(f"{file_name}|t|{text_data}")

    # Extract annotations
    annotations = json_data[text_part]['annotations']
    for annotation in annotations:
        mention = annotation['mention']
        obj = annotation['obj']
        annotation_id = ",".join(annotation['id'])
        begin = annotation['span']['begin']
        end = annotation['span']['end']
        output_lines.append(f"{file_name}\t{begin}\t{end}\t{mention}\t{obj}\t{annotation_id}")

    return "\n".join(output_lines)

def save_to_file(content, output_file_path):
    """Save content to a file."""
    with open(output_file_path, 'w') as file:
        file.write(content)

def process_file(json_file_path):
    """Process a JSON file and generate PubTator content."""
    file_name = os.path.basename(json_file_path).split('.json')[0]  # Get the base name of the file without extension
    
    try:
        pubtator_content = ""
        json_data = read_json_file(json_file_path)  # Read JSON data from file
        
        # Check if 'abstract' part exists and generate content
        if 'title' in json_data:
            pubtator_content = generate_pubtator_format(json_data, file_name, 'title')
            
        # Check if 'abstract' part exists and generate content
        if 'abstract' in json_data:
            pubtator_content = generate_pubtator_format(json_data, file_name, 'abstract')
        
        # Check if 'data' part exists and append generated content
        if 'data' in json_data :
            if pubtator_content:  # Add a new line if there is already content
                pubtator_content += '\n'
            pubtator_content += generate_pubtator_format(json_data, file_name, 'data')
        
        # Check if 'body' part exists and append generated content
        if 'body' in json_data :
            if pubtator_content:  # Add a new line if there is already content
                pubtator_content += '\n'
            pubtator_content += generate_pubtator_format(json_data, file_name, 'body')
        
        return pubtator_content
    
    except Exception as e:
        print(f"An error occurred while processing {json_file_path}: {e}")

def main():
    """Main function to handle input arguments and process files or directories."""
    if len(sys.argv) != 3:
        print("Usage: python script.py <json_file_path_or_directory> <output_directory>")
        return
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Create the output directory if it does not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created output directory: {output_path}")
    
        
    if os.path.isfile(input_path):
        # Process single file
        pubtator_content = process_file(input_path)
        file_name = os.path.basename(input_path).split('.json')[0]
        output_file_path = os.path.join(output_path, f"{file_name}.pubtator")
        save_to_file(pubtator_content, output_file_path)
        print(f"Output saved to {output_file_path}")
    
    elif os.path.isdir(input_path):
        # Process all JSON files in the directory
        for filename in os.listdir(input_path):
            if filename.endswith('.json'):
                file_path = os.path.join(input_path, filename)
                pubtator_content = process_file(file_path)
                output_file_path = os.path.join(output_path, f"{filename.split('.json')[0]}.pubtator")
                save_to_file(pubtator_content, output_file_path)
                print(f"Output saved to {output_file_path}")
    
    else:
        print(f"The path {input_path} is neither a file nor a directory.")

if __name__ == "__main__":
    main()
