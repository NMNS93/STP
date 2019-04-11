"""Tests for lrg_parser"""
import os, subprocess, difflib, time, sys
import xml.etree.ElementTree as ET
import pytest
import requests
import lrg_parser

def test_BED():
    """Assert that output file is in BED format (tab-delimited records)."""
    # Get list of files/directories in 'data/'. Used to get output file name after calling lrg_parser.py on data/LRG_1.xml
    old_env = os.listdir('data')
    sys.argv = ['lrg_parser.py', 'data/LRG_1.xml']
    # Generate output BED for LRG_1.xml
    lrg_parser.main()
    new_env = os.listdir('data')
    # Get BED file name
    output_file_name = [ filename for filename in new_env if filename not in old_env ][0]
    output_file_path = os.path.join('data',output_file_name)
    # Read output BED as list
    with open(output_file_path, 'r') as output_file:
        BED_lines = output_file.readlines()
    # Assert output file is compliant with BED file format: 
    #   - Minimum of three input fields separated by tabs
    #   - Records separated by new lines
    for line in BED_lines:
        assert len(line.split('\t')) >= 3
        assert line.endswith('\n')
    # Delete generated BED file
    os.remove(output_file_path)


def test_convert_lrg1():
    """Assert LRG_1 exon regions are accurately converted to GRCh38.p12 coordinates"""
    # LRG_1 coordintates
    lrg1_root = lrg_parser.set_root(lrg_parser.parse_file('data/LRG_1.xml'))
    lrg1_exon_data_tuple = (lrg_parser.lrg_parse(lrg1_root))
    lrg1_coordinates = lrg_parser.convert_coords(lrg1_root, lrg1_exon_data_tuple)
    lrg1_coords_truthset_wheaders = [ tuple(line.strip().split(",")) for line in open('data/LRG_1_GRCh38_p12_coordinates.csv','r').readlines() ]
    # Remove lines from truthset file that start with '#'. These lines contain headers of the truthset columns
    lrg1_coords_truthset = list(filter(lambda x: not x[0].startswith('#'), lrg1_coords_truthset_wheaders))
    for index in range(len(lrg1_coords_truthset)):
        assert lrg1_coordinates[index][1] == lrg1_coords_truthset[index][1]
        assert lrg1_coordinates[index][2] == lrg1_coords_truthset[index][2]

def test_convert_lrg5():
    """Assert LRG_5 exon regions are accurately converted to GRCh38.p12 coordinates"""
    lrg5_root = lrg_parser.set_root(lrg_parser.parse_file('data/LRG_5.xml'))
    lrg5_exon_data_tuple = (lrg_parser.lrg_parse(lrg5_root))
    lrg5_coordinates = lrg_parser.convert_coords(lrg5_root, lrg5_exon_data_tuple)
    lrg5_coords_truthset_wheaders = [ tuple(line.strip().split(",")) for line in open('data/LRG_5_GRCh38_p12_coordinates.csv','r').readlines() ]
    # Remove lines from truthset file that start with '#'. These lines contain headers of the truthset columns
    lrg5_coords_truthset = list(filter(lambda x: not x[0].startswith('#'), lrg5_coords_truthset_wheaders))
    print(lrg5_coordinates)
    for index in range(len(lrg5_coords_truthset)):
        assert lrg5_coordinates[index][1] == lrg5_coords_truthset[index][1]
        assert lrg5_coordinates[index][2] == lrg5_coords_truthset[index][2]

def test_parse_lrg1():
    """Test that all expected exon labels are parsed from LRG files."""
    # Get exons for LRG 1
    lrg1_root = lrg_parser.set_root(lrg_parser.parse_file('data/LRG_1.xml'))
    lrg1_exon_data_tuple = (lrg_parser.lrg_parse(lrg1_root))
    # Exon labels are the first element of each tuple in returned by lrg_parser.lrg_parse(). 
    # zip() is used to merge the tuples by matching element indexes. e.g.:
    #     a = [(1,2,3), (4,5,6)]
    #     zip(*a) = [(1,4), (2,5), (3,6)]
    lrg1_exons = list(zip(*lrg1_exon_data_tuple))[0]
    # Get exon label truthset from local data
    lrg1_truthset = open('data/LRG1_exons.list', 'r').read().split(",")
    assert set(lrg1_exons) == set(lrg1_truthset)

def test_parse_lrg5():
    """Test that all expected exon labels are parsed from LRG files."""
    # Get exons for LRG 5
    lrg5_root = lrg_parser.set_root(lrg_parser.parse_file('data/LRG_5.xml'))
    lrg5_exon_data_tuple = (lrg_parser.lrg_parse(lrg5_root))
    lrg5_exons = list(zip(*lrg5_exon_data_tuple))[0]
    # Get exon label truthset from local data
    lrg5_truthset = open('data/LRG5_exons.list', 'r').read().split(",")
    assert set(lrg5_exons) == set(lrg5_truthset)

def test_write():
    """Test that it writes a file with the correct name """
    # write_file function writes the data to a file
    lrg_parser.write_file('data', 'LRG_1.xml')
    # Test that a file was output with the correct name (LRG_num_date.bed)
    date_today = time.strftime('%Y%m%d')
    assert os.path.isfile('LRG_1_'+date_today+'.bed')
    os.remove('LRG_1_'+date_today+'.bed')

def test_length():
    """Test that the automatically downloaded XML using the script
    and a manually downloaded XML for the same LRG are the same 
    length. We assume it is unlikely that different LRG files will
    be exactly the same length"""
    # open file downloaded manually, stored in 'data' directory
    with open('data/LRG_1.xml', 'r') as file_1:
        f1 = file_1.read()
    # get_file gets the xml data from web as a string
    f2 = lrg_parser.get_file('LRG_1')
    # check that the strings are exactly the same length
    assert len(f1) == len(f2)

def test_LRG_input():
    """Test that if the input is an existing file, parse_file outputs
    it as a string"""
    data = lrg_parser.parse_file('data/LRG_1.xml')
    assert isinstance(data, str)

def test_set_root_from_file():
    """Test that the xml data string objects are converted to root 
    objects for parsing for file inputs"""
    root = lrg_parser.set_root(lrg_parser.parse_file('data/LRG_1.xml'))
    assert isinstance(root, ET.Element)

def test_set_root_from_name():
    """Test that the xml data string objects are converted to root 
    objects for parsing for LRG number inputs"""
    root = lrg_parser.set_root(lrg_parser.get_file('LRG_1'))
    assert isinstance(root, ET.Element)
