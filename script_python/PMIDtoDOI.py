#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 12:40:23 2024

@author: amichaud
"""

import requests
import argparse

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


def lire_fichier(nom_fichier):
    try:
        with open(nom_fichier, "r") as f:
            lignes = f.readlines()
            lignes_propres = [ligne.rstrip() for ligne in lignes]  # Enlever le caractère de nouvelle ligne
        return lignes_propres
    except FileNotFoundError:
        print("The file doesn't exist")
        return []



            
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PMIDs to DOIs")
    parser.add_argument("PMID_input_file", help="Txt input file containing PMID list")
    parser.add_argument("DOI_output_file", help="Txt output file containing DOI list")

    args = parser.parse_args()
    PMID_input_file = args.PMID_input_file
    DOI_output_file = args.DOI_output_file
    listPMID = lire_fichier(PMID_input_file)
    erreurs = []

    with open(DOI_output_file, "w") as f:
        for pmid in listPMID:
            doi = get_doi_from_pmid(pmid)
            if doi:
                f.write(doi + "\n")
            else:
                erreurs.append(f"DOI not found for PMID {pmid}")

    if erreurs:
        with open("logs/errors_extract_doi_from_pmid.txt", "w") as f_err:
            for erreur in erreurs:
                f_err.write(erreur + "\n")

