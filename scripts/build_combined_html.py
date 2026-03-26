#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import yaml
from bs4 import BeautifulSoup


EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "data", "javascript"}
URL_ATTRS = {
    "a": ("href",),
    "img": ("src",),
    "source": ("src", "srcset"),
}


@dataclass
class Page:
    title: str
    source: str
    groups: list[str]
    slug: str
    html_path: Path
    top_anchor: str = ""
    anchor_map: dict[str, str] = field(default_factory=dict)
    toc_entries: list["TocEntry"] = field(default_factory=list)


@dataclass
class TocEntry:
    title: str
    anchor: str
    level: int
    children: list["TocEntry"] = field(default_factory=list)


def flatten_nav(nav: list[dict], site_dir: Path, groups: list[str] | None = None) -> list[Page]:
    groups = groups or []
    pages: list[Page] = []
    for item in nav:
        title, value = next(iter(item.items()))
        if isinstance(value, str):
            stem = value[:-3] if value.endswith(".md") else value
            slug = "index" if stem == "index" else stem.replace("/", "-")
            html_path = site_dir / ("index.html" if stem == "index" else str(Path(stem) / "index.html"))
            pages.append(Page(title=title, source=value, groups=groups[:], slug=slug, html_path=html_path))
        elif isinstance(value, list):
            pages.extend(flatten_nav(value, site_dir, [*groups, title]))
    return pages


