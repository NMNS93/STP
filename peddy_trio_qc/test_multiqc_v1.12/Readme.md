# dnanexus_multiqc v 1.12
ewels/MultiQC [v1.6](https://github.com/ewels/MultiQC/)

## What does this app do?
This app runs MultiQC to generate run wide quality control (QC) using the outputs from MokaAMP, MokaPipe and MokaWES pipelines including:
* Picard (CalculateHsMetrics, MarkDuplicates and CollectMultipleMetrics, TargetedPcrMetrics)
* FastQC 
* bcl2fastq2
* Peddy
* verifyBAMID
* Sentieon (duplication_metrics)

## What are typical use cases for this app?
To generate QC reports, this app should be run at the end of an NGS pipeline, when all QC software outputs are available.

## What data are required for this app to run?
* project_for_multiQC - The name of the project to be assessed.
  * This project must have a 'QC' folder in its root directory.
* coverage_level - Define which column to display from hsmetrics, reporting the percentage of target bases covered at the required depth (eg PCT_TARGET_BASES_20X)

Additional QC files are downloaded from other locations:
* 'Stats.json' is downloaded from  /runfolder/Data/Intensities/BaseCalls/Stats if demultiplexing was performed by bcl2fastq v2.20 (or later) 
* Any files with \*metrics\* in the name are downloaded. Sentieon apps output all files into the output folder, with inconsistent naming between apps. eg Duplication_metrics and duplication_metrics. 

## What does this app output?
The following outputs are placed in the DNAnexus project under '/QC/multiqc':
* A HTML QC report (with the name of the runfolder) which should be uploaded to the Viapath Genome Informatics server.
* A folder containing the output in text format.

## How does this app work?
1. The app downloads all files within the QC/ directory of the project. 
2. The dx_find_and_download function is used to search for specific files, which are downloaded only if found.
3. If sention duplication_metrics files are present the app replaces the header (with a template packaged in the app) so the file is recognised as a picard markduplicates file.
4. The app sets the minimum-fold coverage reported in the general stats table by editing 'dnanexus_multiqc_config.yaml'. This value comes from the app's 'coverage_level' input parameter.
5. A dockerised version of MultiQC is used. The docker image is stored on DNAnexus as an asset, which is bundled with the app build. The following commands were used to generate this asset in a cloud workstation:
    * `docker pull ewels/multiqc:v1.6`
    * `dx-docker create-asset ewels/multiqc:v1.6`
    * The asset on DNAnexus was then renamed with the following command: `dx mv ewels\\multiqc\\:v1.6 ewels_multiqc_v1.6`
6. MultiQC parses all files, including any recognised files in the report.
7. The MultiQC outputs are uploaded to DNAnexus.

## What are the limitations of this app
* The project which MultiQC is run on must be shared with the user mokaguys
* Only one value can be given to the coverage_level parameter, which may not be ideal for runs with mixed samples. Multiple reports may be required in these cases

## This app was made by Viapath Genome Informatics 
