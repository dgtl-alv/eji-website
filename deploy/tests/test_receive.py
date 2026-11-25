import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('receiver', Path(__file__).resolve().parents[1] / 'receive.py')
receiver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(receiver)
REVISION = 'a' * 40


class ArtifactTests(unittest.TestCase):
    def archive(self, root, entries):
        archive = root / 'site.tar.gz'
        with tarfile.open(archive, 'w:gz') as tar:
            for name, content in entries:
                item = tarfile.TarInfo(name)
                if content is None:
                    item.type, item.linkname = tarfile.SYMTYPE, '/etc/passwd'
                    tar.addfile(item)
                else:
                    item.size = len(content)
                    tar.addfile(item, io.BytesIO(content))
        return archive

    def valid_entries(self):
        names = ['index.html', 'privacy.html', 'terms.html', 'id/index.html', 'id/syarat-ketentuan.html', 'id/kebijakan-privasi.html', 'assets/style.css']
        files = {name: b'content' for name in names}
        manifest = {'revision': REVISION, 'files': {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}}
        return list(files.items()) + [('release.json', json.dumps(manifest).encode())]

    def check(self, entries, revision=REVISION):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            target = root / 'out'
            target.mkdir()
            return receiver.extract(self.archive(root, entries), target, revision)

    def test_valid_complete_artifact(self):
        self.assertEqual(self.check(self.valid_entries())['revision'], REVISION)

    def test_rejects_path_traversal_absolute_path_symlink_and_source(self):
        for name, content in [('../escape.html', b'x'), ('/escape.html', b'x'), ('assets/link.svg', None), ('build.py', b'x'), ('.git/config', b'x')]:
            with self.subTest(name=name), self.assertRaises(AssertionError):
                self.check([(name, content)])

    def test_rejects_duplicate_path(self):
        with self.assertRaises(AssertionError):
            self.check([('index.html', b'x'), ('index.html', b'x')])

    def test_rejects_wrong_commit(self):
        with self.assertRaises(AssertionError):
            self.check(self.valid_entries(), 'b' * 40)

    def test_rejects_file_checksum_mismatch(self):
        entries = self.valid_entries()
        entries[0] = ('index.html', b'tampered')
        with self.assertRaises(AssertionError):
            self.check(entries)

    def test_rejects_unlisted_file(self):
        with self.assertRaises(AssertionError):
            self.check(self.valid_entries() + [('assets/extra.js', b'x')])

    def test_rejects_oversized_archive(self):
        with patch.object(receiver, 'LIMIT', 2), self.assertRaises(AssertionError):
            self.check([('index.html', b'large')])

    def test_atomic_switch_and_restore(self):
        with tempfile.TemporaryDirectory() as work:
            site = Path(work)
            receiver.switch(site, 'releases/old')
            receiver.switch(site, 'releases/new')
            self.assertEqual((site / 'current').readlink(), Path('releases/new'))
            receiver.switch(site, 'releases/old')
            self.assertEqual((site / 'current').readlink(), Path('releases/old'))

    def test_health_failure_restores_previous_release(self):
        with tempfile.TemporaryDirectory() as work:
            site = Path(work)
            receiver.switch(site, 'releases/old')
            with patch.object(receiver, 'health', side_effect=RuntimeError('failed health check')):
                with self.assertRaises(RuntimeError):
                    receiver.activate(site, 'releases/new', REVISION, {})
            self.assertEqual((site / 'current').readlink(), Path('releases/old'))


if __name__ == '__main__':
    unittest.main()
