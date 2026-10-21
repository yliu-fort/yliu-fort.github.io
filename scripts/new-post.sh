#!/usr/bin/env bash
# Create a draft post and its asset folder.
#   scripts/new-post.sh "Post title" [slug]
set -euo pipefail
cd "$(dirname "$0")/.."

title="${1:?usage: scripts/new-post.sh \"Post title\" [slug]}"
slug="${2:-$(printf '%s' "$title" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')}"

if [[ ! "$slug" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error: could not make a slug from the title; pass one, e.g. scripts/new-post.sh \"$title\" my-post" >&2
  exit 1
fi

draft="_drafts/$slug.md"
if [[ -e "$draft" ]] || ls _posts/*-"$slug".md >/dev/null 2>&1; then
  echo "error: a post with slug '$slug' already exists" >&2
  exit 1
fi

mkdir -p _drafts "assets/posts/$slug"
escaped_title=${title//\"/\\\"}
cat > "$draft" <<EOF
---
title: "$escaped_title"
description: "One-sentence summary shown in post lists and link previews."
tags: []
toc: false
---

Opening paragraph.

## First section

See AGENTS.md for math, figures and references. Put images in assets/posts/$slug/.
EOF

echo "created $draft"
echo "assets go in assets/posts/$slug/"
