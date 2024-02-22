#! /usr/bin/env python3

# Programa que permite anotar genes con información de pharmGKB

from io import BytesIO
from zipfile import ZipFile
import requests
import pandas as pd
from argparse import ArgumentParser

# URLs a los archivos primarios de pharmGKB que relacionan genes con enfermedades.
RELATIONSHIP_URL = "https://api.pharmgkb.org/v1/download/file/data/relationships.zip"
GENES_URL = "https://api.pharmgkb.org/v1/download/file/data/genes.zip"

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

    # Download files from PharmGKB
    ## Relationships
    url = requests.get(RELATIONSHIP_URL)
    zipfile = ZipFile(BytesIO(url.content))
    relationships = pd.read_csv(zipfile.open("relationships.tsv"), sep="\t")

    ## Genes
    url = requests.get(GENES_URL)
    zipfile = ZipFile(BytesIO(url.content))
    genes = pd.read_csv(zipfile.open("genes.tsv"), sep="\t")

    symbol2pharmid = {
        symbol: pharmid
        for symbol, pharmid in zip(
            genes[symbol_col].tolist(), genes[Pharm_id_col].tolist()
        )
    }
  

    # Annotate genes
    file_out.append("Gene Symbol,PharmGKB id,Feature,Feature type,Status,PMIDs")
    for gene in genes_list:
        new_line = f"{gene},"

        # Add pharm id
        new_line += f"{symbol2pharmid[gene]}," if gene in symbol2pharmid else ",,,,"

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
