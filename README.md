
# Software Documentation

## Introduction

This software aims at conducting biological entity analysis in scientific publications. 
The software takes DOI numbers of publications as input data but allows starting the analysis pipeline at various stages. 

The stages are as follows:
- Obtain the PMIDs of scientific articles present in NCBI 
- Extract the PMIDs from the Json file obtained with the Aniseed API (https://aniseed.fr/api)
- Obtain DOIs for each article from PMIDs
- Retrieval of scientific publications in PDF format using Sci-Hub
- Grobid analysis (standardization of publications) for content and structure extraction of scientific publications (output in tei.xml format)
- Parsing of generated tei.xml files to retrieve the abstract and body text of publications (output in Json format)


- Biological entity search using Bern2 (not yet done)

## Prerequisites

### GIT

You must have git to clone all the files

### Python

Runs on versions of python 3.7 and higher

### Grobid Installation

You must have Docker installed: [Docker Installation Guide](https://docs.docker.com/desktop/install/ubuntu/)

```bash
sudo apt-get update
sudo apt install docker.io
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
git clone https://github.com/ArmandMichaud/Extract-text-from-DOI Extract-text-from-DOI
cd Extract-text-from-DOI
```

## Using the Software

### Retrieving PMIDs from NCBI

The script generates a list of PMIDs in a txt file containing the list of publications found in the PubMed database (https://pubmed.ncbi.nlm.nih.gov/). The search criterion is the first parameter, the name of the output file the second. 

```python
python script_python/getPMID_from_NCBI.py "tunicata" PMIDs_output.txt
```

It is also possible to perform this step on the PubMed site in order to save a more refined search. 
- Go to pubmed (https://pubmed.ncbi.nlm.nih.gov/)
- Do your research
- Click on Save, choose the selection and set in PMID format
- Click on Create file and save it in this folder 

### Retrieving PMIDs from Aniseed

Json file parser obtained by the Aniseed api 



### PMIDs to DOIs

The PMIDtoDOI.py script reads a text file containing a list of PMIDs, then, using the NCBI api, converts them into DOIs. Some publications may not have a DOI, in which case they will be listed in a log file contained in /logs/errors_extract_doi_from_pmid.txt.

To run the script, you need to enter two parameters, the PMIDs file as input, and the DOIs file as output. 

```python
python script_python/PMIDtoDOI.py PMIDs_input.txt doi.txt
```

### Retrieval of scientific publications in PDF format using Sci-Hub

import a text file containing the DOI numbers of the publications you want to extract. There's a doi.txt file as an example file type. 
to run the extraction, you need to add the txt file containing the DOI list as an argument :  

```bash
bash extract_publi_scihub.sh doi.txt
```

Publications will be saved in the data_pdf folder. Publications will be saved in the data_pdf folder, with their name containing the DOI number of the publication, replacing the '/' with '%2F', the '<' with '%3C', the '>' with '%3E', the ':' with '%3A' and the ';' with '%3B'. 
A number of publications are not available through Sci-hub. The various publications that have not been found are available in the file error_extract_scihub.txt.
You can manually add publications to be analyzed, or publications that could not be extracted with scihub, simply by adding them to the data_pdf folder.

### Grobid analysis

Before using Grobid, make sure to run Grobid locally. This can be done with the following command (same as installation):

```bash
sudo docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0
```

This launches the software in the terminal. Open another terminal to continue. To stop Grobid, close the terminal where you launched the software. 

to run the Grobid analysis: 

```bash
bash extract_text_grobid.sh
```

Publications must be located in the data_pdf directory, and must have the .pdf extension. If extraction errors are detected, these will be marked in the error file grobid_errors.txt.The result of each pdfs analysis is a .tei.xml file. To recover the plain text in these files, a parser must be used. It is run automatically after Grobid analysis. The .tei.xml files will be parsed to recover the raw text of the publications. The text summary and body will be stored in a Json file.

The .tei.xml files are available in the data_tei_xml directory.
The .Json files containing the plain text are available in the data_json directory.

If there are any errors during text extraction, the problem will be written in the grobid_errors.txt file.



 




