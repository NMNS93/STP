# Project Document : LRG Parser v1.0

## Brief
Create a tool that parses exon coordinates from LRG files in XML format. The output should be a BED file with genomic coordinates corresponding to each LRG exon region.

## User story
As a scientist, I want to find all the exon start and end co-ordinates in an LRG file correspinding to a gene so that I can identify whether my variant is coding or non-coding.

## Functional requirements
* FR1 The application accepts an LRG file in XML format as input
* FR2 The application accurately converts LRG exon regions to genomic coordinates for reference genome build GRCh38
* FR3 The application outputs a BED-formatted file with calculated genomic coordinates

## Technical requirements
* TR1 The application is compatible with all operating systems in genetics department os use
* TR2 The application will be available 99% of the time
* TR3 The application will be able to take multiple inputs at a time
* TR3 When the input is an existing file, the output will be produced in less than 3 seconds 95% of the time
* TR4 When the input is an existing file, the output will be produced in less than 10 seconds 99% of the time
* TR5 If the LRG input needs to be fetched from the internet the only acceptable reason for failure will be lack of internet connection or LRG website failure
* TR6 If the LRG input needs to be fetched from the internet, the output will be produced in less than 10 seconds 95% of the time
* TR7 If the LRG input needs to be fetched from the internet, the output will be produced in less than 30 seconds 99% of the time
