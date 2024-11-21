import os
import re
import requests
import time

# Chemins par défaut
INPUT_FOLDER = "ascidians_doi"  # Dossier contenant les fichiers DOI
OUTPUT_FOLDER = "data_pdf"      # Dossier où seront enregistrés les PDFs
LOG_FOLDER = "logs"             # Dossier pour les fichiers de logs

# Paramètres globaux
MAX_RETRIES = 3  # Nombre maximum de tentatives pour un téléchargement
TIMEOUT = 5      # Temps limite pour une requête (en secondes)
WAIT_TIME = 2    # Temps d'attente entre deux tentatives (en secondes)

def create_directories():
    """
    Crée les dossiers de base nécessaires pour stocker les PDFs et les logs.
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)

def extract_url_from_html(html_content):
    """
    Extrait l'URL du fichier PDF à partir de la balise <iframe> dans le contenu HTML.

    Args:
        html_content (str): Contenu HTML téléchargé.

    Returns:
        str: L'URL du fichier PDF ou None si aucune URL n'est trouvée.
    """
    pattern = r'<iframe[^>]*src="([^"]*)"'
    match = re.search(pattern, html_content)
    if match:
        return match.group(1)
    return None

def download_page(doi, retries=MAX_RETRIES):
    """
    Télécharge la page Sci-Hub correspondant à un DOI avec plusieurs tentatives.

    Args:
        doi (str): DOI à traiter.
        retries (int): Nombre de tentatives restantes.

    Returns:
        str: Contenu HTML de la page ou None si une erreur survient.
    """
    sci_hub_url = f"https://sci-hub.3800808.com/{doi}"

    while retries > 0:
        try:
            response = requests.get(sci_hub_url, timeout=TIMEOUT)
            # Si le téléchargement est réussi ou partiellement réussi
            if response.ok or response.status_code in [403, 404]:
                return response.text
        except requests.RequestException as e:
            print(f"**ERREUR:** Une exception s'est produite pour le DOI {doi}: {e}")
        
        retries -= 1
        print(f"Nouvelle tentative pour {doi} dans {WAIT_TIME} secondes...")
        time.sleep(WAIT_TIME)

    print(f"**ERREUR:** Échec de téléchargement pour le DOI {doi} après plusieurs tentatives.")
    return None

def download_pdf(doi, pdf_url, output_folder, retries=MAX_RETRIES):
    """
    Télécharge le fichier PDF depuis une URL avec plusieurs tentatives.

    Args:
        doi (str): DOI du fichier.
        pdf_url (str): URL du fichier PDF.
        output_folder (str): Chemin du dossier où stocker le PDF.
        retries (int): Nombre de tentatives restantes.

    Returns:
        bool: True si le téléchargement réussit, False sinon.
    """
    filename = f"{output_folder}/{doi.replace('/', '_')}.pdf"

    while retries > 0:
        try:
            response = requests.get(pdf_url, stream=True, timeout=TIMEOUT)
            if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('application/pdf'):
                with open(filename, "wb") as pdf_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        pdf_file.write(chunk)
                print(f"**PDF téléchargé avec succès:** {filename}")
                return True
        except requests.RequestException as e:
            print(f"**ERREUR:** Une exception s'est produite lors du téléchargement du PDF pour {doi}: {e}")
        
        retries -= 1
        print(f"Nouvelle tentative pour télécharger le PDF {doi} dans {WAIT_TIME} secondes...")
        time.sleep(WAIT_TIME)

    print(f"**ERREUR:** Échec du téléchargement du PDF pour le DOI {doi} après plusieurs tentatives.")
    return False

def process_doi_file(file_path):
    """
    Lit un fichier de DOIs et tente de télécharger les PDFs correspondants,
    en les stockant dans un sous-dossier basé sur le nom du fichier DOI.

    Args:
        file_path (str): Chemin du fichier contenant les DOIs.
    """
    if not os.path.exists(file_path):
        print(f"**ERREUR:** Le fichier {file_path} n'existe pas.")
        return

    # Récupérer le nom du fichier sans extension pour créer un sous-dossier
    file_name = os.path.basename(file_path).rsplit('.', 1)[0]
    output_folder = os.path.join(OUTPUT_FOLDER, file_name)
    os.makedirs(output_folder, exist_ok=True)

    # Fichier log pour ce fichier DOI
    error_log = os.path.join(LOG_FOLDER, f"errors_{file_name}.txt")

    with open(file_path, "r") as doi_file, open(error_log, "a") as log_file:
        for doi in doi_file:
            doi = doi.strip()
            if not doi:
                continue

            print(f"**Traitement du DOI:** {doi}")
            html_content = download_page(doi)

            if html_content is None:
                log_file.write(f"DOI non téléchargé: {doi}\n")
                continue

            pdf_url = extract_url_from_html(html_content)

            if pdf_url:
                success = download_pdf(doi, pdf_url, output_folder)
                if not success:
                    log_file.write(f"PDF non téléchargé: {doi}\n")
            else:
                print(f"**ERREUR:** URL du PDF introuvable pour le DOI {doi}")
                log_file.write(f"URL introuvable: {doi}\n")

def find_doi_files(folder):
    """
    Trouve tous les fichiers .txt contenant des DOIs dans un dossier.

    Args:
        folder (str): Chemin du dossier à analyser.

    Returns:
        list: Liste des chemins de fichiers trouvés.
    """
    doi_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".txt"):
                doi_files.append(os.path.join(root, file))
    return doi_files

def process_all_doi_files():
    """
    Lance le traitement pour tous les fichiers DOI dans le dossier d'entrée.
    """
    doi_files = find_doi_files(INPUT_FOLDER)
    if not doi_files:
        print(f"**Aucun fichier DOI trouvé dans le dossier {INPUT_FOLDER}.**")
        return

    for doi_file in doi_files:
        print(f"**Traitement du fichier:** {doi_file}")
        process_doi_file(doi_file)

def main():
    print("**Initialisation...**")
    create_directories()
    print("**Traitement des fichiers DOI...**")
    process_all_doi_files()
    print("**Téléchargement terminé. Les fichiers sont organisés par nom de fichier DOI dans le dossier de sortie.**")

if __name__ == "__main__":
    main()
