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

def process_json_string(json_string):
    """
    Process the JSON string to replace newlines with nothing in 'abstract' and 'body' if present.
    
    Args:
        json_string (str): The input string in JSON format.
    
    Returns:
        str: The modified JSON string.
    """
    # Parse the JSON string
    data = json.loads(json_string)
    
    # Replace newlines in 'abstract' if present
    if 'abstract' in data and data['abstract']:
        data['abstract'] = data['abstract'].replace('\n', '')
    
    # Replace newlines in 'body' if present
    if 'body' in data and data['body']:
        data['body'] = data['body'].replace('\n', '')
    
    # Convert the modified data back to a JSON string
    modified_json_string = json.dumps(data)
    
    return modified_json_string


def supprimer_refs_avec_contenu(xml_data):
    xml_wo_ref = re.sub(r'<ref type.*?</ref>', '', xml_data, flags=re.DOTALL)
    return xml_wo_ref
    


def extraction_data_tei(xml_data_modif, name_file, output_dir):
  
    doc = grobid_tei_xml.parse_document_xml(xml_data_modif)
    data_parsee = json.dumps(doc.to_dict(), indent=2)
    with open(output_dir+"/"+name_file+".json", "w") as fichier:
        # Écrire dans le fichier
        
        
        data_parsee = process_json_string(data_parsee)
        fichier.write(data_parsee)
        print(data_parsee)
        
   

def lecture_xml(path_xml):
    # Ouvre le fichier XML et lit son contenu
    with open(path_xml, 'r', encoding='utf-8') as file:
        xml_data = file.read()
    return xml_data





def main():
    # Dossier contenant les fichiers PDF à analyser
    tei_directory = "./data_tei_xml"
    # Répertoire où vous souhaitez enregistrer les fichiers de sortie
    output_dir = "./data_json" # Répertoire où vous souhaitez enregistrer le fichier de sortie
    
    
    # Parcourir tous les fichiers dans le dossier
    for filename in os.listdir(tei_directory):
        if filename.endswith(".tei.xml"):
            xml_path = os.path.join(tei_directory, filename)
            xml_data = lecture_xml(xml_path)
            xml_data_modif = supprimer_refs_avec_contenu(xml_data)
            extraction_data_tei(xml_data_modif,filename.replace(".tei.xml", ""), output_dir)



main()
