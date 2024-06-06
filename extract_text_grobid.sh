#!/bin/bash

mkdir -p data_tei_xml
mkdir -p data_json

echo "Start of Grobid analysis";
#python3 script_python/grobid_analyse.py 
echo "Grobid analysis complete";

echo "Start parsing .tei.xml files";
python3 script_python/grobid_parsing.py 
echo "Parsing of .tei.xml files completed";
echo "The .tei.xml files are available in the data_tei_xml directory.";
echo "The .Json files containing the plain text are available in the data_json directory.";


