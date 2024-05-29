#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 11:33:27 2024

@author: amichaud
"""

from Bio import Entrez
import argparse

def search_pubmed(query):
    Entrez.email = "votre@email.com"  # Remplacez par votre email
    handle = Entrez.esearch(db="pubmed", term=query, retmax=100000)
    results = Entrez.read(handle)
    handle.close()
    return results["IdList"]

def save_pmid_to_file(pmid_list, filename):
    with open(filename, "w") as file:
        for pmid in pmid_list:
            file.write(pmid + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Searches PubMed for articles and saves PMIDs to file.")
    parser.add_argument("search_query", help="The PubMed search query (enclose phrases in quotation marks).")
    parser.add_argument("filename", help="The name of the file in which to save PMIDs.")

    args = parser.parse_args()

    search_query = args.search_query
    filename = args.filename

    pmid_list = search_pubmed(search_query)
    save_pmid_to_file(pmid_list, filename)

    print(f"{len(pmid_list)} articles found for the query '{search_query}'. The PMIDs were registered in {filename}.")
    
    
    
    
    
    
    
    
    
    
    