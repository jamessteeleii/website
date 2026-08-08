"""Build Quarto publication data from downloaded OpenAlex result pages."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


def category(work_type: str) -> str:
    if work_type in {"article", "review", "editorial", "letter"}:
        return "article"
    if work_type in {"preprint", "posted-content"}:
        return "preprint"
    if work_type in {"book", "book-chapter", "monograph", "reference-entry"}:
        return "book"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path("data/publication_overrides.json"),
        help="Optional fields keyed by publication URL (defaults to data/publication_overrides.json)",
    )
    args = parser.parse_args()

    by_title: dict[str, dict] = {}
    for input_path in args.inputs:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        for work in payload.get("results", []):
            title = html.unescape(re.sub(r"<[^>]+>", "", work.get("title") or "Untitled"))
            key = re.sub(r"[^a-z0-9]+", "", title.casefold())
            if not key:
                continue

            location = work.get("primary_location") or {}
            best_oa = work.get("best_oa_location") or {}
            source = location.get("source") or {}
            authors = ", ".join(
                item.get("author", {}).get("display_name", "")
                for item in work.get("authorships", [])
                if item.get("author", {}).get("display_name")
            )
            work_type = work.get("type") or "other"
            doi = work.get("doi")
            record = {
                    "year": work.get("publication_year") or "Undated",
                    "date": work.get("publication_date") or "",
                    "title": title,
                    "authors": authors,
                    "type": work_type,
                    "category": category(work_type),
                    "venue": source.get("display_name") or "",
                    "url": doi or location.get("landing_page_url") or work.get("id"),
                    "full_text": best_oa.get("pdf_url") or "",
                    "open_access": bool((work.get("open_access") or {}).get("is_oa")),
                }
            existing = by_title.get(key)
            score = (
                category(work_type) in {"article", "book"},
                bool(record["venue"]),
                bool(record["full_text"]),
                bool(record["url"]),
            )
            if existing:
                existing_score = (
                    existing["category"] in {"article", "book"},
                    bool(existing["venue"]),
                    bool(existing["full_text"]),
                    bool(existing["url"]),
                )
                if score <= existing_score:
                    continue
            by_title[key] = record

    records = list(by_title.values())
    if args.overrides.exists():
        overrides = json.loads(args.overrides.read_text(encoding="utf-8"))
        for record in records:
            record.update(overrides.get(record["url"], {}))
    records.sort(key=lambda item: (str(item["date"]), item["title"]), reverse=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(records)} works to {args.output}")


if __name__ == "__main__":
    main()
