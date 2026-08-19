# Steele Research

The source for [steele-research.com](https://steele-research.com), authored with Quarto and deployed to GitHub Pages.

## Start in RStudio

Open `website.Rproj` in RStudio. The project uses reproducible defaults: it does not restore `.RData`, save the workspace, or save command history automatically.

Quarto is included with current versions of RStudio and can also be installed from [quarto.org](https://quarto.org/docs/download/). From the RStudio Terminal, start a local preview with:

```sh
quarto preview
```

The preview runs at <http://localhost:1313>. It refreshes after source changes; stop it with `Ctrl+C`. Draft posts are visible in preview but excluded from production builds.

If you prefer to stay in the R console, install the `quarto` R package once and use its equivalent project commands:

```r
install.packages("quarto") # once only
quarto::quarto_preview()
quarto::quarto_render()
```

Run a complete production render before publishing substantial changes:

```sh
quarto render
```

The generated `_site/` directory is ignored by Git and should not be committed.

## Where to edit the site

These are the hand-edited sources:

| Component | File |
|---|---|
| Home-page wording and sections | `index.qmd` |
| About page | `about/index.qmd` |
| Detailed declaration of interests | `declaration-of-interests/index.qmd` |
| Consulting page | `consulting/index.qmd` |
| Research-page heading and introduction | `research/index.qmd` |
| Video-page heading and introduction | `videos/index.qmd` |
| Writing-page heading and listing settings | `writing/index.qmd` |
| Notes index | `notes/index.qmd` |
| Essays index | `essays/index.qmd` |
| Navigation, site title, description, favicon, resources, and rendering options | `_quarto.yml` |
| Shared language and date formatting | `_metadata.yml` |
| Colours, typography, spacing, responsive layout, and component styling | `css/main.css` |
| Shared footer | `includes/site-footer.html` |
| Logos and other shared images | `images/` |
| Publication filtering and other browser behaviour | `js/library.js` and `includes/research-script.html` |

Most page prose is ordinary Quarto Markdown. Some page structures use raw HTML blocks so that the custom layout classes in `css/main.css` can be applied. Edit the words inside those blocks normally, but retain the surrounding tags and class names unless you are deliberately changing the layout.

Do not directly edit `includes/home-library.html`, `includes/home-latest.html`, `includes/research-archive.html`, or `includes/video-archive.html`. They are generated from the publication, writing, and video sources and will be overwritten. The latest published notes and essays appear on the home page automatically; drafts do not.

## Publications

`data/publications.json` is the current source of truth for the publication archive. Each publication is an object like this:

```json
{
  "year": 2026,
  "date": "2026-08-09",
  "title": "Publication title",
  "authors": "First Author, James Steele",
  "type": "article",
  "category": "article",
  "venue": "Journal name",
  "url": "https://doi.org/10.xxxx/example",
  "full_text": "",
  "open_access": false
}
```

To add a publication, copy an existing object, place it in the correct date order, and change its fields. To correct or remove a publication, search this file by DOI or title and edit or delete the complete object. Keep the commas between objects and leave the file as valid JSON.

For a remotely hosted open copy, put its URL in `full_text`. To host an author-shareable PDF locally:

1. Give the PDF a short, descriptive filename and place it in `publications/`.
2. Set `full_text` to `/publications/filename.pdf`.
3. Optionally add `full_text_label`, such as `"Author manuscript"` or `"Preprint PDF"`.
4. Confirm that the version is one you are entitled to share before publishing it.

`data/publication_overrides.json` preserves local full-text links and other corrections when the catalogue is rebuilt from OpenAlex data. If you add a local PDF or correction to `data/publications.json`, make the equivalent DOI-keyed entry in the overrides file so a future bulk rebuild does not discard it.

After changing publication data, regenerate the displayed archive:

```sh
python scripts/render_quarto_data.py
```

For an occasional bulk rebuild from downloaded OpenAlex result pages:

```sh
python scripts/build_publications.py path/to/openalex-page-*.json --output data/publications.json
python scripts/render_quarto_data.py
```

Review the resulting changes before committing; external databases can introduce duplicates, changed titles, or less useful links.

## Videos

`data/videos.yaml` is the source of truth for the video library. Add a new video at the top in this form:

```yaml
- title: Video title
  url: https://www.youtube.com/watch?v=VIDEO_ID
  duration: 12:34
  category: Research talk
```

Edit or remove the corresponding four-line entry to update or remove a video. Categories are free text, but reusing existing labels keeps the archive consistent. Then regenerate the displayed archive:

```sh
python scripts/render_quarto_data.py
```

The GitHub deployment also runs this generator automatically, but running it locally lets you inspect the updated archive in preview before publishing.

## Write a short note

Notes are intended for short observations, links, working ideas, research updates, or compact commentary. Create a dated page bundle, for example:

```text
notes/2026/08/my-note/index.qmd
```

In RStudio, create the folders through the Files pane, copy `templates/note.qmd` to the new folder, and edit it. Alternatively, from a PowerShell terminal:

```powershell
New-Item -ItemType Directory -Path "notes/2026/08/my-note"
Copy-Item "templates/note.qmd" "notes/2026/08/my-note/index.qmd"
```

Replace the template title, description, and `YYYY-MM-DD` date. Leave `kind: "Note"` and `draft: true` while writing.

## Write a long-form essay

Essays use the same page-bundle approach, for example:

```text
essays/2026/my-essay/index.qmd
```

Copy `templates/essay.qmd` into the new folder. Images, data, bibliographies, and other supporting files can live beside `index.qmd`, keeping each essay self-contained.

Useful Quarto patterns include:

```markdown
![A descriptive caption](figure.png)

An in-text citation [@citation-key].

## A section heading
```

For citations, add this to the essay's YAML header and place the bibliography beside the essay:

```yaml
bibliography: references.bib
```

Quarto also supports equations, footnotes, cross-references, callouts, figures, tables, and executable R, Python, or Julia code cells. To give a long essay its own table of contents, add:

```yaml
toc: true
```

The project uses `freeze: auto`. If a post contains executable code, render it locally and commit both its source/supporting files and any generated `_freeze/` output. This allows GitHub to publish the computed result without needing your complete local analytical environment.

## Move a draft to publication

For either a note or an essay:

1. Preview it locally and check links, figures, citations, and mobile-width layout.
2. Replace `draft: true` with `draft: false`, or remove the `draft` line.
3. Run `quarto render` for a final production check.
4. Commit and push the source to `master`.

The post will automatically appear in the combined Writing page and in its Notes or Essays index. Its title, description, date, and kind come from the YAML header.

## Publish changes

You can use RStudio's Git pane:

1. Review the changed files.
2. Stage the files that belong to the update.
3. Commit with a short description.
4. Push to GitHub.

Or use the RStudio Terminal:

```sh
git status
git add path/to/changed-file
git commit -m "Describe the website update"
git push origin master
```

Pushing to `master` runs `.github/workflows/quarto.yaml`. GitHub regenerates the research and video fragments, renders `_site/`, and deploys it to GitHub Pages. Deployment progress is visible in the repository's **Actions** tab. The repository's **Settings → Pages → Build and deployment → Source** must remain set to **GitHub Actions**.

Routine wording or post changes therefore follow this loop:

```text
Open website.Rproj → edit .qmd files → preview → render → commit → push
```

Publication and video changes add one step:

```text
Edit data → regenerate includes → preview → render → commit → push
```

The previous Wowchemy/Hugo site remains recoverable from Git history.
