#!/bin/bash
#
# Publish site/sdrf-data.json to the explorer-catalog branch.
# That branch is the snapshot documentation builds download between
# weekly rebuilds. It is not the default branch: the push replaces
# only refs/heads/explorer-catalog.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MARKER="$REPO_ROOT/vendor/.catalog-rebuilt"
CATALOG="$REPO_ROOT/site/sdrf-data.json"

if [ ! -f "$MARKER" ]; then
    echo "Explorer catalog was not rebuilt; leaving the explorer-catalog branch unchanged."
    exit 0
fi

if [ ! -s "$CATALOG" ]; then
    echo "Error: $CATALOG is missing, so the catalog branch was not updated." >&2
    exit 1
fi

if [ -z "${GITHUB_REPOSITORY:-}" ]; then
    echo "Not in GitHub Actions; leaving the explorer-catalog branch unchanged."
    rm -f "$MARKER"
    exit 0
fi

cd "$REPO_ROOT"
export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-github-actions[bot]}"
export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"
export GIT_COMMITTER_NAME="${GIT_COMMITTER_NAME:-$GIT_AUTHOR_NAME}"
export GIT_COMMITTER_EMAIL="${GIT_COMMITTER_EMAIL:-$GIT_AUTHOR_EMAIL}"

BLOB="$(git hash-object -w "$CATALOG")"
TREE="$(printf '100644 blob %s\tsdrf-data.json\n' "$BLOB" | git mktree)"
COMMIT="$(git commit-tree "$TREE" -m "Refresh SDRF explorer catalog")"

echo "Publishing catalog commit $COMMIT to explorer-catalog ..."
git push origin "$COMMIT:refs/heads/explorer-catalog" --force
rm -f "$MARKER"
echo "explorer-catalog branch updated."
