#!/usr/bin/env python3
"""
rename.py

Rename MRI quality assurance images following the UCLH medical physics SOP MPB138 (QA ImageHandling)

Version: 1.0
Created: 30th April 2018
"""

import argparse
import configparser
import itertools
import logging
import os
import re
import shutil
import sys
import pydicom


def command_line_parser(args):
    """Parse command line arguments,
    Args:
        args - A list containing the command line string split by spaces.
    Returns:
        An argparse.ArgumentParser object containing attributes for the input directory and config.
    """
    parser = argparse.ArgumentParser(description='Rename MRI quality assurance images following UCLH '+ 
        'medical physics SOP MPB138 (QA ImageHandling)')
    parser.add_argument('-i', type=str, metavar='indir', help='Directory containing DICOM files', required=True)
    parser.add_argument('-c', type=str, metavar='config', help='config file containing filename regular expressions', required=True)
    parser.add_argument('-v', action='version', version='{} v1.0'.format(parser.prog))
    return parser.parse_args(args)

def manage_dirs(opts):
    """Create the output directories if they do not exist, else exit if it they do.
    Args:
        opts - An argparse.ArgumentParser object with an attribute for the input directory (opts.i).
    Returns:
        A tuple with the full paths of the new directories in the format (renamed_directory, unnamed_directory)
    """
    # Set the directory for renamed and unnamed dicom files respectively
    renamed_dir = os.path.join(opts.i, 'renamed')
    unnamed_dir = os.path.join(opts.i, 'unnamed')
    # Create directories and return
    try:
        os.mkdir(renamed_dir)
        os.mkdir(unnamed_dir)
        return(renamed_dir, unnamed_dir)
    # Exit if directories exist
    except FileExistsError:
        sys.stderr.write('ERROR: Previous analysis detected, please remove: "{}" or rename output with "-o"\n'.format(renamed_dir))
        exit()


class RenameQA(object):
    """Rename MRI QA files as outlined in SOP MPB138.
    Ars:
        indir - Input directory
        outdir - Output directory
        unnmrdir - Directory for unnamed files
        config - A configparser.ConfigParser() object that has read the config.ini input file
    """

    def __init__(self, indir, outdir, unnmdir, config):
        # Create class instance of the console logger
        self.logger = logging.getLogger('mriqa.rename.RenameQA')

        # Set the directory paths and config object for a class instance
        self.indir = indir
        self.outdir = outdir
        self.unnmdir = unnmdir
        self.config=config

        # Create a combined list of all DICOM filename regular expressions from the config object
        self.logger.debug(config.sections())
        self.FNAMES = set(itertools.chain.from_iterable(
                [config['regex'][row].split(',') for row in config['regex']]
                ))
        
        # Set counters for files processed
        self.dcm_count = 0 # Dicom files found
        self.file_count = 0 # All files found
        self.dcm_rename_count = 0 # Dicom files renamed

        # Loop through all files in the input directory and call process() on the file
        self.logger.info('Processing DICOM files in {}'.format(self.indir))
        for dcm_file in self.filepath(self.indir):
            self.file_count += 1
            self.process(dcm_file)
        # Report number files processed
        self.logger.info('Found {} files. Renamed {}/{} DICOM files'.format(self.file_count, self.dcm_rename_count, self.dcm_count))

    def filepath(self, indir):
        """Return the absolute path for all files in the given directory.
        Args:
            indir - Input directory
        """
        # Filter dirtree (os.walk()) by all paths not containing a string in the ignoredir list
        dirtree = os.walk(indir)

        # Loop through directroy tree
        for path,dirs,filenames in dirtree:
            for f in filenames:
                    # Print file if path does not match output directory or unnamed file directory
                    # Stops the search accessing files that have already been processed
                    if all(map(lambda dir: path != dir, [self.outdir, self.unnmdir])):
                        yield os.path.abspath(os.path.join(path, f))

    def copy_unnamed(self, infile):
        """Copy files to the directory set to self.unnmdir
        Args:
            infile - A file which is unable to be renamed by the script
        """
        # Copy file to the unnamed directory
        shutil.copy(infile, self.unnmdir)
        # Write details to console log
        self.logger.warning('Unnamed (file,SeriesDescription): {}'.format(os.path.basename(infile)))        

    def process(self, infile):
        """Validate and rename DICOM files.
        Args: 
            infile - A file to be processed for renaming
        """
        # Attempt to read the file as a DICOM image
        try:
            dcm = pydicom.dcmread(infile)
            self.dcm_count += 1
        # Return None if the input file is not DICOM format.
        except(pydicom.errors.InvalidDicomError):
            return None

        # Attempt to store the series description
        try: 
            desc = dcm.SeriesDescription.lower()
        # If the dicom file does not contain a tag for SeriesDescription, copy to the 'unnamed' directory
        except AttributeError:
            self.copy_unnamed(infile)

        # If the Series Description matches a regular expression in the config file (self.FNAMES)
        if any([ re.match(regex, desc, flags=re.IGNORECASE) for regex in self.FNAMES ]):
            # If the match is for a slice position file, prefix the current filename with the SeriesDescription
            if re.match(self.config['regex']['SLI_POS'].strip("'"), desc, flags=re.IGNORECASE):
                outfile = desc + "_" + os.path.basename(infile)
            # Else set the output filename to the DICOM SeriesDescription
            else:
                outfile =  desc
            # Copy input DICOM to output directory and rename
            shutil.copy(infile, os.path.join(self.outdir, outfile))
            self.dcm_rename_count += 1
        else:
            # Copy unnamed DCM file to 'unnamed' directory
            self.copy_unnamed(infile)

def main(args):
    """
    Run MRI QA rename protocol.
    Args:
        args - A list containing the command line string split by spaces.
    """
    # Setup logging. Calls to logger.info('message') will print 'message' to the console.
    logger = logging.getLogger('mriqa.rename')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Get command line arguments
    opts = command_line_parser(args)
    
    # Create directories for renamed and unnamed files respectively
    outdir, unnmdir = manage_dirs(opts)

    # Read regular expressions for DICOM filenames from the config file
    config = configparser.ConfigParser()
    config.read(opts.c)

    # Run MRI file rename protocol using the RenameQA class.
    logger.info('BEGIN')
    logger.info('Input directory is {}, Output directory is {}'.format(opts.i, outdir))
    RenameQA(opts.i, outdir, unnmdir, config)
    logger.info('MRI QA rename complete.')

if __name__ == "__main__":
    main(sys.argv[1:])