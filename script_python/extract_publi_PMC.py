import os
import requests
import xml.etree.ElementTree as ET
import re
import subprocess
import sys

# Répertoire de sortie pour les PDFs
output_dir = "data_pdf"
os.makedirs(output_dir, exist_ok=True)

# Fichier de log
log_file = "log_PMC.txt"

# Fonction pour convertir le PMID en PMCID
def pmid_to_pmcid(pmid):
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmid}&format=xml"
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        record = root.find(".//record")
        if 'pmcid' in record.attrib:
            return record.attrib['pmcid']
    return None

# Fonction pour trouver l'URL du PDF à partir de la page PMCID
def find_pdf_url(pmcid):
    url = f"https://www.ncbi.nlm.nih.gov/pmc/?term={pmcid}"
    response = requests.get(url)
    if response.status_code == 200:
        # Utilisation des expressions régulières pour trouver le lien du PDF
        pdf_url_pattern = rf'/pmc/articles/{pmcid}/pdf/[^"]+\.pdf'
        pdf_url_match = re.search(pdf_url_pattern, response.text)
        if pdf_url_match:
            return f"https://www.ncbi.nlm.nih.gov{pdf_url_match.group(0)}"
    return None

# Fonction pour télécharger le PDF en utilisant wget
def download_pdf_with_wget(pdf_url, file_name):
    pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
    command = f"wget --user-agent=\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\" -O {pdf_path} {pdf_url}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du téléchargement du PDF avec wget: {e.stderr.decode().strip()}")
        return False

# Fonction pour transformer le DOI en un format de fichier valide
def transform_doi(doi):
    return re.sub(r'[<>:;/]', lambda x: f"%{ord(x.group(0)):02X}", doi)

# Fonction pour obtenir le DOI à partir du PMID
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

def main():
    if len(sys.argv) != 2:
        print("Erreur: Veuillez fournir un fichier d'entrée contenant des DOI ou des PMID.")
        print("Usage: python script.py <fichier_d_entree>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Erreur: Le fichier {input_file} n'existe pas.")
        sys.exit(1)

    # Lire la liste des DOI et PMID à partir du fichier
    with open(input_file, 'r') as f:
        identifiers = [line.strip() for line in f.readlines()]
    
    # Traiter chaque identifiant
    with open(log_file, 'w') as log:
        for identifier in identifiers:
            if identifier.lower().startswith('10.'):
                # C'est un DOI
                doi = identifier
                file_name = transform_doi(doi)
                pmcid = pmid_to_pmcid(doi)
            else:
                # C'est un PMID
                pmid = identifier
                doi = get_doi_from_pmid(pmid)
                if doi:
                    file_name = transform_doi(doi)
                else:
                    file_name = pmid
                pmcid = pmid_to_pmcid(pmid)
    
            if pmcid:
                pdf_url = find_pdf_url(pmcid)
                if pdf_url:
                    success = download_pdf_with_wget(pdf_url, file_name)
                    if success:
                        print(f"Article {identifier} téléchargé avec succès en tant que {file_name}.pdf")
                    else:
                        print(f"Échec du téléchargement de l'article {identifier} (PMCID: {pmcid})")
                        log.write(f"Échec du téléchargement de l'article {identifier} (PMCID: {pmcid})\n")
                else:
                    print(f"URL PDF non trouvée pour l'article {identifier} (PMCID: {pmcid})")
                    log.write(f"URL PDF non trouvée pour l'article {identifier} (PMCID: {pmcid})\n")
            else:
                print(f"PMCID non trouvé pour l'article {identifier}")
                log.write(f"PMCID non trouvé pour l'article {identifier}\n")

if __name__ == "__main__":
    main()

