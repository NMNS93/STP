#!/usr/bin/env python3

"""
uniformity.py

Analyse MRI quality assurance images following the UCLH medical physics SOP MPB139 "Uniformity" protocol.

Usage: uniformity.py [-h] [--version] [-o outdir] [-c config] [-i indir]

Version: 1.0
Author: Nana Mensah <Nana.mensah1@nhs.net>
Created: 30th April 2018
"""

import argparse
import configparser
import collections
import logging
import cv2
import csv
import os
import re
import sys
import matplotlib.pyplot as plt
import pydicom
import numpy as np

def cli(args):
    """Configure argument parser."""
    parser = argparse.ArgumentParser(description='Rename MRI quality assurance images following UCLH '+
        'medical physics SOP MPB138 (QA ImageHandling)')
    parser.add_argument('-v, --version', action='version', version='{} v1.0'.format(parser.prog))
    parser.add_argument('-i', type=str, metavar='indir', help='Directory containing DICOM files')
    parser.add_argument('-o', type=str, metavar='outdir', help='output directory name')
    parser.add_argument('-c', type=str, metavar='config', help='config file containing filename regular expressions')
    return parser.parse_args(args)

class UniformityQA(object):
    """Analyse MRI images according to SOP MB139 Uniformity Protocol.

    Attributes:
        indir: Input directory containing uniformity images
        config: Config file object created by parsing the a config file with configparser.Configparser().
        files: List of tuples for each uniformity dicom file in the input directory.
            Format: [(file_prefix, file_path, pydicom_object), ...]

    """

    def __init__(self, indir, outdir, config):
        """Initialise object with input directory and configuration file.

        Args:
            indir: Input directory containing uniformity images
            config: config.ini file containing regular expression for uniformity file
        """ 
        self.indir = indir
        self.config = configparser.ConfigParser()
        self.config.read(config)
        self.files = self.uniformity_files(self.indir)
        self.logger = logging.getLogger('mriqa.uniformityObject')
        self.outdir = outdir

        # Run Uniformity QA protocol
        for UniformityTuple in self.files:
            self.logger.info('Reading file: {}'.format(UniformityTuple.filename))
            uniformity_stats = self.measure(UniformityTuple.filename, UniformityTuple.pydicom.pixel_array)
            self.write(uniformity_stats)

    def uniformity_files(self, indir):
        """Find the filenames and absolute paths of uniformity images in the input directory.
        Args:
            indir: Directory containing uniformity DICOM images. Uniformity images are recognised by
            a regular expression in the 'config.ini' file under the keys [analysis][UNIFORMITY].
        Returns:
            A list of namedtuples mapping filenames, absolute filepaths and dicom objects. For example:
            (('hd_uni_cor', 'C:\\User\\hd_uni_cor.dcm', <class 'pydicom.dataset.FileDataset'>), ...)"""
        
        # Get the uniformity regular expression string from the config file object
        uniformity_regex = self.config['analysis']['UNIFORMITY']

        # Initialise a named tuple to store individual dicom file data
        UnifFiles = collections.namedtuple('uniformity_files',['filename','abspath','pydicom'])
        # Initialise a list to store uniformity file tuples. This list is returned by the function.
        file_data_tuples = []

        # Loop through the input directory file tree 
        dirtree = os.walk(os.path.join(indir, 'renamed'))
        for path,dirs,filenames in dirtree:
            # For every file in the input directory
            for filename in filenames:
                # Add details to uniformity_files if valid uniformity DICOM file.
                try:
                    fname = os.path.basename(os.path.splitext(filename)[0])
                    fullpath = os.path.abspath(os.path.join(path, filename))
                    pydicom_object = pydicom.dcmread(fullpath)
                    # Add file data to list of tuples returned by function if filename matches 
                    # uniformity regular expression.
                    if re.match(uniformity_regex, filename, re.IGNORECASE):
                        file_data_tuples.append(UnifFiles(fname, fullpath, pydicom_object))
                # Skip if the input file is not DICOM format.
                except(pydicom.errors.InvalidDicomError):
                    pass
        return file_data_tuples

    def phantom_midpoint(self, image):
        """Return midpoint of the largest contour in an image, along with contour object
        Args:
            image: A numpy array containing grayscale image data.
        Returns:
            (x, y, contour) where x,y are coordinates of largest contour midpoint.
        """
        # Write and read image for processing. Pydicom reads images as dtype uint16, however OpenCV
        # requires uint8 format for contour identification. This write-read process achieves that.
        tempfile = os.path.join(self.outdir, '__temp.png')
        cv2.imwrite(tempfile, image)
        image_8bit = cv2.imread(tempfile, 0)
        # Threshold image for contouring
        ret,thresh = cv2.threshold(image_8bit,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # Get contours.
        im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        # Select contour with the highest area.
        img_contour = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        # Return the midpoint of the contour, calculated from cv2.moments()
        M = cv2.moments(img_contour)
        midx, midy = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
        return(midx, midy, img_contour)

    def measure(self, filename, pydicom_image):
        """Return measurement statistics from an MRI image for uniformity analysis.
        Arguments:
            filename - String containing the output filename prefix
            pydicom_image -  Numpy array (uint16) from pydicom.dcmread()
        Returns:
            A dict containing QA measurements from the input pydicom image.
            Keys: filename, dimensions, midpoint, central_roi_mean, vertical_roi_profile, 
                fraction, fraction uniformity
        """

        # Calculate the midpoint of the phantom in the DICOM image.
        midx, midy, contour = self.phantom_midpoint(pydicom_image)

        # Calculate the central ROI mean
        # For top-left (x1,y1) and bottom-right (x2,y2) coordinates of a rectangular ROI,
        # ROI = Image[y1:y2, x1:x2] where Image is a numpy array.
        central_roi = pydicom_image[midy-10:midy+10, midx-10:midx+10]
        central_roi_mean = np.mean(central_roi)
        
        # Calculate the vertical ROI profile values
        # Slice the vertical ROI (160x10) from the image
        vertical_roi = pydicom_image[midy-5:midy+5, midx-80:midx+80]
        # Loop through the vertical ROI y-axis values and calculate the averages
        profile_data = ([np.average(vertical_roi[:,i]) for i in range(vertical_roi.shape[1])])

        # Measure the fraction and fraction uniformity
        # Calculate the the aboslute difference between each vertical profile and the central ROI mean.
        abs_dif = list(map(lambda x: abs(x - central_roi_mean), profile_data))
        # Get the fraction count. This is the number of profiles where abs_diff < (profile_mean *0.1)
        fraction = sum([ (diff < (profile*0.1)) for profile, diff in zip(profile_data, abs_dif)])
        fraction_uniformity = fraction/160

        # Calculate horizontal and vertical single line profiles
        horizontal_profile = [pydicom_image[midy,x] for x in range(pydicom_image.shape[1])]
        vertical_profile = [pydicom_image[y, midx] for y in range(pydicom_image.shape[0])]

        # Create and return a dict of relevant QA statistics
        uniformity_stats = {
            "filename": filename, 
            "dimensions": pydicom_image.shape,
            "phantom_xy": (midx, midy),
            "central_roi_mean": central_roi_mean,
            "fraction": fraction,
            "fraction_uniformity": fraction_uniformity,
            "vertical_roi_profile": profile_data,
            "horizontal_sl_profile": horizontal_profile,
            "vertical_sl_profile": vertical_profile,
            "image": pydicom_image,
            "contour": contour
            }

        return uniformity_stats

    def write(self, stats):
        """Generate plots and tables for uniformity QA report.
        Args:
            stats: A dictionary of image QA measurements returned by UniformityQA.measure(). 
        """
        # Generate a plot of the image with ROIs drawn
        tempfile = os.path.join(self.outdir, '__temp.png')
        cv2.imwrite(tempfile, stats["image"])
        ROI_image = cv2.imread(tempfile, 0)
        midx, midy = stats["phantom_xy"]
        contour = stats["contour"]
        cv2.rectangle(ROI_image, (midx-10,midy-10), (midx+10, midy+10), (255,255,255), 1)
        cv2.rectangle(ROI_image, (midx-80,midy-5), (midx+80, midy+5), (255,255,255), 1)
        cv2.line(ROI_image, (midx, 0), (midx, ROI_image.shape[1]), (255,0,0), 1)
        cv2.line(ROI_image, (0, midy), (ROI_image.shape[1], midy), (255,0,0), 1)
        cv2.drawContours(ROI_image, [contour], 0, (255,255,255), 1)
        ROI_outfile = os.path.join(self.outdir, (stats['filename'] + '_imageROIs.png')) 
        cv2.imwrite(ROI_outfile, ROI_image)

        # Draw charts for each of the uniformity profiles
        for profile in [key for key in stats.keys() if key.endswith('profile')]:
            plt.plot(stats[profile])
            plot_outfile = os.path.join(self.outdir, (stats['filename'] + '_' + profile + '.png'))
            plt.savefig(plot_outfile)
            plt.gcf().clear()

        # Set output CSV file path and check if it exists
        stats_outfile = os.path.join(self.outdir, 'uniformity_stats.csv')
        outfile_bool = os.path.isfile(stats_outfile)
        # Write out QA data using CSV writer
        with open(stats_outfile, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=stats.keys())
            if not outfile_bool:
                writer.writeheader()
                writer.writerow(stats)
            else:
                writer.writerow(stats)


def main(args):
    # Setup logging. Calls to logger.info('string') will print 'string' to the console.
    logger = logging.getLogger('mriqa.uniformity')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info('Running uniformity analysis')

    # Initialise uniformity object with input, output and config from args
    opts = cli(args)

    # Create output directories required
    outdir = os.path.join(opts.i, 'uniformity')
    try:
        os.mkdir(outdir)
    except FileExistsError:
        sys.stderr.write('ERROR: Previous uniformity analysis detected, please remove: "{}" or rename'.format(outdir))
        exit()

    # Run Uniformity QA protocol
    UniformityQA(opts.i, outdir, opts.c)
    logger.info('Uniformity protocol complete')


if __name__ == '__main__':
    main(sys.argv[1:])