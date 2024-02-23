# PharmDOG
![logo](.assets/logo.png)
Pharmacogenomic decoding of genes (**PharmDOG**) is an annotation tool designed to provide comprehensive gene annotations by harnessing the information available in the [PharmGKB](https://www.pharmgkb.org/) database.

## Instalation

You have the option to download the zipped version of this repository (find the button on the right-hand side of the screen). Utilize the `pharm_gene_annotator.py` in the `src` directory as a stand-alone program.

In case your system lacks Python version 3.10 or newer, it is necessary to [download and install it](http://www.python.org/downloads/). On Linux-like systems (including Ubuntu) you can install it from the command line using:

```
sudo apt-get install python3
```
Ensure that the [requests](https://requests.readthedocs.io/en/latest/) and [pandas](https://pandas.pydata.org/) Python modules are installed. You can conveniently install them using pip by referencing the [requirements file](requirements.txt) provided in this repository:

```
pip3 install -r requirements.txt
```
## Command line interface

Here is the general usage (you can view this in your command line with `python3 /path/to/PharmDOG/src/pharm_gene_annotator.py -h`):

```
usage: pharm_gene_annotator.py [-h] -i INPUT_FILE -o OUTPUT_FILE

Script to annotate genes with PharmGKB

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input INPUT_FILE
                        File with genes to query in gene symbol format
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        File to save the annotation
```

The **input file** should be a text file formatted with one gene per line using gene symbol notation. The input file also supports comment lines starting with **#**.

## Output

The output from [pharm_gene_annotator.py](src/pharm_gene_annotator.py)  is presented as a comma-separated file (CSV) with six columns:



- **Gene_symbol**: The symbol name of the queried genes.
- **PharmGKB_id**: Identification code for the gene in the PharmGKB database.
- **Feature**: Entity associated with the gene in the PharmGKB database.
- **Feature_type**: Broad classification of the Feature (e.g., Disease, Chemical...).
- **Status**: Indicates whether the Feature is associated with the gene or not.
- **PMIDs**: Identification codes for the evidence supporting the relationship. If multiple, they are separated by ";".