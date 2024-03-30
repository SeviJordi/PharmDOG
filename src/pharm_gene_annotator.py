#! /usr/bin/env python3

__author__ = "Jordi Sevilla Fortuny"
__date__ = "Wed feb 21 2024"
__email__ = "jorsefor@alumni.uv.es"

# Import modules
from io import BytesIO
from zipfile import ZipFile
import requests
import pandas as pd
from argparse import ArgumentParser
import os

# URLs to zip files from PharmGKB
RELATIONSHIP_URL = "https://api.pharmgkb.org/v1/download/file/data/relationships.zip"
GENES_URL = "https://api.pharmgkb.org/v1/download/file/data/genes.zip"
CONTAINER_PATH = ".data"
GENES_NAME = "genes.tsv"
RELATIONSHIP_NAME = "relationships.tsv"

# Column names
symbol_col = "Symbol"  # Gene symbol
Pharm_id_col = "PharmGKB Accession Id"  # PharmGKB id

###################################################
# Main
###################################################


def main() -> None:
    # Parse arguments
    parser = ArgumentParser(description="Script to annotate genes with PharmGKB")
    parser.add_argument(
        "-i",
        "--input",
        dest="input_file",
        action="store",
        required=True,
        help="File with genes to query in gene symbol format",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        action="store",
        required=True,
        help="File to save the annotation",
    )

    args = parser.parse_args()

    # Read genes from input file
    with open(args.input_file) as f:
        lines = f.readlines()
        genes_list = [line.strip() for line in lines if not line.startswith("#")]
        file_out = [line.strip() for line in lines if line.startswith("#")]

    # Download files from PharmGKB if needed
    pharmdogPath = os.path.dirname(os.path.realpath(__file__))

    ## Relationships
    if not os.path.isfile(f"{pharmdogPath}/{CONTAINER_PATH}/{RELATIONSHIP_NAME}"):
        url = requests.get(RELATIONSHIP_URL)
        zipfile = ZipFile(BytesIO(url.content))
        relationships = pd.read_csv(zipfile.open("relationships.tsv"), sep="\t")

        # save the file
        if not os.path.isdir(f"{pharmdogPath}/{CONTAINER_PATH}"):
            os.mkdir(f"{pharmdogPath}/{CONTAINER_PATH}")
        
        relationships.to_csv(
            f"{pharmdogPath}/{CONTAINER_PATH}/{RELATIONSHIP_NAME}",
            sep="\t"
        )
            
    else:
        relationships = pd.read_csv(
            f"{pharmdogPath}/{CONTAINER_PATH}/{RELATIONSHIP_NAME}",
            sep="\t"
            )

    ## Genes
    if not os.path.isfile(f"{pharmdogPath}/{CONTAINER_PATH}/{GENES_NAME}"):
        url = requests.get(GENES_URL)
        zipfile = ZipFile(BytesIO(url.content))
        genes = pd.read_csv(zipfile.open("genes.tsv"), sep="\t")

        # save the file
        if not os.path.isdir(f"{pharmdogPath}/{CONTAINER_PATH}"):
            os.mkdir(f"{pharmdogPath}/{CONTAINER_PATH}")
        
        genes.to_csv(
            f"{pharmdogPath}/{CONTAINER_PATH}/{GENES_NAME}",
            sep="\t"
        )

    else:
        genes = pd.read_csv(
            f"{pharmdogPath}/{CONTAINER_PATH}/{GENES_NAME}",
            sep="\t"
            )

    symbol2pharmid = {
        symbol: pharmid
        for symbol, pharmid in zip(
            genes[symbol_col].tolist(), genes[Pharm_id_col].tolist()
        )
    }
  
    # Annotate genes
    file_out.append("Gene_Symbol,PharmGKB_id,Feature,Feature_type,Status,PMIDs")
    for gene in genes_list:
        new_line = f"{gene},"

        # Add pharm id
        if gene not in symbol2pharmid:
            new_line += ",,,,"
        else:
            new_line += f"{symbol2pharmid[gene]},"

            # If not pharm id no annotation
            if symbol2pharmid[gene] not in relationships["Entity1_id"].tolist():
                new_line += ",,,"
                
            else:
                entry = relationships.loc[
                    relationships["Entity1_id"] == symbol2pharmid[gene]
                ].iloc[0]
                new_line += "{},{},{},{}".format(
                    entry["Entity2_name"],
                    entry["Entity2_type"],
                    entry["Association"],
                    entry["PMIDs"],
                )

        file_out.append(new_line)

    # Save the annotation
    f = open(args.output_file, "w")
    for line in file_out:
        f.write(f"{line}\n")

    exit(0)


if __name__ == "__main__":
    main()
