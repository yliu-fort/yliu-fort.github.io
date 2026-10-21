#!/usr/bin/env bash
# Check a draft and move it into _posts/ with a date. Does not commit or push.
#   scripts/publish-post.sh <slug> [YYYY-MM-DD]
set -euo pipefail
cd "$(dirname "$0")/.."

slug="${1:?usage: scripts/publish-post.sh <slug> [YYYY-MM-DD]}"
date="${2:-$(date +%Y-%m-%d)}"
src="_drafts/$slug.md"
dst="_posts/$date-$slug.md"

[[ -f "$src" ]] || { echo "error: no draft at $src" >&2; exit 1; }
[[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "error: date must be YYYY-MM-DD" >&2; exit 1; }
[[ ! -e "$dst" ]] || { echo "error: $dst already exists" >&2; exit 1; }

python3 scripts/check-post.py "$src"

mkdir -p _posts
if git ls-files --error-unmatch "$src" >/dev/null 2>&1; then
  git mv "$src" "$dst"
else
  mv "$src" "$dst"
fi

echo "moved to $dst"
echo
echo "To publish:"
echo "  git add $dst assets/posts/$slug"
echo "  git commit -m \"Post: $(sed -n 's/^title: *//p' "$dst" | head -1 | tr -d '\"')\""
echo "  git push origin dev"
