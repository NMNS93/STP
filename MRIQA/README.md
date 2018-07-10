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
  args        command line arguments to be passed to downstream module: -i indir, -c config
  -h, --help  show this help message and exit
  -v          show program's version number and exit
```

## Modules

### gui.py
Generates the graphical user interface for the MRI QA software.

### rename.py
Rename DICOM images by validating strings in the DICOM Series Description tag.
```
usage: rename.py [-h] -i indir -c config [-v]

optional arguments:
  -i indir    directory containing DICOM files
  -c config   config file containing filename regular expressions for validating Series Description
  -h, --help  show this help message and exit
  -v          show program's version number and exit
```

## Development

### Updating the GUI
TBD

### Adding new modules
TBD

### TODO
* Add appropriate logging statements for functions and write logs to output file.
* Retain only relevant columns in the uniformity output CSV files.
* Implement OpenCV convexing of the countour to make the mid-point more accurate. Some phantoms contain air bubbles which should be included in the contour shape.
* Package for use on Windows systems
* Package for use on MacOS systems
