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
# Pages that are published but not yet in effect: must carry noindex + DRAFT
# banner and must not be linked from the index page.
DRAFTS = ["strike-log/privacy/index.html", "bounce-tower/privacy/index.html"]
# Sensitive / internal strings that must never reach the public repo.
# Some literals are split so this file does not match itself.
SECRET_PATTERNS = {
    "company mail/domain": re.compile("imsmobil" + "ity", re.I),
    "local user path": re.compile(r"/Users/|C:\\\\Users\\\\|/home/[a-z]"),
    "private key": re.compile("-----BEGIN [A-Z ]*PRIVATE" + " KEY-----"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
    "GitHub token": re.compile(r"gh[pousr]_[0-9A-Za-z]{30,}"),
    "AWS key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "Slack/Discord webhook": re.compile(r"hooks\.slack\.com/services|discord(?:app)?\.com/api/webhooks"),
    "JWT": re.compile(r"eyJ[0-9A-Za-z_\-]{10,}\.eyJ[0-9A-Za-z_\-]{10,}\."),
    "AdMob real unit id": re.compile(r"ca-app-pub-(?!3940256099942544)\d{16}"),
    "password assignment": re.compile(r"(?i)(password|passwd|secret|token)\s*[:=]\s*['\"][^'\"]{6,}"),
    "private IP": re.compile(r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}"),
}
SKIP_DIRS = {".git", ".omc", "__pycache__"}
FORBIDDEN_FILES = re.compile(r"(\.env|\.jks|\.keystore|key\.properties|google-services\.json|GoogleService-Info\.plist)$")


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
        elif href.startswith("mailto:"):
            if not re.fullmatch(r"mailto:[^@\s]+@[^@\s]+\.[a-z]{2,}", href):
                errs.append(f"bad mailto {href}")
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


def scan_secrets():
    """Scan every file that would be published (everything except SKIP_DIRS)."""
    errs, scanned = [], 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            path = os.path.join(root, name)
            if FORBIDDEN_FILES.search(name):
                errs.append(f"forbidden file {path}")
                continue
            try:
                text = open(path, encoding="utf-8").read()
            except UnicodeDecodeError:
                errs.append(f"binary file {path}")
                continue
            scanned += 1
            for label, pat in SECRET_PATTERNS.items():
                m = pat.search(text)
                if m:
                    errs.append(f"{label} in {path}: {m.group(0)[:40]!r}")
    return scanned, errs


def check_drafts():
    errs = []
    index = open("index.html", encoding="utf-8").read()
    for f in DRAFTS:
        src = open(f, encoding="utf-8").read()
        if not re.search(r'<meta name="robots" content="noindex">', src):
            errs.append(f"{f}: missing noindex")
        if "DRAFT — not yet in effect" not in src:
            errs.append(f"{f}: missing DRAFT banner")
        link = f.replace("index.html", "")
        if f'href="{link}"' in index:
            errs.append(f"index.html links draft page {link}")
    return errs


def main():
    ok = True
    all_ph = {}
    for f in FILES:
        p, errs, ph = check(f)
        if f not in DRAFTS and ph:
            errs.append(f"{len(ph)} placeholder(s) left in a published page")
        for x in ph:
            all_ph[x] = all_ph.get(x, 0) + 1
        status = "OK" if not errs else "; ".join(errs)
        print(f"{f}: sections en={p.h2['en']} ko={p.h2['ko']} links={len(p.hrefs)} placeholders={len(ph)} -> {status}")
        ok = ok and not errs
    derrs = check_drafts()
    print(f"\nDraft isolation ({len(DRAFTS)} pages): " + ("OK" if not derrs else "; ".join(derrs)))
    ok = ok and not derrs
    scanned, serrs = scan_secrets()
    print(f"Secret/internal-info scan ({scanned} files): " + ("OK" if not serrs else ""))
    for e in serrs:
        print(f"  - {e}")
    ok = ok and not serrs
    print("\nPlaceholders to fill before publishing (draft pages only):")
    for k, v in sorted(all_ph.items()):
        print(f"  {v:3d}  {k}")
    print("\nALL OK" if ok else "\nFAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
