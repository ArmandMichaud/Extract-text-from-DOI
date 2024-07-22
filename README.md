
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

### General dependencies 

Bash, apt, Git, Python 3.7 or higher (in a venv).


### Grobid Installation

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

### BERN2 Installation
You first need to install BERN2 and its dependencies.

Install torch with conda (please check your CUDA version)
```bash
conda create -n bern2 python=3.7
conda activate bern2
conda install pytorch==1.9.0 cudatoolkit=10.2 -c pytorch
conda install faiss-gpu libfaiss-avx2 -c conda-forge
```

Check if cuda is available
```bash
python -c "import torch;print(torch.cuda.is_available())"
```

Install BERN2
```bash
git clone git@github.com:dmis-lab/BERN2.git
cd BERN2
pip install -r requirements.txt
```

Then, you need to download resources (e.g., external modules or dictionaries) for running BERN2. Note that you will need 70GB of free disk space. 
```bash
wget http://nlp.dmis.korea.edu/projects/bern2-sung-et-al-2022/resources_v1.1.b.tar.gz
tar -zxvf resources_v1.1.b.tar.gz
md5sum resources_v1.1.b.tar.gz
```

make sure the md5sum is 'c0db4e303d1ccf6bf56b42eda2fe05d0'
```bash
rm -rf resources_v1.1.b.tar.gz
```

install CRF 
```bash
cd resources/GNormPlusJava
tar -zxvf CRF++-0.58.tar.gz
mv CRF++-0.58 CRF
cd CRF
./configure --prefix="$HOME"
make
make install
cd ../../..

conda deactivate 
```

## Software Installation

Warning: Once the software is installed, do not modify the hierarchical structure of the software files!

```bash
git clone https://github.com/ArmandMichaud/Extract-text-from-DOI Extract-text-from-DOI
cd Extract-text-from-DOI
```

to extract images, you need PyMuPDF : 

```bash
pip install PyMuPDF
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

Parse the json file obtained with the Aniseed api to obtain a text file containing a list of DOIs

```python
python script_python/extract_doi_from_json_aniseed.py publications_aniseed.json doi_aniseed.txt
```


### PMIDs to DOIs

The PMIDtoDOI.py script reads a text file containing a list of PMIDs, then, using the NCBI api, converts them into DOIs. Some publications may not have a DOI, in which case they will be listed in a log file contained in /logs/errors_extract_doi_from_pmid.txt.

To run the script, you need to enter two parameters, the PMIDs file as input, and the DOIs file as output. 

```python
python script_python/PMIDtoDOI.py PMIDs_input.txt doi.txt
```


### Retrieval of scientific publications in PDF format using Sci-Hub

import a text file containing the DOI numbers of the publications you want to extract.  
There's a doi.txt file as an example file type.  
To run the extraction, you need to specify the txt file containing the DOI list as an argument:  

```bash
bash extract_publi_scihub.sh doi.txt
```

Publications will be saved in the data_pdf/ folder, with the DOI number as their name, replacing the replacing the '/' with '%2F', the '<' with '%3C', the '>' with '%3E', the ':' with '%3A' and the ';' with '%3B'. 
Some publications may not be available on Sci-Hub. Their names will be noted in the file "error_extract_scihub.txt".  
You can manually add publications to be analysed, or publications that could not be extracted with Sci-Hub, simply by adding them to the data_pdf/ folder.  

### Grobid

#### Launch Grobid
Before using Grobid, make sure to run Grobid locally. The following command (same as installation) launches the software in the terminal:  
```bash
sudo docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.0&
```
Make sure the port 8070 is open and accessible.  
To stop Grobid, kill the corresponding PID.  
NB on TensorFlow and GPU:  (ToDo)  
(TODO) Configure and Run Grobid as a service  


#### Grobid analysis 
You may need to install requests first: `pip install requests`  

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

### Extraction of figures 

From the grobid analysis, it is also possible to extract the figures from the coordinates retrieved from the tei.xml files. 
Taking the tei.xml files and the pdf folder as input, an analysis will generate a folder containing all the images, and an openable html file containing all the figures in the pdf with their legends. 
The folder containing the tei.xml files should be called data_tei_xml and the folder containing the pdf files should be called data_pdf. Output will be in the data_figure_html folder. 


To start figure extraction : 

```bash
python script_python/extract_figure.py
```

### BERN2

BERN2 (Advanced Biomedical Entity Recognition and Normalization) is 'a tool that improves the previous neural network-based NER tool by employing a multi-task NER model and neural network-based NEN models to achieve much faster and more accurate inference.'

BERN2's git at the following link: [BERN2](https://github.com/dmis-lab/BERN2/blob/main/README.md)
 

#### Running BERN2

The minimum memory requirement for running BERN2 on GPU is 63.5GB of RAM & 5.05GB of GPU. The following command runs BERN2.

```bash
conda activate bern2
export CUDA_VISIBLE_DEVICES=0
cd scripts

bash run_bern2.sh
```

(Optional) To restart BERN2, you need to run the following commands.

```bash
export CUDA_VISIBLE_DEVICES=0
cd scripts
bash stop_bern2.sh
bash run_bern2.sh
```

#### Using BERN2

After successfully running BERN2 in your local environment, you can access it via RESTful API.
Input data must be in json format and located in data_json. Output data will be stored in the data_bern2 folder.

```bash
conda activate bern2
python3 script_python/bern2_analyse.py 

```


### 
 