def copy_static_asset(source: Path, site_dir: Path, html_dir: Path) -> str:
    target = html_dir / "assets" / "site" / source.relative_to(site_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
    return target.relative_to(html_dir).as_posix()


def is_external(url: str) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in EXTERNAL_SCHEMES or url.startswith("//")


def resolve_site_target(page: Page, raw_path: str, site_dir: Path) -> Path | None:
    raw_path = raw_path or ""
    base = page.html_path.parent

    candidate_paths: list[Path] = [(base / raw_path).resolve()]
    trimmed = raw_path
    while trimmed.startswith("../"):
        trimmed = trimmed[3:]
    if trimmed and trimmed != raw_path:
        candidate_paths.append((site_dir / trimmed).resolve())
    if raw_path.startswith("./"):
        candidate_paths.append((site_dir / raw_path[2:]).resolve())

    seen: set[Path] = set()
    for candidate in candidate_paths:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_dir():
            index_candidate = candidate / "index.html"
            if index_candidate.exists():
                return index_candidate
            return candidate
        if candidate.exists():
            return candidate
        if raw_path.endswith("/"):
            index_candidate = candidate / "index.html"
            if index_candidate.exists():
                return index_candidate
        if candidate.suffix == "":
            html_candidate = candidate / "index.html"
            if html_candidate.exists():
                return html_candidate
        if candidate.suffix == ".html" and candidate.exists():
            return candidate
        if candidate.is_relative_to(site_dir):
            return candidate
    return None


def make_page_lookup(pages: list[Page]) -> tuple[dict[Path, Page], dict[Path, Page]]:
    dir_map: dict[Path, Page] = {}
    file_map: dict[Path, Page] = {}
    for page in pages:
        dir_map[page.html_path.parent.resolve()] = page
        file_map[page.html_path.resolve()] = page
    return dir_map, file_map


def prefix_ids(article: BeautifulSoup, page: Page) -> None:
    for tag in article.select("[id]"):
        if tag.find_parent("svg") is not None:
            continue
        old_id = tag.get("id")
        if not old_id:
            continue
        new_id = f"{page.slug}--{old_id}"
        page.anchor_map[old_id] = new_id
        tag["id"] = new_id

    first_heading = article.find(["h1", "h2", "h3"])
    if first_heading is None:
        first_heading = BeautifulSoup("", "html.parser").new_tag("h1")
        first_heading.string = page.title
        article.insert(0, first_heading)

    if not first_heading.get("id"):
        first_heading["id"] = f"{page.slug}--top"
    page.top_anchor = first_heading["id"]


def rewrite_fragment_link(fragment: str, page: Page) -> str:
    if not fragment:
        return f"#{page.top_anchor}"
    return f"#{page.anchor_map.get(fragment, f'{page.slug}--{fragment}')}"


def rewrite_links_and_assets(
    article: BeautifulSoup,
    page: Page,
    html_dir: Path,
    site_dir: Path,
    page_dirs: dict[Path, Page],
    page_files: dict[Path, Page],
) -> None:
    for anchor in article.select("a.headerlink"):
        anchor.decompose()

    for tag in article.find_all("a"):
        value = tag.get("href") or tag.get("xlink:href")
        if not value or is_external(value):
            continue

        parsed = urlparse(value)
        target_path = parsed.path
        fragment = parsed.fragment

        rewritten = None
        if not target_path:
            rewritten = rewrite_fragment_link(fragment, page)
        else:
            resolved = resolve_site_target(page, target_path, site_dir)
            if resolved is not None:
                resolved = resolved.resolve()
                target_page = page_files.get(resolved) or page_dirs.get(resolved)
                if target_page is None and resolved.is_dir():
                    target_page = page_dirs.get(resolved)
                if target_page is not None:
                    rewritten = rewrite_fragment_link(fragment, target_page)
                elif resolved.exists() and resolved.is_relative_to(site_dir):
                    asset_href = copy_static_asset(resolved, site_dir, html_dir)
                    rewritten = urlunparse(parsed._replace(path=asset_href))

        if rewritten is None:
            continue
        if "href" in tag.attrs:
            tag["href"] = rewritten
        if "xlink:href" in tag.attrs:
            tag["xlink:href"] = rewritten

    for tag in article.find_all(True):
        if tag.name == "a":
            continue
        attrs = URL_ATTRS.get(tag.name, ())
        for attr in attrs:
            value = tag.get(attr)
            if not value or attr == "srcset" or is_external(value):
                continue

            parsed = urlparse(value)
            target_path = parsed.path
            resolved = resolve_site_target(page, target_path, site_dir)
            if resolved is None or not resolved.exists() or not resolved.is_relative_to(site_dir):
                continue
            tag[attr] = urlunparse(parsed._replace(path=copy_static_asset(resolved, site_dir, html_dir)))


def collect_toc_entries(article: BeautifulSoup, page: Page) -> None:
    entries: list[TocEntry] = []
    stack: list[TocEntry] = []
    for heading in article.find_all(["h1", "h2", "h3"]):
        anchor = heading.get("id")
        title = " ".join(heading.stripped_strings)
        if not anchor or not title:
            continue
        entry = TocEntry(title=title, anchor=anchor, level=int(heading.name[1]))
        while stack and stack[-1].level >= entry.level:
            stack.pop()
        if stack:
            stack[-1].children.append(entry)
        else:
            entries.append(entry)
        stack.append(entry)
    page.toc_entries = entries or [TocEntry(title=page.title, anchor=page.top_anchor, level=1)]


def render_toc_entries(entries: list[TocEntry], level: int = 1) -> str:
    lines = [f'<ol class="book-toc__list book-toc__list--level-{level}">']
    for entry in entries:
        lines.append("<li>")
        lines.append(f'<a href="#{entry.anchor}"><span>{entry.title}</span></a>')
        if entry.children:
            lines.append(render_toc_entries(entry.children, level + 1))
        lines.append("</li>")
    lines.append("</ol>")
    return "\n".join(lines)


def render_nav_toc(pages: list[Page]) -> str:
    lines = ['<nav class="book-toc" aria-label="Document contents">', '<h2>Table of contents</h2>']
    current_group: tuple[str, ...] | None = None
    for page in pages:
        groups = tuple(page.groups)
        if groups != current_group:
            label = " / ".join(groups) if groups else "Overview"
            lines.append(f'<h3 class="book-toc__group">{label}</h3>')
            current_group = groups
        lines.append(render_toc_entries(page.toc_entries))
    lines.append("</nav>")
    return "\n".join(lines)


def render_cover(site_name: str, site_description: str) -> str:
    today = date.today().strftime("%B %d, %Y")
    return f"""
<section class="cover" id="cover">
  <p class="cover__eyebrow">BYU Capstone Team 33</p>
  <h1>{site_name}</h1>
  <p class="cover__summary">{site_description}</p>
  <dl class="cover__meta">
    <div><dt>Prepared By</dt><dd>BYU Capstone Team 33</dd></div>
    <div><dt>Generated</dt><dd>{today}</dd></div>
    <div><dt>Format</dt><dd>Paged.js PDF</dd></div>
  </dl>
</section>
""".strip()


def page_markup(page: Page, article: BeautifulSoup) -> str:
    kicker = ""
    if page.groups:
        kicker = f'<p class="doc-page__kicker">{" / ".join(page.groups)}</p>'
    page_classes = ["doc-page"]
    if article.select_one(".architecture-diagram-shell"):
        page_classes.append("doc-page--has-diagram")
    return f"""
<section class="{' '.join(page_classes)}" id="page-{page.slug}" data-page-title="{page.title}">
  {kicker}
  {article.decode_contents()}
</section>
""".strip()


def build_paged_variant(
    site_name: str,
    site_description: str,
    pages: list[Page],
    sections: list[str],
    html_dir: Path,
) -> None:
    cover = render_cover(site_name, site_description)
    toc = render_nav_toc(pages)
    body = "\n".join(sections)

    paged_html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="author" content="BYU Capstone Team 33">
    <title>{site_name}</title>
    <link rel="stylesheet" href="assets/styles/base.css">
    <link rel="stylesheet" href="assets/styles/paged.css">
  </head>
  <body class="export export-paged">
    <main class="book">
      {cover}
      {toc}
      {body}
    </main>
  </body>
</html>
"""
    (html_dir / "combined-paged.html").write_text(paged_html, encoding="utf-8")


def copy_styles(repo_root: Path, html_dir: Path) -> None:
    styles_dir = html_dir / "assets" / "styles"
    styles_dir.mkdir(parents=True, exist_ok=True)
    for name in ("base.css", "paged.css"):
        shutil.copy2(repo_root / "export-styles" / name, styles_dir / name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="mkdocs.yml")
    parser.add_argument("--site-dir", default="site")
    parser.add_argument("--output-dir", default=".pdf-build/html")
    args = parser.parse_args()

    repo_root = Path.cwd()
    config_path = repo_root / args.config
    site_dir = (repo_root / args.site_dir).resolve()
    html_dir = (repo_root / args.output_dir).resolve()

    if html_dir.exists():
        shutil.rmtree(html_dir)
    html_dir.mkdir(parents=True, exist_ok=True)

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    pages = flatten_nav(config["nav"], site_dir)
    page_dirs, page_files = make_page_lookup(pages)
    page_articles: dict[str, BeautifulSoup] = {}

    for page in pages:
        source_html = page.html_path
        page_soup = BeautifulSoup(source_html.read_text(encoding="utf-8"), "html.parser")
        article = page_soup.select_one("article.md-content__inner")
        if article is None:
            raise RuntimeError(f"Could not locate article body in {source_html}")

        article_copy = BeautifulSoup(str(article), "html.parser")
        article_root = article_copy.select_one("article.md-content__inner")
        assert article_root is not None
        prefix_ids(article_root, page)
        page_articles[page.slug] = article_root

    sections: list[str] = []
    for page in pages:
        article_root = page_articles[page.slug]
        rewrite_links_and_assets(article_root, page, html_dir, site_dir, page_dirs, page_files)
        collect_toc_entries(article_root, page)
        sections.append(page_markup(page, article_root))

    copy_styles(repo_root, html_dir)
    build_paged_variant(config["site_name"], config.get("site_description", ""), pages, sections, html_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
