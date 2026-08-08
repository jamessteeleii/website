"""Inventory local publication PDFs and match them to the website catalogue.

This produces an audit file only. It deliberately does not decide that possession of
a publisher PDF grants redistribution rights.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from pypdf import PdfReader


DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
LICENSE_PATTERNS = {
    "cc_by": re.compile(r"creative\s+commons\s+attribution|CC\s*BY(?:\s|[-–]NC|[-–]ND|[-–]SA|$)", re.I),
    "open_access": re.compile(r"open\s+access", re.I),
}
VERSION_PATTERNS = {
    "accepted_manuscript": re.compile(
        r"accepted\s+(?:author\s+)?manuscript|author(?:'s)?\s+accepted\s+(?:version|manuscript)|post[- ]print",
        re.I,
    ),
    "preprint": re.compile(r"preprint|sportRxiv|medRxiv|bioRxiv|PsyArXiv|OSF\s+Preprints", re.I),
    "proof": re.compile(r"uncorrected\s+proof|journal\s+pre[- ]proof|proof\s+copy", re.I),
    "publisher_version": re.compile(
        r"©\s*(?:19|20)\d{2}|all\s+rights\s+reserved|published\s+by\s+Elsevier|Springer\s+Nature|Taylor\s*&\s*Francis|Wiley",
        re.I,
    ),
}
STOP_WORDS = {
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "upon", "with",
}


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def title_tokens(value: str) -> set[str]:
    return {token for token in normalize(value).split() if token not in STOP_WORDS and len(token) > 1}


def title_score(candidate: str, title: str) -> float:
    a, b = normalize(candidate), normalize(title)
    if not a or not b:
        return 0.0
    ta, tb = title_tokens(a), title_tokens(b)
    overlap = len(ta & tb) / max(1, len(ta | tb))
    sequence = SequenceMatcher(None, a, b).ratio()
    containment = min(len(ta & tb) / max(1, len(ta)), len(ta & tb) / max(1, len(tb)))
    return round(max(sequence, overlap, containment), 4)


def clean_doi(value: str) -> str:
    return value.rstrip(".,;:)]}").lower()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_pdf(path: Path) -> dict:
    record: dict = {
        "path": str(path),
        "filename": path.name,
        "size_bytes": path.stat().st_size,
        "sha256": file_hash(path),
        "page_count": None,
        "metadata_title": "",
        "metadata_author": "",
        "dois": [],
        "years": [],
        "version_signals": [],
        "license_signals": [],
        "mentions_james_steele": False,
        "read_error": "",
    }
    try:
        reader = PdfReader(str(path), strict=False)
        record["page_count"] = len(reader.pages)
        metadata = reader.metadata or {}
        record["metadata_title"] = str(metadata.get("/Title") or "").strip()
        record["metadata_author"] = str(metadata.get("/Author") or "").strip()
        chunks = []
        for page in list(reader.pages[:3]) + list(reader.pages[-1:]):
            try:
                chunks.append(page.extract_text() or "")
            except Exception:
                continue
        text = "\n".join(chunks)
        record["dois"] = list(dict.fromkeys(clean_doi(match) for match in DOI_RE.findall(text)))
        record["years"] = sorted(set(YEAR_RE.findall(text)))
        record["mentions_james_steele"] = bool(
            re.search(r"James\s+(?:R\.\s+|L\.\s+)?Steele|Steele,\s*James|J\.\s*(?:R\.\s+|L\.\s+)?Steele", text, re.I)
        )
        record["version_signals"] = [name for name, pattern in VERSION_PATTERNS.items() if pattern.search(text)]
        record["license_signals"] = [name for name, pattern in LICENSE_PATTERNS.items() if pattern.search(text)]
    except Exception as exc:
        record["read_error"] = f"{type(exc).__name__}: {exc}"
    return record


def catalogue_doi(item: dict) -> str:
    value = item.get("url", "")
    return clean_doi(value.split("doi.org/", 1)[1]) if "doi.org/" in value else ""


def match_record(record: dict, catalogue: list[dict]) -> None:
    pdf_dois = set(record["dois"])
    exact = [item for item in catalogue if catalogue_doi(item) in pdf_dois and catalogue_doi(item)]
    names = [record["metadata_title"], Path(record["filename"]).stem]
    if exact:
        best = max(exact, key=lambda item: max(title_score(name, item["title"]) for name in names))
        exact_title_score = max(title_score(name, best["title"]) for name in names)
        method, score = ("doi", 1.0) if exact_title_score >= 0.45 else ("unmatched", exact_title_score)
    else:
        ranked = sorted(
            ((max(title_score(name, item["title"]) for name in names), item) for item in catalogue),
            key=lambda pair: pair[0],
            reverse=True,
        )
        score, best = ranked[0]
        method = "title" if score >= 0.72 else "unmatched"
    record["match_method"] = method
    record["match_score"] = score
    record["catalogue_title"] = best["title"] if method != "unmatched" else ""
    record["catalogue_url"] = best["url"] if method != "unmatched" else ""
    record["catalogue_year"] = best["year"] if method != "unmatched" else None
    record["catalogue_open_access"] = best["open_access"] if method != "unmatched" else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_root", type=Path)
    parser.add_argument("catalogue", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    records = []
    for path in sorted(args.pdf_root.rglob("*.pdf"), key=lambda item: str(item).lower()):
        record = inspect_pdf(path)
        match_record(record, catalogue)
        records.append(record)

    duplicate_groups = {}
    for record in records:
        duplicate_groups.setdefault(record["sha256"], []).append(record["path"])
    summary = {
        "pdf_count": len(records),
        "read_errors": sum(bool(item["read_error"]) for item in records),
        "doi_matches": sum(item["match_method"] == "doi" for item in records),
        "title_matches": sum(item["match_method"] == "title" for item in records),
        "unmatched": sum(item["match_method"] == "unmatched" for item in records),
        "exact_duplicate_groups": sum(len(paths) > 1 for paths in duplicate_groups.values()),
        "license_signals": sum(bool(item["license_signals"]) for item in records),
        "accepted_manuscript_signals": sum("accepted_manuscript" in item["version_signals"] for item in records),
        "preprint_signals": sum("preprint" in item["version_signals"] for item in records),
    }
    output = {"summary": summary, "records": records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
