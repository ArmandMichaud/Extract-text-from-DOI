#!/bin/bash

# Répertoires pour les téléchargements
scihub_dir="data_pdf_scihub"
doi_dir="data_pdf_DOI"
combined_dir="data_pdf"
log_file="logs/errors_download.txt"

# Créer les répertoires s'ils n'existent pas
mkdir -p "$scihub_dir"
mkdir -p "$doi_dir"
mkdir -p "$combined_dir"
mkdir -p "logs"

# Vérifier si un fichier contenant des DOI est fourni en argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 doi_file.txt"
    exit 1
fi

# Fichier contenant la liste des DOI
doi_file=$1

# Vérifier si le fichier existe
if [ ! -f "$doi_file" ]; then
    echo "Le fichier $doi_file n'existe pas."
    exit 1
fi

# Fonction pour télécharger en utilisant SciHub
download_scihub() {
    local doi=$1
    local modified_doi=$(echo "$doi" | sed -e 's/</%3C/g' -e 's/>/%3E/g' -e 's/:/%3A/g' -e 's/;/%3B/g' -e 's/\//%2F/g')
    local filename="${modified_doi}.pdf"
    local temp_page="temppage"

    wget -q -O "$temp_page" "https://sci-hub.3800808.com/$doi"
    url=$(python3 script_python/extract_publi.py "$temp_page")

    if [ -z "$url" ] || [[ "$url" == "err"* ]]; then
        echo "$doi" >> "$log_file"
        rm -f "$temp_page"
        return 1
    fi

    wget -q -O "$scihub_dir/$filename" "$url"
    if [ -f "$scihub_dir/$filename" ] && [ -s "$scihub_dir/$filename" ]; then
        if [ ! -f "$combined_dir/$filename" ]; then
            cp "$scihub_dir/$filename" "$combined_dir/$filename"
        fi
    else
        echo "$doi" >> "$log_file"
        rm -f "$scihub_dir/$filename"
        rm -f "$temp_page"
        return 1
    fi

    rm -f "$temp_page"
    return 0
}

# Fonction pour télécharger en utilisant DOI
download_doi() {
    local doi=$1
    local modified_doi=$(echo "$doi" | sed -e 's/</%3C/g' -e 's/>/%3E/g' -e 's/:/%3A/g' -e 's/;/%3B/g' -e 's/\//%2F/g')
    local filename="${modified_doi}.pdf"
    local html_content=$(wget -qO- "https://doi.org/$doi")
    local pdf_link=$(echo "$html_content" | grep -oP 'https://.*?\.pdf')

    if [ -n "$pdf_link" ]; then
        wget -q "$pdf_link" -O "$doi_dir/$filename"
        if [ -f "$doi_dir/$filename" ] && [ -s "$doi_dir/$filename" ]; then
            if [ ! -f "$combined_dir/$filename" ]; then
                cp "$doi_dir/$filename" "$combined_dir/$filename"
            fi
        else
            echo "$doi" >> "$log_file"
            rm -f "$doi_dir/$filename"
            return 1
        fi
    else
        echo "$doi" >> "$log_file"
        return 1
    fi

    return 0
}

# Boucler à travers chaque DOI dans le fichier
while IFS= read -r doi; do
    if ! download_scihub "$doi"; then
        download_doi "$doi"
    fi
done < "$doi_file"

echo "Téléchargement terminé. Vérifiez '$combined_dir' pour les articles téléchargés."
