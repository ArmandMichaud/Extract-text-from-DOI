# Software Documentation

## Introduction

This software aims to conduct biological entity analysis of scientific publications. 
The software takes the DOI of publications as input data, but allows users to start the analysis at various stages of the pipeline. 

The stages are as follows:
- Retrieval of scientific publications in PDF format using Sci-Hub
- Grobid analysis (standardisation of publications) for content and structure extraction of scientific publications (output in tei.xml format)
- Parsing of tei.xml files to retrieve the abstract and body text of publications (output in JSON format)
- (ToDo) Biological entity search using Bern2

## Prerequisites

### General dependencies 

Bash, apt, Git, Python 3.7 or higher (in a venv), 

### Grobid

For Grobid, you must have Docker installed: [Docker Installation Guide](https://docs.docker.com/desktop/install/ubuntu/)

```bash
sudo apt update && sudo apt install docker.io
```

You need to install Grobid: [Grobid GitHub Repository](https://github.com/kermitt2/grobid)

```bash
sudo docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
```

You must have the Grobid client for Python installed: [Grobid Python Client](https://github.com/kermitt2/grobid_client_python/tree/master)

```bash
pip install grobid
```

You must have the parser to analyze tei_xml files installed: [Grobid TEI_XML Parser](https://gitlab.com/internetarchive/grobid_tei_xml)

```bash
pip install grobid_tei_xml
```

## Software Installation

Warning: Once the software is installed, do not modify the hierarchical structure of the software files!

```bash
git clone https://github.com/ArmandMichaud/Extract-text-from-DOI Extract-text-from-DOI && cd Extract-text-from-DOI
```

__


## Using the Software

### Retrieval of scientific publications in PDF format using Sci-Hub

import a text file containing the DOI numbers of the publications you want to extract. 
There's a doi.txt file as an example file type. 
To run the extraction, you need to specify the txt file containing the DOI list as an argument:  

```bash
bash extract_publi_scihub.sh doi.txt
```

Publications will be saved in the data_pdf/ folder, with the DOI number as their name, replacing the '/' with '%2F'.
Some publications may not be available on Sci-Hub. Their names will be noted in the file "error_extract_scihub.txt".
You can manually add publications to be analysed, or publications that could not be extracted with Sci-Hub, simply by adding them to the data_pdf/ folder.

### Grobid

#### Launch Grobid
Before using Grobid, make sure to run Grobid locally. This can be done with the following command (same as installation):
```bash
sudo docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0&
```

This launches the software in the terminal. To stop Grobid, kill the corresponding PID. 
(TODO) Configure and Run Grobid as a service

#### Grobid analysis 
You may need to install requests first: `pip install requests`
Make sure the port 8070 is open and accessible.

To run the analysis:
```bash
bash extract_text_grobid.sh
```

Publications must be located in the data_pdf/ directory, and their names must contain the .pdf extension.
The result of each pdf analysis is a .tei.xml file. 
To recover the plain text from these files, a parser is run automatically after the Grobid analysis: the .tei.xml files will be parsed to recover the raw text of the publications. The abstract and the body will be stored in a JSON file.

The .tei.xml files are available in the data_tei_xml/ directory.
The .json files containing the plain texts are available in the data_json/ directory.
If extraction errors are detected, they will be saved in the error file grobid_errors.txt.

