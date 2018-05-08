# UCLH Medical Physics MRI QA File Handler
**v1.0**

The UCLH Medical Physics department performs MRI phantom scans for quality assurance testing. This script processes a directory of QA images in DICOM format for downstream testing using the following protocol:
1. Read the SeriesDescription field from each DICOM file header. This field is filled manually by the Clinical Scientist at the time of the MRI scan.
2. Validate the SeriesDescription for use as the DICOM filename, according to the filename conventions in SOP MPB138\_QA\_ImageHandling.
3. If valid, rename file and copy to the output directory.
4. Copy invalid files to the subdirectory 'unnamed'of the output directory.

# Installation
python setup.py install

# Usage
The script `mriqa` is called from the command line. It is designed to contain several modules: 

        usage: mriqa [module] [opts]
        modules: mpb138

## mpb138
This module is called and given an input directory containing DICOM files to process. 
An optional output directory name can be given with the flag `-o`. All DICOM SeriesDescriptions are 
validated against regular expressions found in 'config.ini' in the script's. The following outputs are produced:
- Output directory (default: 'mri\_qa\_images') contains renamed DICOM files and a sub-directory ('unnamed') containing files with invalid SeriesDescriptions.

        usage: mriqa [-h] [-v, --version] [-o outdir] [-c config] indir
        
        positional arguments:
          indir          Directory containing DICOM files
        
        optional arguments:
          -h, --help     show this help message and exit
          -v, --version  show program's version number and exit
          -o outdir      output directory name
          -c config      config file containing filename regular expressions

