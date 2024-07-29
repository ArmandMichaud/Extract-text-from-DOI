#!/bin/bash

# Vérifier si un fichier contenant des DOI est fourni en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 <DOI_file>"
    exit 1
fi

# Fichier contenant la liste des DOI
doi_file=$1

# Répertoire pour enregistrer les articles téléchargés
download_dir="data_pdf"
error_file="erreur_extraction_doi.txt"

# Créer le répertoire de téléchargement s'il n'existe pas
mkdir -p "$download_dir"

# Boucler à travers chaque DOI dans le fichier
while IFS= read -r doi; do
    # Remplacer les "/" par "%2F" dans le DOI
    doi_formatted=$(echo "$doi" | sed -e 's/</%3C/g' -e 's/>/%3E/g' -e 's/:/%3A/g' -e 's/;/%3B/g' -e 's/\//%2F/g')
    

    # Récupérer le contenu HTML de la page de l'article
    html_content=$(wget -qO- "https://doi.org/$doi")

    # Rechercher le lien PDF dans le contenu HTML
    pdf_link=$(echo "$html_content" | grep -oP 'https://.*?\.pdf')

    # Si un lien PDF est trouvé, télécharger le fichier PDF
    if [ -n "$pdf_link" ]; then
        # Enregistrer le fichier avec le DOI formaté comme nom
        wget -q "$pdf_link" -O "$download_dir/$doi_formatted.pdf"
        echo "$doi file successfully downloaded"
    else
        echo "$doi" >> "$error_file"
        echo "$doi file download failed"
    fi
done < "$doi_file"

echo "Téléchargement terminé. Vérifiez '$download_dir' pour les articles téléchargés."

