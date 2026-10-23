"""Tests for the SDRF explorer catalog builder."""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "site" / "build-sdrf-index.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_sdrf_index", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def catalog_module():
    return load_module()


def write_sdrf(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_catalog_counts_samples_without_mixing_organism_parts(catalog_module, tmp_path):
    header = (
        "source name\tcharacteristics[organism]\tcharacteristics[organism part]\t"
        "characteristics[disease]\tcomment[instrument]\tcomment[label]\t"
        "comment[proteomics data acquisition method]\n"
    )
    write_sdrf(
        tmp_path / "PXD000001" / "PXD000001.sdrf.tsv",
        "#template=ms-proteomics\n#version=1.0.0\n"
        + header
        + "sample1\tNT=Homo sapiens;AC=NCBITaxon:9606\tliver\tnormal\t"
        "NT=Q Exactive;AC=MS:1001911\tNT=TMT126;AC=MS:1002909\t"
        "Data-independent acquisition\n"
        "sample2\tNT=Homo sapiens;AC=NCBITaxon:9606\tliver\t"
        "NT=breast cancer;AC=MONDO:0007254\tNT=Q Exactive;AC=MS:1001911\t"
        "NT=label free sample;AC=MS:1002038\tData-independent acquisition\n",
    )
    write_sdrf(
        tmp_path / "PXD000001" / "PXD000001-fraction.sdrf.tsv",
        header
        + "sample3\tNT=Mus musculus;AC=NCBITaxon:10090\tbrain\tnot available\t"
        "NT=Orbitrap Fusion Lumos;AC=MS:1002732\tNT=label free sample;AC=MS:1002038\t"
        "Data-dependent acquisition\n",
    )
    write_sdrf(tmp_path / "PXD000002" / "empty.sdrf.tsv", header)

    catalog = catalog_module.build_catalog(
        str(tmp_path), "bigbio/sdrf-annotated-datasets", "main"
    )
    stats = catalog["statistics"]
    datasets = {item["file"]: item for item in catalog["datasets"]}

    assert stats["total_sdrf_files"] == 2
    assert stats["total_accessions"] == 1
    assert stats["total_samples"] == 3
    assert stats["split_accessions"] == 1
    assert stats["organisms"] == {"Homo sapiens": 2, "Mus musculus": 1}
    assert "liver" not in stats["organisms"]
    assert stats["organism_parts"]["liver"] == 2
    assert stats["diseases"] == {"breast cancer": 1}
    assert "normal" not in stats["diseases"]
    assert stats["organism_count"] == 2
    assert stats["source_repository"] == "bigbio/sdrf-annotated-datasets"
    assert stats["source_branch"] == "main"

    primary = datasets["PXD000001.sdrf.tsv"]
    assert primary["id"] == "PXD000001"
    assert primary["samples"] == 2
    assert primary["files"] == 2
    assert primary["experiment_type"] == "DIA"
    assert primary["label_type"] == "TMT"
    assert primary["template"] == "ms-proteomics"
    assert primary["version"] == "1.0.0"
    assert primary["organisms"] == ["Homo sapiens"]
    assert primary["diseases"] == ["breast cancer"]
    assert "github_url" not in primary

    fraction = datasets["PXD000001-fraction.sdrf.tsv"]
    assert fraction["experiment_type"] == "DDA"
    assert fraction["label_type"] == "Label-free"
    assert "template" not in fraction


def test_column_match_does_not_treat_organism_part_as_organism(catalog_module):
    assert catalog_module.column_matches(
        "characteristics[organism]", "characteristics[organism]"
    )
    assert not catalog_module.column_matches(
        "characteristics[organism part]", "characteristics[organism]"
    )
    assert catalog_module.column_matches(
        "characteristics[organism].1", "characteristics[organism]"
    )
