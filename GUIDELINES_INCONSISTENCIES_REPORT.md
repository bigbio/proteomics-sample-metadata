# SDRF-Proteomics Guidelines Inconsistencies Report

## Overview

This report documents inconsistencies between the SDRF-Proteomics specification guidelines and actual usage in annotated datasets. The analysis compares:
- Sample metadata guidelines (`sdrf-proteomics/metadata-guidelines/sample-metadata.adoc`)
- Template-specific guidelines (human, plants, cell-lines, vertebrates, invertebrates, single-cell)
- Actual usage in annotated projects

## Key Findings

### 1. Organism Name Capitalization

**Guideline (sample-metadata.adoc, line 32):**
> Use the scientific name in lowercase. The validator will map to the correct ontology term.

**Examples from guidelines:**
- `homo sapiens` (lowercase)
- `mus musculus` (lowercase)
- `arabidopsis thaliana` (lowercase)

**Inconsistencies found:**
- Many datasets use `Homo sapiens` (capitalized) instead of `homo sapiens`
- Examples:
  - `PXD023650.sdrf.tsv`: Uses `Homo sapiens`
  - `PXD015270.sdrf.tsv`: Uses `Homo sapiens`
  - `PXD016837.sdrf.tsv`: Uses `Homo sapiens`
  - `COMBINEDPX0000001.sdrf.tsv`: Uses `Homo sapiens`

**Recommendation:** All organism names should be lowercase. Validators should normalize or flag capitalized organism names.

---

### 2. Ancestry Category Capitalization

**Guideline (human/README.adoc, lines 428-432):**
> Use lowercase values.

**Examples from guidelines:**
- `African` (shown in table, but should be lowercase per general guidelines)
- `South Asian` (shown in table, but should be lowercase per general guidelines)

**Inconsistencies found:**
- `PXD023650.sdrf.tsv`: Uses `Black` (capitalized)
- `PXD015270.sdrf.tsv`: Uses `Caucasian` (capitalized)
- `PXD016837.sdrf.tsv`: Uses `Caucasian` (capitalized)
- `COMBINEDPX0000001.sdrf.tsv`: Uses `Caucasian` (capitalized)

**Note:** The human template README shows capitalized examples in the table (lines 428-432), which contradicts the general guideline to use lowercase. This is an inconsistency within the guidelines themselves.

**Recommendation:** 
1. Clarify in human template whether ancestry categories should be capitalized or lowercase
2. If lowercase is preferred (per general guidelines), update the human template examples
3. Standardize all datasets to use consistent capitalization

---

### 3. Organism Part Capitalization

**Guideline (sample-metadata.adoc, line 51):**
> Use lowercase for all values.

**Examples from guidelines:**
- `blood`, `liver`, `brain`, `heart`, `kidney` (all lowercase)

**Inconsistencies found:**
- `PXD016837.sdrf.tsv`: Uses `Melanocyte` (capitalized) instead of `melanocyte`

**Recommendation:** All organism part values should be lowercase.

---

### 4. Disease Name Format

**Guideline (sample-metadata.adoc, lines 135-188):**
- For healthy samples: Use `normal` (PATO:0000461) - **Recommended** or `healthy` (PATO:0001421) - **Accepted alternative**
- Disease names should use lowercase (except proper nouns in disease names)
- Examples: `breast carcinoma`, `Alzheimer disease`, `type 2 diabetes mellitus`

**Inconsistencies found:**
- `COMBINEDPX0000001.sdrf.tsv`: Uses `non-small cell lung cancer` (lowercase, correct format)
- `PXD015270.sdrf.tsv`: Uses `non-small cell lung cancer` (lowercase, correct format)
- `PXD016837.sdrf.tsv`: Uses `ductal carcinoma` (lowercase, correct format)
- `PAD000001.sdrf.tsv`: Uses `normal` (lowercase, correct format)

**Status:** Disease names appear to follow guidelines correctly in most cases.

---

### 5. Age Format

**Guideline (sample-metadata.adoc, lines 78-89):**
> Format: `{Number}{Unit}` where Unit is: `Y` (Years), `M` (Months), `W` (Weeks), `D` (Days).

**Examples:**
- `40Y` (40 years old)
- `8W` (8 weeks old)

**Inconsistencies found:**
- `PXD015270.sdrf.tsv`: Uses `58Y` (correct format)
- `PXD016837.sdrf.tsv`: Uses `31Y` (correct format)
- `PXD023650.sdrf.tsv`: Uses `31Y` (correct format)

**Status:** Age format appears to follow guidelines correctly.

---

### 6. Sex Values

