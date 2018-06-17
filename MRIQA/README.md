# MRI Quality Assurance

Software for running UCLH Medical Physics MRI Quality Assurance protocols on DICOM images.
The protocols are defined in the SOPS MPB 138 (Image Handling) and MPB 139 (Image Analysis).

*Not validated for clinical use*

## Modules
### rename.py
Renames DICOM images by validating strings in the DICOM Series Description tag.
```
usage: rename.py [-h] -i indir -c config [-v]
optional arguments:
  -h, --help  show this help message and exit
  -i indir    directory containing DICOM files
  -c config   config file containing filename regular expressions for validating Series Description
  -v          show program's version number and exi
```