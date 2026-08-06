# -*- coding: utf-8 -*-
"""
Generates sitemap.xml — tells Google (and other search engines) about every
URL on the site, so Search Console can discover and index all 650+ word
pages much faster than waiting for organic crawling to find them one by one.

Run any time the word list changes (also wired into the GitHub Actions
rebuild, so this stays in sync automatically).
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
sys.path.insert(0, SCRIPT_DIR)
import build_kslang_db as db

SITE_URL = "https://hellokslang.com"

# Static, hand-authored pages. (privacy.html is intentionally excluded —
# it's a legal page, not content Google needs to prioritize crawling.)
STATIC_PAGES = [
    ("", "1.0", "daily"),              # homepage
    ("category.html", "0.9", "weekly"),
    ("trending.html", "0.7", "weekly"),
    ("whatsnew.html", "0.8", "daily"),
    ("submit.html", "0.5", "monthly"),
    ("about.html", "0.6", "monthly"),
    ("contact.html", "0.4", "monthly"),
]


def slugify(rom):
    import re
    s = rom.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def main():
    urls = []
    for path, priority, freq in STATIC_PAGES:
        urls.append((f"{SITE_URL}/{path}", priority, freq))

    total_words = 0
    for cat_kr, cat_en, terms in db.CATEGORIES:
        for t in terms:
            rom = t[1]
            slug = slugify(rom)
            urls.append((f"{SITE_URL}/word/{slug}.html", "0.6", "monthly"))
            total_words += 1

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url, priority, freq in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")

    out_path = os.path.join(REPO_ROOT, "sitemap.xml")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"sitemap.xml generated: {len(STATIC_PAGES)} static pages + {total_words} word pages = {len(urls)} URLs total")


if __name__ == "__main__":
    main()