**Guideline (sample-metadata.adoc, lines 98-108):**
> Allowed values: `male`, `female`, `intersex`, `not available`, `not applicable`
> NOTE: Use lowercase values.

**Inconsistencies found:**
- Most datasets correctly use lowercase: `male`, `female`
- No capitalization issues found for sex values

**Status:** Sex values follow guidelines correctly.

---

### 7. Developmental Stage

**Guideline (sample-metadata.adoc, lines 122-126):**
> Values: `adult`, `embryonic`, etc. (lowercase)

**Inconsistencies found:**
- `PXD015270.sdrf.tsv`: Uses `adult` (lowercase, correct)
- `PXD023650.sdrf.tsv`: Uses `adult` (lowercase, correct)

**Status:** Developmental stage values follow guidelines correctly.

---

### 8. Cell Line Naming

**Guideline (cell-lines/README.adoc):**
- Use Cellosaurus as primary standard
- `characteristics[cellosaurus accession]` is REQUIRED (CVCL_XXXX format)
- Use official Cellosaurus names

**Inconsistencies found:**
- `COMBINEDPX0000001.sdrf.tsv`: Uses cell line names (A549, H1975, H446, H69) but may be missing Cellosaurus accessions
- `PXD015270.sdrf.tsv`: Uses cell line names but may be missing Cellosaurus accessions

**Note:** Need to verify if Cellosaurus accessions are present in these files.

**Recommendation:** Ensure all cell line datasets include `characteristics[cellosaurus accession]` as required.

---

### 9. Treatment Values

**Guideline (sample-metadata.adoc, lines 545-548):**
> Use lowercase for all controlled vocabulary values

**Status:** Need to check treatment values in datasets for consistency.

---

### 10. Plants Template - Developmental Stage

**Guideline (plants/README.adoc, lines 142-154):**
> Use Plant Ontology (PO) terms: `seedling stage`, `rosette growth stage`, `vegetative growth stage`, etc.

**Status:** Need to check plant datasets for proper PO term usage.

---

### 11. Invertebrates Template - Genotype Format

**Guideline (invertebrates/README.adoc, lines 158-190):**
- Drosophila: `w[1118]`, `w[*]; P{GAL4-da.G32}`
- C. elegans: `daf-2(e1370)`, `wild type`

**Status:** Need to check invertebrate datasets for proper genotype notation.

---

## Summary of Critical Issues

### High Priority

1. **Organism name capitalization**: Widespread use of `Homo sapiens` instead of `homo sapiens`
2. **Ancestry category capitalization**: Inconsistent capitalization (`Caucasian`, `Black` vs lowercase)
3. **Guideline inconsistency**: Human template shows capitalized ancestry examples, but general guidelines say lowercase

### Medium Priority

4. **Organism part capitalization**: Some instances of capitalized values (`Melanocyte`)
5. **Cell line Cellosaurus accessions**: Need verification that required accessions are present

### Low Priority

6. **Age, sex, developmental stage**: Generally follow guidelines correctly
7. **Disease names**: Generally follow guidelines correctly

---

## Recommendations

1. **Update guidelines** to be consistent:
   - Clarify ancestry category capitalization in human template
   - Ensure all examples use lowercase for controlled vocabulary values

2. **Create validation rules** to flag:
   - Capitalized organism names (should be lowercase)
   - Capitalized ancestry categories (if lowercase is preferred)
   - Missing Cellosaurus accessions for cell lines

3. **Update annotated datasets** to match guidelines:
   - Convert `Homo sapiens` → `homo sapiens`
   - Convert `Caucasian` → `caucasian` (if lowercase is preferred)
   - Convert `Melanocyte` → `melanocyte`
   - Add Cellosaurus accessions where missing

4. **Document exceptions**: If certain values (like ancestry categories) should be capitalized, document this clearly with rationale.

---

## Template-Specific Issues

### Human Template
- Ancestry category capitalization inconsistency between table examples and general guidelines

### Plants Template
- Need to verify PO term usage in actual datasets

### Cell Lines Template
- Need to verify Cellosaurus accession presence in all cell line datasets

### Vertebrates Template
- Generally consistent with guidelines

### Invertebrates Template
- Need to verify genotype notation format in actual datasets

### Single-Cell Template
- Template is in draft status, fewer datasets available for comparison

---

## Next Steps

1. Review additional annotated datasets to identify more patterns
2. Create automated validation script to check for these inconsistencies
3. Update guidelines to resolve internal inconsistencies
4. Create migration guide for updating existing datasets
5. Update validator to flag these issues

---

*Report generated: 2026-01*
*Based on analysis of guidelines and sample annotated projects*
