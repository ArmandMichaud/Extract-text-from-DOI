#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to analyse text with bern2 (regex clean of 'NaN' in response only, with figure legends support)

@author: amichaud
"""

import os
import json
import re
import requests

def save_file(file_name, res_data_directory, content):
    file_path = os.path.join(res_data_directory, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=2)

def regex_clean_nan_in_response(data):
    """
    Recursively apply regex to remove 'NaN' (as a word) from any string in the response.
    """
    if isinstance(data, dict):
        return {k: regex_clean_nan_in_response(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [regex_clean_nan_in_response(item) for item in data]
    elif isinstance(data, str):
        return re.sub(r'\bNaN\b', '', data, flags=re.IGNORECASE)
    else:
        return data

def query_plain(text, url="http://localhost:8888/plain"):
    try:
        response = requests.post(url, json={'text': text})
        response.raise_for_status()
        cleaned = regex_clean_nan_in_response(response.json())
        return cleaned
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {}

def process_json_files(json_directory, res_data_directory):
    directory_path = os.path.abspath(json_directory)
    if not os.path.isdir(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            res_abstract = query_plain(data['abstract']) if 'abstract' in data and data['abstract'] else {}
            res_body = query_plain(data['body']) if 'body' in data and data['body'] else {}

            res_legends = []
            if 'figure_legends' in data and isinstance(data['figure_legends'], list):
                for legend in data['figure_legends']:
                    if legend.strip():
                        res_legends.append(query_plain(legend))

            json_final = {
                "abstract": res_abstract,
                "body": res_body,
                "figure_legends": res_legends
            }

            result_filename = "data_bern2_" + filename
            print(f"File {filename} processed successfully.")
            save_file(result_filename, res_data_directory, json_final)

def main():
    json_directory = "./data_json"
    res_data_directory = "./data_bern2"
    os.makedirs(res_data_directory, exist_ok=True)
    process_json_files(json_directory, res_data_directory)

main()

