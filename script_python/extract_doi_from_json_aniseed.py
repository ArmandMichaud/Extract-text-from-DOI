#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 11:30:37 2024

@author: amichaud
"""

import requests
import json
import argparse
import os



def get_doi_from_pmid(pmid):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "json"
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    article_ids = data["result"][pmid]["articleids"]
    doi = next((article_id["value"] for article_id in article_ids if article_id["idtype"] == "doi"), None)
    return doi




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="parse the json file obtained with the Aniseed api")
    
    parser.add_argument("Json_input_file", help="Json input file containing PMID list")
    parser.add_argument("DOI_output_file", help="Txt output file containing DOI list")

    args = parser.parse_args()
    Json_input_file = args.Json_input_file
    DOI_output_file = args.DOI_output_file
    
    try:
        # Load JSON data
        with open(Json_input_file, "r") as f:
            publications = json.load(f)
    except FileNotFoundError:
        print("The file doesn't exist")

    
    erreurs = []    
    # retrieve DOIs and write them to a text file
    # or in an error file if not found
    with open(DOI_output_file, "w") as f:
        for publication in publications:
            pmid = publication["value"]
            doi = get_doi_from_pmid(pmid)
            if doi:
                f.write(doi + "\n")
            else:
                erreurs.append(f"DOI not found for PMID {pmid}")
    if erreurs:
       os.makedirs('logs', exist_ok=True)
       with open("logs/errors_extract_doi_from_pmid.txt", "w") as f_err:
           for erreur in erreurs:
               f_err.write(erreur + "\n")     


