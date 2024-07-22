#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 15:36:48 2024

@author: amichaud
"""

import fitz  # PyMuPDF
import os
import re
import shutil
from collections import defaultdict

def extract_figures_and_coords(text):
    pattern = re.compile(
        r'<figure(?![^>]*\btype="table")[^>]*>\s*'
        r'<head>[^<]*</head>\s*'
        r'<label>[^<]*</label>\s*'
        r'<figDesc>(.*?)</figDesc>\s*'
        r'(<graphic[^>]*coords="([^"]+)"[^>]*type="bitmap"[^>]*/>)?',
        re.DOTALL
    )
    matches = pattern.findall(text)
    results = []

    for match in matches:
        figDesc = match[0].strip()
        coords = match[2].strip() if match[1] else None
        results.append((figDesc, coords))

    return results

def extract_figure_number(figDesc):
    pattern = re.compile(
        r'(?:Fig(?:ure)?(?:\s|\.|s|ure supplement)?\.?\s*(\d+[A-Za-z]?))', 
        re.IGNORECASE
    )
    
    matches = pattern.findall(figDesc)
    if matches:
        return matches[0]
    else:
        raise ValueError(f"No figure number found in description: {figDesc}")

def extract_images_from_coords(pdf_path, coords_list, output_dir, zoom=2.0):
    doc = fitz.open(pdf_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    figures_per_page = {}
    image_paths = []

    for coords in coords_list:
        if coords:
            page_num, x, y, w, h = map(float, coords.split(','))
            page_num = int(page_num)
            page = doc[page_num - 1]

            rect = fitz.Rect(x, y, x + w, y + h)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, clip=rect)

            if page_num not in figures_per_page:
                figures_per_page[page_num] = 0
            figures_per_page[page_num] += 1
            figure_num = figures_per_page[page_num]

            output_image_path = f"{output_dir}/coord_page_{page_num}_figure_{figure_num}.png"
            pix.save(output_image_path)
            image_paths.append(output_image_path)
            print(f"Image extracted and saved to: {output_image_path}")

    return image_paths

def extract_images_from_pdf(pdf_path, output_folder, error_log):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_document = fitz.open(pdf_path)
    image_paths = []
    size_count = defaultdict(int)

    # First pass to count the image sizes
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_info in image_list:
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_size = len(image_bytes)

            size_count[image_size] += 1

    # Second pass to extract unique images by size
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_size = len(image_bytes)

            if size_count[image_size] > 1:
                # Log the error in the TSV file
                error_log.write(f"{os.path.basename(pdf_path)}\t\tDuplicate image size detected (Size: {image_size} bytes)\tThe image is ignored because it has the same size as other images\n")
                continue  # Ignore this image as it has duplicates

            img_filename = f"extract_page_{page_num + 1}_image_{img_index + 1}.png"
            img_path = os.path.join(output_folder, img_filename)
            with open(img_path, "wb") as img_file:
                img_file.write(image_bytes)
            image_paths.append(img_path)

    pdf_document.close()
    return image_paths

def html_creation(pdf_filename_without_ext, results, image_paths_coords, image_paths_pdf, output_dir, error_log):
    html_filename = f"{output_dir}/{pdf_filename_without_ext}.html"
    with open(html_filename, 'w', encoding='utf-8') as html_file:
        html_file.write(f"<html><head><title>{pdf_filename_without_ext}</title></head><body>\n")
        html_file.write(f"<h1>{pdf_filename_without_ext}</h1>\n")
        html_file.write("<table border='1'>\n")
        html_file.write("<tr><th>Figure Number</th><th>Image</th><th>Caption</th></tr>\n")

        image_idx = 0
        for figDesc, coords in results:
            try:
                figure_number = extract_figure_number(figDesc)
            except ValueError as e:
                print(e)
                figure_number = 'Error'
                if not coords:
                    error_log.write(f"{pdf_filename_without_ext}\t\t{figDesc}\tNo coordinates and no figure number\tNo coordinates and no figure number found\n")
                    continue

                if coords and image_idx < len(image_paths_coords):
                    image_path = image_paths_coords[image_idx]
                    error_log.write(f"{pdf_filename_without_ext}\t{image_path}\t{figDesc}\tNo figure number\tNo figure number found\n")
                    image_idx += 1
                else:
                    error_log.write(f"{pdf_filename_without_ext}\t\t{figDesc}\tNo figure number\tNo figure number found\n")

            html_file.write("<tr>\n")
            html_file.write(f"<td>{figure_number}</td>\n")

            if coords and image_idx < len(image_paths_coords):
                image_path = image_paths_coords[image_idx]
                relative_image_path = os.path.relpath(image_path, output_dir)
                html_file.write(f"<td><img src='{relative_image_path}' alt='Image'></td>\n")
                image_idx += 1
            else:
                html_file.write("<td></td>\n")

            html_file.write(f"<td>{figDesc}</td>\n")
            html_file.write("</tr>\n")

        html_file.write("</table>\n")

        # Adding images extracted from the PDF
        html_file.write("<h2>Additional Images Extracted from PDF</h2>\n")
        html_file.write("<table border='1'>\n")
        html_file.write("<tr><th>Image</th></tr>\n")
        for image_path in image_paths_pdf:
            relative_image_path = os.path.relpath(image_path, output_dir)
            html_file.write("<tr>\n")
            html_file.write(f"<td><img src='{relative_image_path}' alt='Image'></td>\n")
            html_file.write("</tr>\n")

        html_file.write("</table>\n")

        html_file.write("</body></html>\n")
    print(f"HTML file created: {html_filename}")

def main():
    output_root_dir = 'data_figure_html'

    if os.path.exists(output_root_dir):
        shutil.rmtree(output_root_dir)

    os.makedirs(output_root_dir)

    pdf_folder = './data_pdf'
    tei_folder = './data_tei_xml'
    error_log_path = os.path.join(output_root_dir, 'error_log.tsv')

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]

    with open(error_log_path, 'w', encoding='utf-8') as error_log:
        error_log.write("PDF Filename\tImage Path\tFigure Description\tError\tExplanation\n")

        for pdf_file in pdf_files:
            pdf_filename_without_ext = os.path.splitext(pdf_file)[0]
            tei_file_path = os.path.join(tei_folder, f"{pdf_filename_without_ext}.tei.xml")

            if os.path.exists(tei_file_path):
                print(f"Extracting legends for {pdf_file} \n")
                with open(tei_file_path, 'r', encoding='utf-8') as tei_file:
                    tei_content = tei_file.read()

                results = extract_figures_and_coords(tei_content)

                output_dir = os.path.join(output_root_dir, pdf_filename_without_ext)
                coords_list = [coords for _, coords in results if coords]
                image_paths_coords = extract_images_from_coords(os.path.join(pdf_folder, pdf_file), coords_list, output_dir, zoom=1.0)
                image_paths_pdf = extract_images_from_pdf(os.path.join(pdf_folder, pdf_file), output_dir, error_log)

                html_creation(pdf_filename_without_ext, results, image_paths_coords, image_paths_pdf, output_dir, error_log)
            else:
                error_log.write(f"{pdf_filename_without_ext}\t\t\tNo corresponding TEI file found\tNo corresponding TEI file found\n")
                print(f"Error: No corresponding TEI file found for {pdf_file}")

if __name__ == "__main__":
    main()
