#!/bin/bash
#
# Rebuild site/sdrf-data.json from bigbio/sdrf-annotated-datasets.
# The weekly catalog workflow runs this. A normal documentation build
# reuses the published snapshot instead.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SDRF_DATASETS_REPO="${SDRF_DATASETS_REPO:-bigbio/sdrf-annotated-datasets}"
SDRF_DATASETS_BRANCH="${SDRF_DATASETS_BRANCH:-main}"

if [ -z "${SDRF_DATASETS_DIR:-}" ]; then
    VENDOR_DIR="$REPO_ROOT/vendor/sdrf-annotated-datasets"
    if [ -d "$VENDOR_DIR/.git" ]; then
        echo "Updating $SDRF_DATASETS_REPO@$SDRF_DATASETS_BRANCH in $VENDOR_DIR ..."
        git -C "$VENDOR_DIR" fetch --depth 1 origin "$SDRF_DATASETS_BRANCH"
        git -C "$VENDOR_DIR" checkout -f -B "$SDRF_DATASETS_BRANCH" FETCH_HEAD
    else
        echo "Cloning $SDRF_DATASETS_REPO@$SDRF_DATASETS_BRANCH into $VENDOR_DIR ..."
        rm -rf "$VENDOR_DIR"
        mkdir -p "$(dirname "$VENDOR_DIR")"
        git clone --depth 1 --single-branch --branch "$SDRF_DATASETS_BRANCH" \
            "https://github.com/${SDRF_DATASETS_REPO}.git" "$VENDOR_DIR"
    fi
    SDRF_DATASETS_DIR="$VENDOR_DIR/datasets"
fi

if [ ! -d "$SDRF_DATASETS_DIR" ]; then
    echo "Error: datasets directory not found at $SDRF_DATASETS_DIR" >&2
    exit 1
fi

export SDRF_DATASETS_DIR SDRF_DATASETS_REPO SDRF_DATASETS_BRANCH
echo "Using SDRF datasets from: $SDRF_DATASETS_DIR"
python3 "$REPO_ROOT/site/build-sdrf-index.py"

mkdir -p "$REPO_ROOT/vendor"
touch "$REPO_ROOT/vendor/.catalog-rebuilt"
echo "SDRF explorer catalog rebuilt."
