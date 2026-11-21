"""Static checks for the policy pages. Run from the repo root:

    python3 tools/check_policies.py

Checks: tag balance, no external resources/JS, anchors and relative links
resolve, rel=noopener on external links, EN/KO section counts match,
no "(추정)" left, and lists remaining placeholders.
"""
import os
import re
import sys
from html.parser import HTMLParser

VOID = {"meta", "br", "link", "img", "hr", "input"}
FILES = [
    "index.html",
    "strike-log/privacy/index.html",
    "bounce-tower/privacy/index.html",
    "plain-focus/privacy/index.html",
]
PLACEHOLDER = re.compile(r"\[대표 확인 필요: [^\]]+\]")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.errors, self.ids, self.hrefs = [], [], [], []
        self.h2 = {"en": 0, "ko": 0}
        self.lang = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append((a["href"], a.get("rel")))
        if tag == "section":
            self.lang = a.get("lang")
        if tag == "h2" and self.lang in self.h2 and "langhead" not in (a.get("class") or ""):
            self.h2[self.lang] += 1
        if tag in ("script", "link", "img", "iframe"):
            self.errors.append(f"forbidden <{tag}>")
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"mismatched </{tag}> near {self.stack[-3:]}")
        else:
            self.stack.pop()
        if tag == "section":
            self.lang = None


def check(path):
    src = open(path, encoding="utf-8").read()
    p = Page()
    p.feed(src)
    errs = list(p.errors)
    if p.stack:
        errs.append(f"unclosed {p.stack}")
    dup = {i for i in p.ids if p.ids.count(i) > 1}
    if dup:
        errs.append(f"duplicate ids {dup}")
    if re.search(r"@import|url\(|\ssrc=", src):
        errs.append("external resource reference")
    if "(추정)" in src:
        errs.append("'(추정)' left in page")
    for href, rel in p.hrefs:
        if href.startswith("http"):
            if rel != "noopener":
                errs.append(f"missing rel=noopener: {href}")
        elif href.startswith("#"):
            if href[1:] not in p.ids:
                errs.append(f"broken anchor {href}")
        else:
            target = os.path.normpath(os.path.join(os.path.dirname(path), href, "index.html"))
            if not os.path.exists(target):
                errs.append(f"broken link {href}")
    for need in ("<!DOCTYPE html>", 'charset="utf-8"', 'name="viewport"', '<html lang="en">', "<title>"):
        if need not in src:
            errs.append(f"missing {need}")
    if path != "index.html" and p.h2["en"] != p.h2["ko"]:
        errs.append(f"EN/KO section count differs {p.h2}")
    return p, errs, PLACEHOLDER.findall(src)


def main():
    ok = True
    all_ph = {}
    for f in FILES:
        p, errs, ph = check(f)
        for x in ph:
            all_ph[x] = all_ph.get(x, 0) + 1
        status = "OK" if not errs else "; ".join(errs)
        print(f"{f}: sections en={p.h2['en']} ko={p.h2['ko']} links={len(p.hrefs)} placeholders={len(ph)} -> {status}")
        ok = ok and not errs
    print("\nPlaceholders to fill before publishing:")
    for k, v in sorted(all_ph.items()):
        print(f"  {v:3d}  {k}")
    print("\nALL OK" if ok else "\nFAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
