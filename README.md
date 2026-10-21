# yliu-fort.github.io

Personal site and blog of Yuxuan Liu, served by GitHub Pages from the `dev` branch at
<https://yliu-fort.github.io>.

Posts are Markdown files with LaTeX (MathJax), figures and code. How to write, preview and
publish a post is described in [AGENTS.md](AGENTS.md).

```bash
scripts/new-post.sh "Post title"      # start a draft
scripts/serve.sh                      # preview at http://localhost:4000
scripts/publish-post.sh <slug>        # check and move into _posts/
scripts/portrait.py                   # set the home-page portrait
```
