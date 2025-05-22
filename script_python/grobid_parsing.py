#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:54:27 2024

@author: amichaud
"""

import json
import grobid_tei_xml
import re
import os
from bs4 import BeautifulSoup

def process_json_string(json_string):
    """
    Clean 'abstract' and 'body' fields by removing newlines.
    
    Args:
        json_string (str): The input JSON string.
    
    Returns:
        str: The cleaned JSON string.
    """
    data = json.loads(json_string)

    if 'abstract' in data and data['abstract']:
        data['abstract'] = data['abstract'].replace('\n', '')
    if 'body' in data and data['body']:
        data['body'] = data['body'].replace('\n', '')

    return json.dumps(data)

def remove_references_with_content(xml_data):
    """
    Remove all <ref> elements with content from the XML.
    
    Args:
        xml_data (str): The raw XML string.
    
    Returns:
        str: The XML string with <ref> removed.
    """
    return re.sub(r'<ref type.*?</ref>', '', xml_data, flags=re.DOTALL)

def extract_figure_legends(xml_data):
    """
    Extract figure legends from TEI XML.
    
    Args:
        xml_data (str): The XML string of the document.
    
    Returns:
        list: A list of figure legends (strings).
    """
    soup = BeautifulSoup(xml_data, "xml")
    figures = soup.find_all("figure")
    legends = []
    for fig in figures:
        desc = fig.find("figDesc")
        if desc:
            legends.append(desc.get_text(strip=True))
    return legends

def extract_tei_data(xml_data_modif, name_file, output_dir):
    """
    Parse TEI XML and export a JSON file with additional figure legends.
    
    Args:
        xml_data_modif (str): Cleaned and modified XML string.
        name_file (str): Base name for the output JSON file.
        output_dir (str): Directory to save the JSON.
    """
    doc = grobid_tei_xml.parse_document_xml(xml_data_modif)
    doc_dict = doc.to_dict()

    # Extract and include figure legends
    legends = extract_figure_legends(xml_data_modif)
    doc_dict["figure_legends"] = legends

    data_parsed = json.dumps(doc_dict, indent=2)
    data_parsed = process_json_string(data_parsed)

    with open(os.path.join(output_dir, name_file + ".json"), "w") as file:
        file.write(data_parsed)
        print(data_parsed)

def read_xml(path_xml):
    """
    Read the content of a .tei.xml file.
    
    Args:
        path_xml (str): Path to the XML file.
    
    Returns:
        str: The XML file content.
    """
    with open(path_xml, 'r', encoding='utf-8') as file:
        return file.read()

def main():
    """
    Main function to process all .tei.xml files in a directory.
    """
    tei_directory = "./data_tei_xml"
    output_dir = "./data_json"

    for filename in os.listdir(tei_directory):
        if filename.endswith(".tei.xml"):
            xml_path = os.path.join(tei_directory, filename)
            xml_data = read_xml(xml_path)
            xml_data_modif = remove_references_with_content(xml_data)
            extract_tei_data(xml_data_modif, filename.replace(".tei.xml", ""), output_dir)

main()

