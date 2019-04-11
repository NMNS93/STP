#!/usr/bin/env python3
'''lrg_parser.py

Parse exon regions from an LRG record in XML format to a BED file containing GRCh38 regions
'''
import argparse
import os
import re
import time
import xml.etree.ElementTree as ET

import requests

def parse_file(filename):
	"""Read a local input file as a Python string object."""
	print('File found on system.')
	with open(filename, 'r') as file_data:
		file_string = file_data.read()
	return file_string

def lrg_parse(root):
	"""Gets exons and exon regions from an input root object.

	Args:
	 	root (xml.etree.ElementTree): An ElementTree generated from an LRG file in XML format
	Returns:
	    sorted_data (List[Tuple[str]]): A list of tuples. Each tuple contains an LRG exon label (sorted),
			exon start and exon end values for the input LRG record.
	"""
	exon_tags = []
	# Iterate through each exon tag in the LRG XML record
	for exon in root.iter('exon'):
		# All exons tags describing transcripts have the attribute 'label'.
		if 'label' in exon.attrib.keys():
			exon_tags.append(exon)

	lrg_record_name = list(root.iter('id'))[0].text
	# Create an empty list to append tuples of exon labels and their LRG record regions
	data_list = []
	# Exon tags contain nested coordinate tags with the exon, transcript and protein locations in the LRG record.
	# Get data from the tag for exon regions, which has a 'coord_system' attribute matching the LRG record name.
	for exon in exon_tags:
		for child in exon:
			if lrg_record_name == child.attrib['coord_system']:
				data_to_append = (exon.attrib['label'], child.attrib['start'], child.attrib['end'])
				if data_to_append not in data_list:
					data_list.append(data_to_append)

	# Sort the data according to position in the genome.
	# Records with multiple transcripts have exon label numbers followed by a letter for each transcript.
	# This sorting uses numerical then alphabetical order.
	sorted_data = sorted(data_list, key=lambda line: int(re.split('[A-Za-z]+', line[0])[0]))
	return sorted_data

def write_file(data, file_name):
	"""Writes data to a new file in BED format.

	Args:
		data (List[Tuple[int]]): Data to write in BED format
		file_name (str): File name used to make prefix for output file.
	"""
	output_file_prefix = file_name.split('.')[0]
    # Add current year, month and day to output BED file name
	output_file_name = output_file_prefix + '_' + time.strftime('%Y%m%d') + '.bed'
	with open(output_file_name, 'w') as output_file:
		for data_tuple in data:
			# Join data by tabs as per BED format. Separate with newline character.
			bed_line = "\t".join(data_tuple) + '\n'
			output_file.write(bed_line)

def get_file(lrg_num):
	"""Downloads LRG records from the LRG website.

	Args:
		lrg_num (str): The name of an LRG record to download
	Returns:
		xml_text.text (str): LRG record in XML format
	"""
	print(lrg_num + ' not found on system, retrieving from internet.')
	# Set URL and download LRG data
	website = 'http://ftp.ebi.ac.uk/pub/databases/lrgex/'+ lrg_num +'.xml'
	xml_text = requests.get(website)
	# LRGs pending approval will have a different URL, so if the above web
	# address throws a 404 error then use a different URL with 'pending' in
	if xml_text.status_code == 404:
		website = 'http://ftp.ebi.ac.uk/pub/databases/lrgex/pending/'+ lrg_num +'.xml'
		xml_text = requests.get(website)
	return xml_text.text

def set_root(xml_data):
	"""Read an XML string as a python object.
	
	Args:
		xml_data (str): An xml file in a python string
	Returns:
		root (xml.etree.ElementTree): An object with methods to iterate over XML tags and data
	"""
	root = ET.fromstring(xml_data)
	print('root created successfully')
	return root

def convert_coords(xml_root, sorted_data):
	"""Convert LRG co-ordinates to GRCh38 coordinates.

	Args:
		xml_root (xml.etree.ElementTree): An object with methods for iterating over XML tags and data.
		sorted_data (List[Tuple[str]]): A list of tuples. Each tuple contains an LRG exon label (sorted),
			exon start and exon end values for the input LRG record.
	Returns:
		genome_coordinates (List[Tuple[str]]): 
	"""
	# Get GRCh38 data from xml_root (including coordinates)
	for item in xml_root.iter('mapping'):
		if item.attrib['coord_system'].startswith('GRCh38'):
			grch38 = item.attrib
			grch38_map = item.findall('mapping_span')[0].attrib
	# Empty list for new string
	genome_coordinates = []
	# Loop over LRG exon coordinates
	for xml_tuple in sorted_data:
		# Get LRG locations for reference genome
		genome_start = int(grch38_map['other_start'])
		genome_end = int(grch38_map['other_end'])
		exon_label, lrg_start_pre, lrg_end_pre = xml_tuple
		# Set LRG start and end coordinates. Reduce by -1 for accurate addition/subtraction from reference genome
		lrg_start = int(lrg_start_pre) - 1
		lrg_end = int(lrg_end_pre) - 1
		# If LRG coordinates are on the reverse strand, swap genome start and end.
		if grch38_map['strand'] == '-1':
			genome_start = genome_end
			# Reverse strand requires lrg coordinates to be subtracted from genome coordinates.
			# Multiple LRG coordinates by -1 to achieve this downstream.
			lrg_start, lrg_end = map(lambda x: x*-1, [lrg_start, lrg_end])
		# Created new tuple with GRChp38 coordinates
		coords = (
		    ('chr' + str(grch38['other_name'])),  # chromosome number
		    str(genome_start + lrg_start),  # grch38 start coordinates
		    str(genome_start + lrg_end)  # grch38 end coordinates
		)
		genome_coordinates.append(coords)
	return genome_coordinates

def main():
	'''Parse script input from command line arguments'''
	parser = argparse.ArgumentParser(description='Parse an XML file to produce a BED file')
	parser.add_argument('xml_file', nargs='+', help='Enter the names of the LRG file to parse')
	args = parser.parse_args()

	# store the output from lrg_parse() in a variable to write to a file
	files_to_parse = args.xml_file
	print('attempting to parse inputs: ' + ', '.join(files_to_parse))
	for f in files_to_parse:
		print('parsing ' + f)
		# call different functions depending on whether the XML file is 
		# on the system or needs to be accessed from the web
		if os.path.isfile(f):
			xml_string = parse_file(f)
			xml_root = set_root(xml_string)
			data = lrg_parse(xml_root)
		else:
			try:
				fname = f.upper()
				xml_string = get_file(fname)
				xml_root = set_root(xml_string)
				data = lrg_parse(xml_root)
			except ET.ParseError:
				print(f + ' does not exist.')
				continue
		# Convert exon regions to genomic coordinates for grch38
		output_bed = convert_coords(xml_root, data)
		write_file(output_bed, f)
		print('bed file for ' + f + ' complete.')

if __name__ == "__main__":
	main()
