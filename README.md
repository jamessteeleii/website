# Steele Research

The source for [steele-research.com](https://steele-research.com), authored with Quarto and deployed to GitHub Pages.

## Preview

Quarto is included with current versions of RStudio and can also be installed from [quarto.org](https://quarto.org/docs/download/).

```sh
quarto preview
```

The project uses port `1313`. Draft posts are visible in preview but excluded from production builds.

After changing `data/publications.json` or `data/videos.yaml`, regenerate the data-driven page fragments before previewing:

```sh
python scripts/render_quarto_data.py
```

## Write a short note

Copy `templates/note.qmd` to a dated page bundle such as:

```text
notes/2026/08/my-note/index.qmd
```

Write in Quarto Markdown, leave `draft: true` while working, and remove that line or change it to `false` when ready to publish.

## Write a long-form essay

Copy `templates/essay.qmd` to a page bundle such as:

```text
essays/2026/my-essay/index.qmd
```

Images, bibliographies, data, and other supporting files can live beside `index.qmd`. Quarto citations use `[@citation-key]`; add `bibliography: references.bib` to the document front matter when needed.

Executable R, Python, or Julia content is supported. The project uses `freeze: auto`, so render computational posts locally and commit the generated `_freeze/` output with the source.

## Publish

Pushing to `main` or `master` runs `.github/workflows/quarto.yaml`. GitHub installs Quarto, regenerates the research and video pages, renders `_site/`, and deploys it to GitHub Pages. The repository's **Settings → Pages → Build and deployment → Source** must be set to **GitHub Actions**.

The generated `_site/` directory is ignored and should not be committed.

## Custom domain

The root `CNAME` file is copied into the rendered site. Configure `steele-research.com` in the repository's Pages settings before changing DNS away from Netlify, then enable HTTPS once GitHub has issued the certificate.

## Structure

- `index.qmd` — home page
- `about/`, `consulting/`, `research/`, `videos/`, `writing/` — main sections
- `notes/` — short posts
- `essays/` — long-form posts
- `templates/` — starting points for new posts
- `data/` — publication and video catalogues
- `css/main.css` — site design
- `scripts/render_quarto_data.py` — builds static research/video fragments
- `publications/` — locally hosted, shareable full texts

The previous Wowchemy/Hugo site remains recoverable from Git history.
