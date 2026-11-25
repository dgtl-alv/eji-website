"""Build, validate local links, and package only the public static site."""
import gzip
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.links, self.ids = [], set()
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.links.append(attrs[attr])


def validate(root):
    documents = {p: Document(p.read_text()) for p in root.rglob('*.html')}
    assert len(documents) == 6, 'Expected all six English and Indonesian pages'
    count = 0
    for page, document in documents.items():
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = ((root if url.path.startswith('/') else page.parent) / unquote(url.path).lstrip('/')).resolve() if url.path else page
            assert target.is_relative_to(root.resolve()), f'Link escapes output: {page}: {link}'
            if target.is_dir():
                target /= 'index.html'
            assert target.is_file(), f'Missing local target: {page}: {link}'
            if url.fragment and target in documents:
                assert unquote(url.fragment) in documents[target].ids, f'Missing anchor: {page}: {link}'
            count += 1
    for css in root.rglob('*.css'):
        for link in re.findall(r'url\([\s\"\x27]*([^\)\"\x27]+)', css.read_text()):
            if not urlsplit(link).scheme:
                assert (css.parent / unquote(link)).is_file(), f'Missing CSS asset: {link}'
    print(f'Validated {len(documents)} pages and {count} local links/assets')


def package(revision):
    assert re.fullmatch(r'[0-9a-f]{40}', revision), 'Expected a full commit SHA'
    output = ROOT / 'dist'
    site = output / 'site'
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    subprocess.run([sys.executable, str(ROOT / 'build.py'), str(site)], check=True)
    shutil.copytree(ROOT / 'assets', site / 'assets')
    validate(site)
    manifest = {'revision': revision, 'files': {str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(site.rglob('*')) if p.is_file()}}
    (site / 'release.json').write_text(json.dumps(manifest, sort_keys=True) + '\n')
    archive = output / 'site.tar.gz'
    with archive.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as tar:
        for path in sorted(site.rglob('*')):
            if not path.is_file() or path.is_symlink():
                assert not path.is_symlink(), f'Symlink is not a static asset: {path}'
                continue
            content = path.read_bytes()
            info = tarfile.TarInfo(str(path.relative_to(site)))
            info.size, info.mode, info.mtime = len(content), 0o644, 0
            tar.addfile(info, io.BytesIO(content))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / 'artifact.json').write_text(json.dumps({'revision': revision, 'digest': digest}) + '\n')
    print(f'Artifact: {archive.name}; revision: {revision}; sha256: {digest}')
    return archive


if __name__ == '__main__':
    package(sys.argv[1])
