"""Installed by an administrator. Never execute code from deployment artifacts."""
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request

ROOT = Path('/opt/electrajaringan')
LIMIT = 25 * 1024 * 1024


def extract(archive, target, revision):
    seen, size = set(), 0
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            assert member.isfile() and not member.issym(), 'Only regular files are accepted'
            assert not path.is_absolute() and '..' not in path.parts and path.parts, 'Unsafe archive path'
            assert not any(part.startswith('.') for part in path.parts), 'Hidden files are not public assets'
            assert member.name not in seen, 'Duplicate archive path'
            assert member.name == 'release.json' or (path.suffix in {'.html', '.css', '.png', '.webp', '.svg', '.otf', '.woff', '.woff2', '.jpg', '.jpeg', '.ico', '.js'} and (len(path.parts) == 1 or path.parts[0] in {'assets', 'id'})), 'Unexpected public asset'
            seen.add(member.name)
            size += member.size
            assert len(seen) <= 1000 and size <= LIMIT, 'Artifact exceeds size limits'
            destination = target.joinpath(*path.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tar.extractfile(member) as source, destination.open('xb') as output:
                shutil.copyfileobj(source, output)
            destination.chmod(0o644)
    manifest = json.loads((target / 'release.json').read_text())
    assert manifest['revision'] == revision, 'Artifact revision mismatch'
    assert set(manifest['files']) == seen - {'release.json'}, 'Manifest inventory mismatch'
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((target / name).read_bytes()).hexdigest() == digest, f'Corrupt file: {name}'
    for name in ('index.html', 'terms.html', 'privacy.html', 'id/index.html', 'id/syarat-ketentuan.html', 'id/kebijakan-privasi.html', 'assets/style.css'):
        assert name in manifest['files'], f'Missing required file: {name}'
    return manifest


def switch(site, destination):
    temporary = site / '.current-next'
    temporary.unlink(missing_ok=True)
    temporary.symlink_to(destination)
    os.replace(temporary, site / 'current')


def health(revision, manifest):
    for name in ('release.json', 'index.html', 'id/index.html', 'terms.html', 'privacy.html', 'id/syarat-ketentuan.html', 'id/kebijakan-privasi.html', 'assets/style.css'):
        with urllib.request.urlopen('http://127.0.0.1:18160/' + name, timeout=10) as response:
            body = response.read()
        if name == 'release.json':
            assert json.loads(body)['revision'] == revision, 'Origin serves a different release'
        else:
            assert hashlib.sha256(body).hexdigest() == manifest['files'][name], f'Origin mismatch: {name}'


def activate(site, destination, revision, manifest):
    previous = os.readlink(site / 'current')
    switch(site, destination)
    try:
        health(revision, manifest)
    except Exception:
        switch(site, previous)
        raise
    return previous


def deploy(revision, digest):
    assert re.fullmatch('[0-9a-f]{40}', revision), 'Invalid revision'
    assert re.fullmatch('[0-9a-f]{64}', digest), 'Invalid digest'
    import boto3
    config = json.loads((ROOT / 'deploy/config.json').read_text())
    assert Path('/sys/devices/virtual/dmi/id/board_asset_tag').read_text().strip() == config['instance'], 'Wrong deployment host'
    site = ROOT / 'html'
    releases = site / 'releases'
    releases.mkdir(exist_ok=True)
    with (ROOT / '.deploy.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        with tempfile.TemporaryDirectory(prefix='.incoming-', dir=releases) as work:
            work = Path(work)
            archive, extracted = work / 'artifact.tar.gz', work / 'site'
            extracted.mkdir(mode=0o755)
            s3 = boto3.client('s3', region_name=config['region'])
            key = f'releases/{revision}/{digest}.tar.gz'
            obj = s3.get_object(Bucket=config['bucket'], Key=key)
            assert obj['ContentLength'] <= LIMIT, 'Compressed artifact exceeds limit'
            with obj['Body'] as source, archive.open('wb') as output:
                shutil.copyfileobj(source, output)
            assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest, 'Archive checksum mismatch'
            manifest = extract(archive, extracted, revision)
            release = releases / f'{revision}-{digest[:16]}'
            if release.exists():
                # Never trust an existing directory merely because its name matches.
                assert json.loads((release / 'release.json').read_text()) == manifest
                for name, filehash in manifest['files'].items():
                    assert hashlib.sha256((release / name).read_bytes()).hexdigest() == filehash
            else:
                os.rename(extracted, release)
            previous = activate(site, 'releases/' + release.name, revision, manifest)
            receipt = {'revision': revision, 'digest': digest, 'previous': previous, 'current': 'releases/' + release.name}
            (ROOT / 'deployment.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps(receipt))


if __name__ == '__main__':
    deploy(sys.argv[1], sys.argv[2])
