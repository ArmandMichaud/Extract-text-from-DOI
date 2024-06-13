#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyse text with bern2


@author: amichaud
"""

import os
import json
import csv
import time
import re
import requests

def save_file(file_name, res_data_directory, content):
    """
    Save the content to a file in the specified directory.

    Args:
        file_name (str): The name of the file.
        res_data_directory (str): The directory to save the file.
        content (dict): The content to be saved.

    Returns:
        None
    """
    file_path = os.path.join(res_data_directory, file_name)
        
    with open(file_path, 'w') as file:
        # Serialize the data and write it to the file
        json.dump(content, file)
        
def query_plain(text, url="http://localhost:8888/plain"):
    """
    Send a POST request to a specified URL with the provided text.

    Args:
        text (str): The text to send in the request.
        url (str): The URL to send the request to. Default is "http://localhost:8888/plain".

    Returns:
        dict: The JSON response from the server.
    """
    return requests.post(url, json={'text': text}).json()
   

def process_json_files(json_directory, res_data_directory):
    """
    Process JSON files in the specified directory.

    Args:
        json_directory (str): The directory containing JSON files.
        res_data_directory (str): The directory to save the processed data.

    Returns:
        None
    """
    regex_pattern = re.compile(r',')
    # Absolute path of the directory containing JSON files
    directory_path = os.path.abspath(json_directory)

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Open a CSV file to write the results
    with open('results.csv', 'w', newline='') as csvfile:
        fieldnames = ['File Name', 'Abstract Time (s)', 'Body Time (s)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate through the files in the directory
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    if 'abstract' in data:
                        abstract_text = data['abstract']                    
                        start_time = time.time()  # Record start time
                        res_abstract = query_plain(abstract_text)
                        end_time = time.time()  # Record end time        
                        execution_time_abstract = end_time - start_time
                    else:
                        print(f"No 'abstract' key found in the file {file_path}")
                        execution_time_abstract = "#N/A"
                        
                    if 'body' in data:
                        body_text = data['body']                 
                        start_time = time.time()  # Record start time
                        res_body = query_plain(body_text)
                        end_time = time.time()  # Record end time                     
                        execution_time_body = end_time - start_time
                    else:
                        print(f"No 'body' key found in the file {file_path}")
                        execution_time_body = "#N/A"
                        
                    writer.writerow({'File Name': regex_pattern.sub('%2C', filename), 'Abstract Time (s)': execution_time_abstract, 'Body Time (s)': execution_time_body})
                    json_final = {
                        "abstract": res_abstract,
                        "body": res_body
                    }
                    result_filename = "data_bern2_"+filename
                    print(f"File {filename} processed successfully.")
                    save_file(result_filename, res_data_directory, json_final)
                    

def main():
    # Directory containing JSON files
    json_directory = "./data_json"
    os.makedirs('data_bern2', exist_ok=True)    
    res_data_directory = "./data_bern2"
    
    # Call the function to process JSON files in the specified directory
    process_json_files(json_directory, res_data_directory)
    
main()
