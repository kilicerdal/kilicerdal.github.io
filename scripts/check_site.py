"""Check this site's explicit HTML subset and internal destinations without network access."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
REQUIRED = {
    'index.html': ['Application Features', 'Privacy and Contact'],
    'privacy.html': ['Information Accessed', 'How Information Is Used', 'Data Storage and Processing', 'Data Sharing', 'Security', 'Data Retention and Deletion', 'Contact'],
    'terms.html': ['Application Purpose', 'Authorized Use', 'Google Services', 'AI-Generated Results', 'Availability', 'Privacy', 'Contact'],
}


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack, self.tags, self.links, self.ids, self.dates, self.errors = [], [], [], set(), [], []
        self.text, self.headings = [], []
        self.heading = None
        self.doctype = False
        self.language = False
        self.feed(source)
        self.close()
        if self.stack:
            self.errors.append('Unclosed tags: ' + ', '.join(self.stack))

    def handle_decl(self, decl):
        self.doctype = decl.casefold() == 'doctype html'

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'html':
            self.language = attrs.get('lang') == 'en'
        if tag == 'h2':
            self.heading = []
        if attrs.get('id'):
            if attrs['id'] in self.ids:
                self.errors.append('Duplicate id: ' + attrs['id'])
            self.ids.add(attrs['id'])
        if tag == 'a':
            if not attrs.get('href'):
                self.errors.append('Anchor has no destination')
            else:
                self.links.append(attrs['href'])
        if tag == 'time':
            self.dates.append(attrs.get('datetime', ''))
        if tag in {'script', 'iframe', 'form'}:
            self.errors.append('This information site must not embed executable services: ' + tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append('Mismatched closing tag: ' + tag)
        else:
            self.stack.pop()
        if tag == 'h2' and self.heading is not None:
            self.headings.append(''.join(self.heading).casefold())
            self.heading = None

    def handle_data(self, data):
        self.text.append(data)
        if self.heading is not None:
            self.heading.append(data)


def check(root):
    root = Path(root).resolve()
    errors, pages = [], {}
    for name, headings in REQUIRED.items():
        path = root / name
        if not path.is_file():
            errors.append(name + ': missing required page')
            continue
        source = path.read_text(encoding='utf-8')
        page = pages[name] = Page(source)
        errors.extend(name + ': ' + error for error in page.errors)
        if not page.doctype or not page.language:
            errors.append(name + ': requires HTML doctype and English language')
        for tag in ['html', 'head', 'title', 'body', 'main', 'h1']:
            if page.tags.count(tag) != 1:
                errors.append(name + ': requires exactly one ' + tag)
        for heading in headings:
            if not any(heading.casefold() in text for text in page.headings):
                errors.append(name + ': missing disclosure section ' + heading)
        text = ' '.join(page.text).casefold()
        for phrase in ['static information site', 'separate private application', 'last reviewed:', 'erdal.kilic.us@gmail.com']:
            if phrase not in text:
                errors.append(name + ': missing scope/review metadata ' + phrase)
        if len(page.dates) != 1:
            errors.append(name + ': requires one machine-readable review date')
        for value in page.dates:
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value) or date.fromisoformat(value) > date.today():
                    raise ValueError(value)
            except ValueError:
                errors.append(name + ': invalid or future review date')
    for name, page in pages.items():
        for href in page.links:
            link = urlsplit(href)
            if link.scheme or link.netloc:
                if link.scheme not in {'https', 'mailto'}:
                    errors.append(name + ': unsupported link scheme')
                continue
            target = (root / unquote(link.path or name)).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                errors.append(name + ': broken internal link ' + href)
            elif link.fragment:
                target_page = Page(target.read_text(encoding='utf-8'))
                if unquote(link.fragment) not in target_page.ids:
                    errors.append(name + ': missing internal fragment ' + href)
    return errors


if __name__ == '__main__':
    problems = check(Path(__file__).resolve().parents[1])
    for problem in problems:
        print('FAIL ' + problem)
    if not problems:
        print('PASS: three information pages, HTML structure, local links and disclosure metadata')
    raise SystemExit(bool(problems))
