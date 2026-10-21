#!/usr/bin/env bash
# Local preview with drafts: http://localhost:4000
#   scripts/serve.sh [extra jekyll options]
set -euo pipefail
cd "$(dirname "$0")/.."
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
exec bundle exec jekyll serve --drafts "$@"
