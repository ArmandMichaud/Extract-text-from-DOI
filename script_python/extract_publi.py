#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to read the content of a file and extract URL links from <iframe> tags.


@author: amichaud
"""

import re
import argparse

def read_file_content(file_name):
    """
    Read the content of a file.

    Args:
        file_name (str): The name of the file to read.

    Returns:
        str: The content of the file.
    """
    try:
        with open(file_name, 'r') as file:
            text = file.read()
            return text
    except FileNotFoundError:
        print("err: The specified file does not exist.")
        return ''

def parse_file(text):
    """
    Extract URL links from <iframe> tags in the provided text.

    Args:
        text (str): The text in which to search for <iframe> tags.

    Returns:
        None
    """
    # Using a regular expression to extract the content of the <iframe> tag
    pattern = r'<iframe[^>]*>.*?</iframe>'
    iframe_content = re.findall(pattern, text, re.DOTALL)

    # Using a regular expression to extract the HTTP link contained within the <iframe> tag text
    if iframe_content:
        src_content = iframe_content[0]
        pattern_src = r'src="([^"]*)"'
        src_link = re.search(pattern_src, src_content)

        if src_link:
            iframe_src_url = src_link.group(1)
            print(iframe_src_url)
        else:
            print("err: No link found inside the <iframe> tag.")
    else:
        print("err: No <iframe> tag found in the HTML content.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read the content of a file.')
    parser.add_argument('file_name', type=str, help='Name of the file to read')

    args = parser.parse_args()
    text = read_file_content(args.file_name)
    parse_file(text)

