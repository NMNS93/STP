# lrg_parser v1.0
*Created by: Jes Adams (jadams8) and Nana Mensah (nmns93)*  
Developed in accordance to the Association for Clinical Genetic Sciences' guidelines for development and validation of software. Available at: http://www.acgs.uk.com/media/1025075/ngs_bioinformatics_bpg_final_version_2016.pdf

## About
Generate BED file from LRG XML files using exon coordinates. Two inputs are accepted by the script in any combination:
* LRG files in XML format.
* An LRG number, e.g. `LRG_5`. XML files are retrieved from the API for these inputs.

Output files are written to the current working directory if the LRG record is downloaded from the internet. Otherwise, output files are written to the same path as the given input file. To name the BED file, lrg_parser.py removes file extensions from the input and appends a timestamp in Year-Month-Day format:
> lrg_parser.py LRG_1.xml ---> LRG_1_20181211.bed

## Installation
### Unix command line
```
git clone https://github.com/jadams8/lrg_parser.git
cd lrg_parser
pip install -r requirements.txt
export PATH=$PATH:$(pwd) # Add to ~/.bashrc for access from every terminal session
```

### Testing
Tests are run with the pytest library using the following command:
```
pytest lrg_parser/tests.py
```

## Limitations
* Tested with python version 3.6 only.
* Requires an internet connection to install dependencies listed in *requirements.txt*.
* Not tested on Microsoft Windows platforms.

## Usage
```
lrg_parser.py [-h] xml_file [xml_file ...]

Parse an XML file to produce a BED file

positional arguments:
  xml_file    Enter the names of the LRG file to parse

optional arguments:
  -h, --help  show this help message and exit
```
