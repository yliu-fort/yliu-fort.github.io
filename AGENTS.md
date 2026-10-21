# Writing and publishing on yliu-fort.github.io

This repository is Yuxuan Liu's personal site: a home page, a blog, a publication list and a CV.
It is a plain Jekyll site built by **GitHub Pages from the `dev` branch**: whatever is pushed to
`dev` is public at <https://yliu-fort.github.io> about a minute later.

These instructions are for anyone writing a post, human or AI agent.

## Where things live

| Path | What |
| --- | --- |
| `_drafts/<slug>.md` | Unpublished posts (never built on the live site) |
| `_posts/YYYY-MM-DD-<slug>.md` | Published posts; the date in the file name is the post date |
| `assets/posts/<slug>/` | Images and other files for one post |
| `_data/publications.yml` | Publication list (`selected: true` shows an entry on the home page) |
| `_data/cv.yml` | Education, research experience, talks |
| `_data/portrait.yml` | Home-page portrait; written by `scripts/portrait.py` |
| `index.html` | Home page text |
| `_layouts/`, `_includes/`, `assets/css/` | Design. Do not touch these when writing a post. |

Post URLs look like `/blog/2026/<slug>/`.

## Workflow

```bash
scripts/new-post.sh "Title of the post" [slug]   # creates _drafts/<slug>.md and assets/posts/<slug>/
scripts/serve.sh                                 # preview at http://localhost:4000, drafts included
scripts/check-post.py _drafts/<slug>.md          # lint math, images and front matter
scripts/publish-post.sh <slug> [YYYY-MM-DD]      # check, then move the draft into _posts/
git add _posts/<date>-<slug>.md assets/posts/<slug>
git commit -m "Post: <title>"
git push origin dev                              # this makes it public
```

A slug is lower-case ASCII words joined by hyphens (`wave-breaking-closures`). For a title that is
not in English, pass the slug explicitly.

Publishing is public and immediate. Run `scripts/check-post.py` and look at the post in the local
preview before pushing. An agent acting for the owner should follow the owner's instructions
on whether to push.

## Front matter

```yaml
---
title: "Learned closures for wave breaking"
description: "One sentence. Shown under the title, in post lists and in link previews. No math."
tags: [waves, machine learning]     # optional, lower case
toc: true                           # optional: table of contents from ## and ### headings
lang: zh                            # optional: for a post written in Chinese
last_modified_at: 2026-11-02        # optional: shown as "updated"
image: /assets/posts/<slug>/card.png  # optional: link-preview image
mathjax: false                      # optional: math is on by default
cite: false                         # optional: hides the "Cite this post" BibTeX block
---
```

Only `title` and `description` are required. Start the body at heading level `##`; the
title is the only `#`.

## Math (MathJax 3, rendered in the browser)

The site uses kramdown (GFM flavour) as on GitHub Pages. Kramdown treats `$$…$$` as math and
leaves its contents alone; a single `$…$` is ordinary text that MathJax picks up later, so
Markdown escaping applies to it first.

- **Inline:** `$k a$`, `$\omega^2 = g k \tanh(kh)$`, `$u_t + u u_x = 0$` all work.
  If the formula contains a backslash followed by punctuation, such as `\{ \} \| \! \\ \# \_`,
  write it as `$$…$$` inside the sentence instead: `the set $$\{x : \|x\| < 1\}$$ is open`.
  `$$…$$` inside a paragraph renders inline and is always safe.
- **Display:** put `$$` on its own lines with a blank line before and after.

  ```markdown
  The energy balance reads

  $$
  \frac{\partial E}{\partial t} + \nabla \cdot (\mathbf{c}_g E) = -\epsilon_b
  $$

  where ...
  ```

- **Numbered equations:** use an environment inside the `$$` block, `\label` it and refer to it
  with `\eqref`:

  ```markdown
  $$
  \begin{equation}
  \eta = a\cos\theta + \tfrac12 k a^2 \cos 2\theta \label{eq:stokes}
  \end{equation}
  $$

  Equation \eqref{eq:stokes} is the second-order Stokes wave.
  ```

  `align`, `aligned`, `cases`, `pmatrix` and the rest of AMS math work the same way. Plain
  `$$…$$` displays are not numbered.
- **Macros:** define them once at the top of the post in a display block, e.g.
  `$$\newcommand{\R}{\mathbb{R}}$$`.
- **A literal dollar sign** in text: write `\\$`. Inside code spans and code blocks, `$` is never
  treated as math.

`scripts/check-post.py` flags inline formulas that will lose their backslashes and display
blocks without a blank line before them.

## Figures

Put files in `assets/posts/<slug>/`. Prefer SVG for plots and diagrams; keep raster images
under about 500 KB and at most about 1600 px wide.

Numbered figure with a caption (Markdown and math allowed in the caption):

```liquid
{% include figure.html
   src="/assets/posts/<slug>/stokes.svg"
   alt="Linear and second-order Stokes wave profiles"
   caption="Linear (dashed) and second-order Stokes (solid) profiles for $ka = 0.25$."
   width="85%" %}
```

Figures are numbered automatically in order (Figure 1, Figure 2, …); refer to them in the text by
number. For an unnumbered image use plain Markdown: `![alt text](/assets/posts/<slug>/photo.jpg)`.
Always use paths starting with `/assets/`, and always give alt text.

## Other writing features

- Code blocks with a language (`python`, `cpp`, `fortran`, `bash`, `julia`, …) are highlighted.
- Footnotes: `text[^1]` and later `[^1]: The note.` They are collected at the end of the post.
- Tables use GFM pipe syntax.
- References: there is no BibTeX processing. Cite as (Author, Year) in the text and list the
  references under a final `## References` heading, with DOI links.
- Raw HTML is allowed when Markdown is not enough (e.g. `<details>`), but keep it simple.

See `_drafts/example-post.md` for a post that uses all of the above; preview it with
`scripts/serve.sh`.

## Home-page portrait

The left column of the home page holds a 2:3 full-length portrait. With no portrait set
it shows a blank frame. To set or change it:

```bash
scripts/portrait.py          # opens http://127.0.0.1:4010 in the browser
```

Choose or drop a photo, drag and scroll to frame it, adjust tone, then **Save to site**. The
tool writes `assets/images/portrait.jpg` (900 × 1350), `portrait.webp`, `portrait-card.jpg`
(1200 × 630, used for link previews) and `_data/portrait.yml`; commit those and push.
**Remove portrait from site** deletes them and leaves the frame blank. Processing happens in the
browser, and re-encoding drops EXIF metadata such as GPS position. This is the owner's photo:
agents should not change it unless asked.

## Do not

- add Jekyll plugins: GitHub Pages only runs its own allow-list, and a build with an unknown plugin
  fails silently on the live site;
- change `_config.yml`, layouts or styles as part of writing a post;
- commit large binaries (videos, datasets, PDFs over a few MB); link to them instead;
- push to `dev` without a clean `scripts/check-post.py` run.
