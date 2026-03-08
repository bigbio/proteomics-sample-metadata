"""Tests for the template inheritance resolver module."""

import pytest
from pathlib import Path

# Resolve paths
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "sdrf-proteomics" / "sdrf-templates"

from resolve_templates import (
    load_manifest,
    load_template_yaml,
    build_inheritance_chain,
    merge_columns,
    resolve_template,
    resolve_all,
)

METADATA_FIELDS = [
    "name",
    "description",
    "documentation",
    "contributors",
    "version",
    "layer",
    "extends",
    "usable_alone",
    "mutually_exclusive_with",
    "requires",
    "excludes",
    "inheritance_chain",
    "own_columns",
    "inherited_columns",
    "all_columns",
]


# --- Manifest tests ---


class TestManifestLoading:
    def test_manifest_loads_all_templates(self):
        manifest = load_manifest(TEMPLATES_DIR)
        assert isinstance(manifest, dict)
        assert "base" in manifest
        assert "sample-metadata" in manifest
        assert "human" in manifest
        assert "ms-proteomics" in manifest
        assert "dia-acquisition" in manifest
        assert "metaproteomics" in manifest
        assert len(manifest) >= 10  # sanity: we know there are many templates


# --- Single template loading ---


class TestTemplateYamlLoading:
    def test_load_base_template(self):
        tpl = load_template_yaml(TEMPLATES_DIR, "base", "1.1.0")
        assert tpl["name"] == "base"
        assert "columns" in tpl
        assert len(tpl["columns"]) > 0

    def test_load_human_template(self):
        tpl = load_template_yaml(TEMPLATES_DIR, "human", "1.1.0")
        assert tpl["name"] == "human"
        assert tpl["extends"] == "sample-metadata@>=1.0.0"


# --- Inheritance chain ---


class TestInheritanceChain:
    def test_base_chain_length_1(self):
        manifest = load_manifest(TEMPLATES_DIR)
        chain = build_inheritance_chain("base", manifest, TEMPLATES_DIR)
        assert chain == ["base"]

    def test_sample_metadata_chain(self):
        manifest = load_manifest(TEMPLATES_DIR)
        chain = build_inheritance_chain("sample-metadata", manifest, TEMPLATES_DIR)
        assert chain == ["base", "sample-metadata"]

    def test_human_chain_3_levels(self):
        manifest = load_manifest(TEMPLATES_DIR)
        chain = build_inheritance_chain("human", manifest, TEMPLATES_DIR)
        assert chain == ["base", "sample-metadata", "human"]

    def test_dia_acquisition_chain_4_levels(self):
        manifest = load_manifest(TEMPLATES_DIR)
        chain = build_inheritance_chain("dia-acquisition", manifest, TEMPLATES_DIR)
        assert chain == ["base", "sample-metadata", "ms-proteomics", "dia-acquisition"]

    def test_metaproteomics_chain_not_through_sample_metadata(self):
        manifest = load_manifest(TEMPLATES_DIR)
        chain = build_inheritance_chain("metaproteomics", manifest, TEMPLATES_DIR)
        assert chain == ["base", "metaproteomics"]
        assert "sample-metadata" not in chain


# --- Column merging ---


class TestColumnMerging:
    def test_own_vs_inherited_separation(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        own_names = {c["name"] for c in resolved["own_columns"]}
        inherited_names = {c["name"] for c in resolved["inherited_columns"]}
        # human defines disease override + new columns like age, sex
        assert "characteristics[age]" in own_names
        assert "characteristics[sex]" in own_names
        # disease is overridden by human, so it's own
        assert "characteristics[disease]" in own_names
        # source name comes from base, not overridden by human
        assert "source name" in inherited_names

    def test_child_override_of_parent_column(self):
        """Human overrides disease to required (parent has recommended)."""
        resolved = resolve_template("human", TEMPLATES_DIR)
        disease_col = next(
            c for c in resolved["all_columns"] if c["name"] == "characteristics[disease]"
        )
        assert disease_col["requirement"] == "required"
        # Should still have inherited validators from sample-metadata
        assert "validators" in disease_col
        assert len(disease_col["validators"]) > 0

    def test_all_columns_no_duplicates(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        names = [c["name"] for c in resolved["all_columns"]]
        assert len(names) == len(set(names)), f"Duplicate columns found: {[n for n in names if names.count(n) > 1]}"

    def test_all_columns_ordering_inherited_before_own(self):
        """Inherited columns appear before own additions in all_columns."""
        resolved = resolve_template("human", TEMPLATES_DIR)
        all_names = [c["name"] for c in resolved["all_columns"]]
        # "source name" is inherited from base, should appear before human-only columns
        source_idx = all_names.index("source name")
        # "characteristics[age]" is new in human
        age_idx = all_names.index("characteristics[age]")
        assert source_idx < age_idx

    def test_source_template_annotation_on_every_column(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        for col in resolved["all_columns"]:
            assert "source_template" in col, f"Column {col['name']} missing source_template"
            assert isinstance(col["source_template"], str)
            assert col["source_template"] in resolved["inheritance_chain"]


# --- Resolved template metadata ---


class TestResolvedMetadata:
    def test_all_metadata_fields_present(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        for field in METADATA_FIELDS:
            assert field in resolved, f"Missing field: {field}"

    def test_base_metadata(self):
        resolved = resolve_template("base", TEMPLATES_DIR)
        assert resolved["name"] == "base"
        assert resolved["extends"] is None
        assert resolved["inheritance_chain"] == ["base"]
        assert resolved["usable_alone"] is False

    def test_human_metadata(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        assert resolved["name"] == "human"
        assert resolved["extends"] == "sample-metadata@>=1.0.0"
        assert resolved["layer"] == "sample"
        assert isinstance(resolved["contributors"], list)
        assert len(resolved["contributors"]) > 0

    def test_mutually_exclusive_with(self):
        resolved = resolve_template("human", TEMPLATES_DIR)
        assert isinstance(resolved["mutually_exclusive_with"], list)
        assert "vertebrates" in resolved["mutually_exclusive_with"]


# --- resolve_all ---


class TestResolveAll:
    def test_resolve_all_succeeds(self):
        all_resolved = resolve_all(TEMPLATES_DIR)
        manifest = load_manifest(TEMPLATES_DIR)
        assert len(all_resolved) == len(manifest)
        for name, resolved in all_resolved.items():
            assert resolved["name"] == name
            assert len(resolved["all_columns"]) > 0
            assert len(resolved["inheritance_chain"]) >= 1

    def test_resolve_all_every_template_has_all_fields(self):
        all_resolved = resolve_all(TEMPLATES_DIR)
        for name, resolved in all_resolved.items():
            for field in METADATA_FIELDS:
                assert field in resolved, f"Template {name} missing field: {field}"

    def test_resolve_all_no_duplicate_columns_in_any_template(self):
        all_resolved = resolve_all(TEMPLATES_DIR)
        for name, resolved in all_resolved.items():
            names = [c["name"] for c in resolved["all_columns"]]
            assert len(names) == len(set(names)), (
                f"Template {name} has duplicate columns: "
                f"{[n for n in names if names.count(n) > 1]}"
            )
