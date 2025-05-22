#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import argparse
from urllib.parse import urljoin

def read_file_content(file_name):
    """Read the content of a file."""
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print("err: The specified file does not exist.")
        return ''

def extract_pdf_urls(text, base_url="https://sci-hub.se/"):
    """Extracts all possible PDF URLs from the HTML page."""

    possible_urls = set()  # Utilisation d'un set pour éviter les doublons

    # 1️⃣ Chercher les URLs dans les balises `onclick` des boutons (<button>)
    button_pattern = r"onclick=['\"]location.href=['\"](//[^'\"]+\.pdf)[?'\"]?"
    for match in re.findall(button_pattern, text):
        possible_urls.add(urljoin(base_url, match))

    # 2️⃣ Chercher les balises `<embed>` contenant un PDF
    embed_pattern = r'<embed[^>]+src=["\'](//[^"\']+\.pdf)[^"\']*["\']'
    for match in re.findall(embed_pattern, text):
        possible_urls.add(urljoin(base_url, match))

    # 3️⃣ Chercher les balises `<iframe>` contenant un PDF
    iframe_pattern = r'<iframe[^>]+src=["\'](//[^"\']+\.pdf)["\']'
    for match in re.findall(iframe_pattern, text):
        possible_urls.add(urljoin(base_url, match))

    # 4️⃣ Chercher les balises `<a>` contenant un lien vers un PDF
    a_href_pattern = r'href=["\'](https?://[^"\']+\.pdf)["\']'
    for match in re.findall(a_href_pattern, text):
        possible_urls.add(match)

    # 5️⃣ Chercher les liens PDF dans du JavaScript (ex: `window.location.href = 'URL'`)
    js_pattern = r'window\.location\.href\s*=\s*["\'](https?://[^"\']+\.pdf)["\']'
    for match in re.findall(js_pattern, text):
        possible_urls.add(match)

    # 📌 Si des liens sont trouvés, les afficher
    if possible_urls:
        for url in possible_urls:
            print(url)
        return

    # 📌 Si aucun lien trouvé, on sauvegarde le fichier pour analyse
    with open("debug_scihub.html", "w", encoding="utf-8") as debug_file:
        debug_file.write(text)

    print("err: No valid PDF URL found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract publication URL from Sci-Hub page.')
    parser.add_argument('file_name', type=str, help='Name of the file to read')

    args = parser.parse_args()
    text = read_file_content(args.file_name)
    extract_pdf_urls(text)

