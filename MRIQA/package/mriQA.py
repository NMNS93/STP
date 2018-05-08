import argparse
import configparser
import logging
import logging.config
import os
import pydicom
import re
import shutil
import sys
import itertools

#TODO:
#-Write tests for: 0 DCM images, non DCM file, strings in and out of fnames, 
#   output directory errors, unnamed directory with log file creation.

#-Package the script as a python module, install (write installation to readme) and test on windows machine.
#-Place script and files in a github repo
#-Check EU medical devices directive for software
#-Make any remaining changes
#-See magda


class RenameQA(object):
    """Rename MRI QA DICOM files according to SOP MPB138."""
    def __init__(self, indir, outdir, unnmdir, config):
        """Intialise directories and call self.process() to process DICOM files."""

        # Create loggers for console and log file messages
        self.logger = logging.getLogger('RenameQA')
        self.unnamed_log = logging.getLogger('unnamed')
        self.logmain = logging.getLogger('main')

        # Set the directory paths
        self.indir = indir
        self.outdir = outdir
        self.unnmdir = unnmdir

        # Make the filename config object available to class functions
        self.config=config
        # Create a combined list of all DICOM filename regular expressions given in config
        self.FNAMES = set(itertools.chain.from_iterable(
                [config['regex'][i].strip("'").split(',') for i in config['regex']]
                ))
        self.logger.info('Regular expressions from read from config:\n{}'.format(self.FNAMES))
        
        # Set counter for DICOM files processed and files found
        self.dcm_count = 0
        self.file_count = 0
        self.dcm_rename_count = 0
        # Process all DICOM images within the input directory
        self.logger.info('Processing DICOM files in {}'.format(self.indir))
        for dcm_file in self.abspath(self.indir, [os.path.basename(self.outdir)]):
            self.file_count += 1
            self.process(dcm_file)
        # Report number files processed
        self.logmain.info('Found {} files. Renamed {}/{} DICOM files'.format(self.file_count, self.dcm_rename_count, self.dcm_count))

    def abspath(self, indir, ignoredirs):
        """Return the absolute path for all files in the given directory."""
        # Filter dirtree (os.walk()) by all paths not containing a string in the ignoredir list
        dirtree = filter(lambda tree: 
            all(
                map(lambda string: string not in tree[0], ignoredirs)
                ), os.walk(indir)
            )
        # Yield the paths for all files in the directory
        for path,dirs,filenames in dirtree:
            for f in filenames:
                    yield os.path.abspath(os.path.join(path, f))

    def process(self, infile):
        """Validate and rename DICOM files."""
        # Attempt to read the file as a DICOM image
        try:
            dcm = pydicom.dcmread(infile)
            self.dcm_count += 1
        # Return None if the input file is not DICOM format.
        except(pydicom.errors.InvalidDicomError):
            return None

        # Store the series description
        desc = dcm.SeriesDescription.lower()

        # If the Series Description matches any regular expression in FNAME
        if any([ re.match(regex, desc, flags=re.IGNORECASE) for regex in self.FNAMES ]):
            # If the SeriesDescription indicates a slice position file prefix the current filename with the SeriesDescription
            if re.match(self.config['regex']['SLI_POS'].strip("'"), desc, flags=re.IGNORECASE):
                outfile = desc + "_" + os.path.basename(infile)
            # Else set the output filename for all other files to the entire SeriesDescription
            else:
                outfile =  desc + ".dcm"
            # Copy input DICOM to output directory and rename
            shutil.copy(infile, os.path.join(self.outdir, outfile))
            self.logger.info('Successfully renamed {} to {}'.format(infile, outfile))
            self.dcm_rename_count += 1

        else:
            # Copy unnamed DCM file to 'unnamed' directory
            shutil.copy(infile, self.unnmdir)
            # Write details to unnamed directory log
            self.unnamed_log.warning('Unnamed (file,SeriesDescription): {},{}'.format(os.path.basename(infile), desc))