#!/usr/bin/env python3

"""
mpb138

Automate the protocol for image handling in the UCLH medical physics MRI department. For details of 
the protocol, see SOP MPB138_QA_ImageHandling.

Usage: image_handling.py [-h] [--version] [-o outdir] indir

Version: 1.0
Author: Nana Mensah <Nana.mensah1@nhs.net>
Created: 30th April 2018

"""

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

from package import mriQA

def cli(args):
    """Configure argument parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-v, --version', action='version', version='{} v1.0'.format(parser.prog))
    parser.add_argument('indir', type=str, metavar='indir', help='Directory containing DICOM files')
    parser.add_argument('-o', type=str, metavar='outdir', help='output directory name')
    parser.add_argument('-c', type=str, metavar='config', help='config file containing filename regular expressions')
    return parser.parse_args(args)

def manage_dirs(opts, outdir, unnmdir):
    # Create the output directories if they do not exist, else exit if it they do.
    try:
        os.mkdir(outdir)
        os.mkdir(unnmdir)
    except FileExistsError:
        sys.stderr.write('ERROR: Previous analysis detected, please remove: "{}" or rename output with "-o"\n'.format(outdir))
        exit()

def log_setup(outdir, unnmdir):
     # Set logfile names
    logging.image_handling_log = os.path.join(outdir, 'image_handling.log')
    logging.unnamed_log = os.path.join(unnmdir, 'unnamed.log')
    # Load configuration for logging module (stored in logging config file in the script's directory)
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config/log.config')
    logging.config.fileConfig(log_file_path)   


def main(args=None):
    # Get command line arguments
    args = args if args else sys.argv
    print(args)
    opts = cli(args)
    
    # Create directories
    outdir = opts.o if opts.o else 'mri_qa_images'
    unnmdir = os.path.join(outdir, 'unnamed')
    manage_dirs(opts, outdir, unnmdir)

    # Setup logging
    log_setup(outdir, unnmdir)
    # Set main Logger
    logmain = logging.getLogger('main')

    # Configure regular expressions for DICOM filenames from config file
    config = configparser.ConfigParser()
    if opts.c:
        config.read(opts.c)
    else:
        config.read(os.path.join(os.path.dirname((os.path.abspath(__file__))), 'config/config.ini'))

    # Log script run
    logmain.info('Starting script.')
    logmain.info('Input directory is {}, Output directory is {}'.format(opts.indir, outdir))

    # Run protocol
    mriQA.RenameQA(opts.indir, outdir, unnmdir, config)

    # Log output
    logmain.info('MRI QA rename complete.')

if __name__ == "__main__":
    main()