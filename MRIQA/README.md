# MRI Quality Assurance

Software for performing UCLH Medical Physics MRI Quality Assurance (QA) protocols on DICOM images. Protocols are defined in the SOPS MPB 138 (Image Handling) and MPB 139 (Image Analysis).

## Installation
### Linux terminal
Install (miniconda)[https://conda.io/miniconda.html]. Run the following commands from a clone of this repository:
```
conda create --name mriqa_env python=3.6
conda activate mriqa_env
pip install -r requirements.txt
```

## Usage

### mriqa.py
Wrapper script for the MRI QA software modules. Passes command line arguments to the relevant modules. Used by the graphical user interface to run the software.
```
usage: mriqa.py [-h] module args

optional arguments:
  module      name of MRI quality assurance module to run: all, rename
  args        command line arguments to be passed to downstream module: 
  	-i indir	directory containing DICOM files
  	-c config	config file containing filename regular expressions for validating Series Description
  -h, --help  show this help message and exit
  -v          show program's version number and exit
```

## Modules
The modules below can be run stand-alone. All modules with the exception of `gui.py` take the 'args' arguments described above.

### gui.py
Generates the graphical user interface for the MRI QA software.

### rename.py
Rename DICOM images by validating strings in the DICOM Series Description tag.

## Development

### Updating the GUI
TBD

### Adding new modules
TBD

### TODO
* Add appropriate logging statements for functions and write logs to output file.
* Retain only relevant columns in the uniformity output CSV files.
* Get the vertical uniformity of the MRI images
* Add the option to add a config.ini file to the GUI
* Create a windows executeable using py2exe
