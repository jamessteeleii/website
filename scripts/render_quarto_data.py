"""Render publication and video data into static Quarto include fragments."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INCLUDES = ROOT / "includes"


def esc(value: object, *, quote: bool = True) -> str:
    return html.escape(str(value or ""), quote=quote)


def parse_simple_yaml(path: Path) -> list[dict[str, str]]:
    """Parse the deliberately flat list-of-mappings used by videos.yaml."""
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- "):
            if current:
                records.append(current)
            current = {}
            line = line[2:]
        key, value = line.split(":", 1)
        current[key.strip()] = value.strip()
    if current:
        records.append(current)
    return records


def local_link(url: str, depth: int = 1) -> str:
    if url.startswith("/publications/"):
        return "../" * depth + url.lstrip("/")
    return url


def humanize(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").strip().capitalize()


def research_item(work: dict, *, compact: bool = False) -> str:
    heading = "h3" if compact else "h2"
    title = esc(work["title"])
    if compact:
        title_markup = f'<a href="{esc(work["url"])}">{title}</a>'
        source = esc(work.get("venue") or humanize(work.get("type", "other")))
        details = f"<p>{source}</p>"
        attributes = ""
    else:
        search = " ".join(
            str(work.get(key, "")) for key in ("title", "authors", "venue")
        ).lower()
        attributes = (
            ' data-research-item'
            f' data-year="{esc(work.get("year"))}"'
            f' data-type="{esc(work.get("category", "other"))}"'
            f' data-search="{esc(search)}"'
        )
        title_markup = title
        venue = f'{esc(work.get("venue"))} · ' if work.get("venue") else ""
        links = [f'<a href="{esc(work["url"])}">Publication</a>']
        if work.get("full_text"):
            label = esc(work.get("full_text_label") or "Full text")
            links.append(f'<a href="{esc(local_link(work["full_text"]))}">{label}</a>')
        details = (
            f'<p class="research-authors">{esc(work.get("authors"))}</p>'
            f'<p class="research-source">{venue}{esc(humanize(work.get("type", "other")))}</p>'
            f'<div class="research-links">{"".join(links)}</div>'
        )
    return (
        f'<article class="research-item"{attributes}>'
        f'<div class="research-year">{esc(work.get("year"))}</div>'
        f'<div><{heading}>{title_markup}</{heading}>{details}</div>'
        "</article>"
    )


def render(publications: list[dict], videos: list[dict[str, str]]) -> None:
    years = list(dict.fromkeys(str(work["year"]) for work in publications))
    year_options = "".join(f'<option value="{esc(year)}">{esc(year)}</option>' for year in years)
    archive = "".join(research_item(work) for work in publications)
    research_html = f"""
<section class="section shell research-archive">
  <div class="archive-intro">
    <p><strong>{len(publications)} works</strong> matched through ORCID. DOI links lead to the publication record; full-text links point to indexed open copies or clearly labelled author-shareable versions.</p>
  </div>
  <div class="library-controls" aria-label="Filter research outputs">
    <label><span>Search</span><input id="research-search" type="search" placeholder="Title, author, or journal"></label>
    <label><span>Year</span><select id="research-year"><option value="">All years</option>{year_options}</select></label>
    <label><span>Type</span><select id="research-type"><option value="">All types</option><option value="article">Articles</option><option value="preprint">Preprints</option><option value="book">Books &amp; chapters</option><option value="other">Other</option></select></label>
  </div>
  <p id="research-count" class="result-count" aria-live="polite"></p>
  <div class="research-list" id="research-list">{archive}</div>
</section>
""".strip()

    video_cards = "".join(
        (
            '<article class="video-card">'
            f'<a class="video-link" href="{esc(video["url"])}" aria-label="Watch {esc(video["title"])}">'
            '<span class="play-mark" aria-hidden="true">▶</span>'
            f'<span class="video-duration">{esc(video.get("duration"))}</span></a>'
            f'<p class="video-kind">{esc(video.get("category"))}</p>'
            f'<h3><a href="{esc(video["url"])}">{esc(video["title"])}</a></h3>'
            "</article>"
        )
        for video in videos
    )
    video_html = f"""
<section class="section shell video-archive">
  <div class="section-heading"><div><p class="eyebrow">{len(videos)} videos</p><h2>Talks and lessons</h2></div></div>
  <div class="video-grid">{video_cards}</div>
</section>
""".strip()

    home_library = f"""
<section class="section shell home-library">
  <div class="section-heading"><div><p class="eyebrow">The work</p><h2>Research in several forms</h2></div></div>
  <div class="library-grid">
    <a class="library-card" href="research/"><span class="library-number">{len(publications)}</span><h3>Research outputs</h3><p>Articles, preprints, chapters, and open full texts.</p></a>
    <a class="library-card" href="videos/"><span class="library-number">{len(videos)}</span><h3>Videos</h3><p>Talks and lessons on science, methods, and statistics.</p></a>
    <a class="library-card" href="writing/"><span class="library-number">Short + long</span><h3>Writing</h3><p>Notes, essays, project updates, and developing ideas.</p></a>
  </div>
</section>
""".strip()

    latest = "".join(research_item(work, compact=True) for work in publications[:5])
    home_latest = f"""
<section class="section shell">
  <div class="section-heading"><div><p class="eyebrow">Recently published</p><h2>Latest research</h2></div><a class="text-link" href="research/">Full archive <span aria-hidden="true">→</span></a></div>
  <div class="research-list compact-research-list">{latest}</div>
</section>
""".strip()

    outputs = {
        "research-archive.html": research_html,
        "video-archive.html": video_html,
        "home-library.html": home_library,
        "home-latest.html": home_latest,
    }
    INCLUDES.mkdir(parents=True, exist_ok=True)
    for filename, contents in outputs.items():
        fenced = f"```{{=html}}\n{contents}\n```\n"
        (INCLUDES / filename).write_text(fenced, encoding="utf-8")
    print(f"Rendered {len(publications)} publications and {len(videos)} videos")


def main() -> None:
    publications = json.loads((ROOT / "data" / "publications.json").read_text(encoding="utf-8"))
    videos = parse_simple_yaml(ROOT / "data" / "videos.yaml")
    render(publications, videos)


if __name__ == "__main__":
    main()
