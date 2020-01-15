#!/usr/bin/env bash
# dnanexus_peddy v1.4
#   Peddy calculates sex and relatedness metrics from alignment data. 
#   Runs peddy v0.3.1 on BAM files in the output/ directory of a DNANexus project.
#   Project's /output directory must contain multi-/single-sample VCF files for analysis.
#       These files should be suffixed 'refined.vcf.gz' and follow the VIAPATH naming convention:
#       1. Single-sample: 
#       2. Multi-sample: 
#
# Usage:
#    dx run peddy_v1.4 -iproject_for_peddy=<dnanexus_project> -ifam_file=<file.fam>
#    Options:
#       -iproject_for_peddy: A DNANexus project with BAM and BAI files in the /output directory


main(){
    API_KEY=$(dx cat project-FQqXfYQ0Z0gqx7XG9Z2b4K43:mokaguys_nexus_auth_key)

    # Download annotated VCFs. These are suffixed 'refined.vcf.gz' and expected at 'project:/output'
    dx download $project_for_peddy:output/*.refined.vcf.gz $project_for_peddy:output/*refined.vcf.gz.tbi --auth $API_KEY

    # Merge VCF files
    echo "Merging VCFs"
    #   bcftools merge option '-O z' produces a compressed vcf, which is named using the '-o' flag.
    #   Docker `-v /:/data` argument mounts the container root to /data.
    dx-docker run -v ${PWD}:/data quay.io/biocontainers/bcftools:1.6--1 \
        bcftools merge -O z -o /data/merged.vcf.gz /data/*.vcf.gz 
    
    # Create VCF file index
    echo "Creating Index"
    dx-docker run -v ${PWD}:/data quay.io/biocontainers/bcftools:1.6--1 \
        bcftools index -t /data/merged.vcf.gz

    # Create FAM file by parsing sample names from VCF header
    echo "Creating FAM"
    dx-docker run -v ${PWD}:/data quay.io/biocontainers/bcftools:1.6--1 \
        bcftools query -l /data/merged.vcf.gz > sample_names.txt
    generate_fam.py sample_names.txt > peddy.fam

    # Run peddy
    dx-docker run -v ${PWD}:/data quay.io/biocontainers/peddy:0.3.1--py27_0 \
        /bin/bash -c \
        "cd /data; \
        peddy --plot -p 4 --prefix ped merged.vcf.gz peddy.fam" 

    # Move output files to location for upload command
    mkdir -p $HOME/out/peddy/QC/peddy
    #   MultiQC reads files from the QC directory of a project.
    #   This command places peddy files in the correct location
    mv ped.*{peddy.ped,het_check.csv,ped_check.csv,sex_check.csv} $HOME/out/peddy/QC/
    #   Remaining peddy files organised in a QC subfolder
    mv ped* *merged.vcf.gz* $HOME/out/peddy/QC/peddy

    # Upload all output files to DNA Nexus project. Users outputSpec in dxapp.json to upload files
    # in /home/dnanexus/out/peddy/ to the project root.
    dx-upload-all-outputs

}
