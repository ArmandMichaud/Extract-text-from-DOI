#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 11:30:37 2024

@author: amichaud
"""

import requests
import json

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

# Load JSON data
with open("publications.json", "r") as f:
    publications = json.load(f)
    
# retrieve DOIs and write them to a text file
# or in an error file if not found
with open("doi.txt", "w") as f, open("./logs/errors_extract_doi_from_pmid.txt", "w") as f_err:
    for publication in publications:
        pmid = publication["value"]
        doi = get_doi_from_pmid(pmid)
        if doi:
            f.write(doi + "\n")
        else:
            f_err.write(f"DOI not found for PMID {pmid}\n")

        


