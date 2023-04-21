from pathlib import Path

import polars as pl
from phenopackets import Disease

from phenotype2phenopacket.utils.gene_map_utils import (
    GeneIdentifierUpdater,
    create_gene_identifier_map,
    create_hgnc_dict,
)
from phenotype2phenopacket.utils.phenopacket_utils import (
    PhenopacketInterpretationExtender,
    PhenopacketUtil,
    phenopacket_reader,
    write_phenopacket,
)
from phenotype2phenopacket.utils.utils import all_files


def get_phenotype_to_disease_entries(
    omim_disease_pg: pl.DataFrame, disease: Disease
) -> pl.DataFrame:
    return omim_disease_pg.filter(pl.col("database_id") == disease.term.id)


def add_genes(phenopacket_path: Path, disease_pg, gene_identifier_updater, output_dir):
    phenopacket = phenopacket_reader(phenopacket_path)
    disease = PhenopacketUtil(phenopacket).return_phenopacket_disease()
    filtered_disease_pg = get_phenotype_to_disease_entries(disease_pg, disease)
    if len(filtered_disease_pg) == 0:
        print("No disease matches")
    else:
        phenopacket_with_genes = PhenopacketInterpretationExtender(
            phenopacket
        ).add_gene_interpretation_to_phenopacket(
            omim_disease_phenotype_gene_map=filtered_disease_pg,
            gene_identifier_updater=gene_identifier_updater,
        )
        write_phenopacket(phenopacket_with_genes, output_dir.joinpath(phenopacket_path.name))


def add_genes_to_directory(phenopacket_dir: Path, disease_pg, hgnc_data_file, output_dir):
    hgnc_dict = create_hgnc_dict(hgnc_data_file)
    identifier_map = create_gene_identifier_map(hgnc_data_file)
    gene_identifier_updater = GeneIdentifierUpdater(
        gene_identifier="ensembl_id", hgnc_data=hgnc_dict, identifier_map=identifier_map
    )
    for phenopacket_path in all_files(phenopacket_dir):
        add_genes(phenopacket_path, disease_pg, gene_identifier_updater, output_dir)
