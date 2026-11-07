import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from backend import model, system


class RootfsTest(unittest.TestCase):
    def test_manifest_rejects_unpinned_or_insecure_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'manifest.json'
            for sha, urls in [('latest', ['https://host/rootfs']), ('a'*64, []),
                              ('a'*64, ['http://host/rootfs']), ('a'*64, ['https://user:secret@host/rootfs'])]:
                path.write_text(json.dumps({'sha256': sha, 'urls': urls}))
                with self.assertRaises(ValueError):
                    model.load_rootfs_manifest(path)

    def test_download_joins_parts_in_order_and_checks_whole_archive(self):
        pieces = {'https://host/first': b'first', 'https://host/second': b'second'}
        def download(argv, **kwargs):
            Path(argv[argv.index('--output') + 1]).write_bytes(pieces[argv[-1]])
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(system, 'ROOTFS_URLS', tuple(pieces)), \
             patch.object(system, 'ROOTFS_SHA256', hashlib.sha256(b'firstsecond').hexdigest()), \
             patch.object(system, 'run', side_effect=download):
            path = system.fetch_rootfs(directory)
            system.verify_rootfs(path)
            self.assertEqual(path.read_bytes(), b'firstsecond')
            path.write_bytes(b'tampered')
            with self.assertRaises(model.InstallError):
                system.verify_rootfs(path)
            self.assertFalse((Path(directory)/'pond-rootfs.download').exists())

    def test_failed_part_removes_partial_archive(self):
        with tempfile.TemporaryDirectory() as directory, \
             patch.object(system, 'run', side_effect=RuntimeError('download failed')):
            with self.assertRaises(RuntimeError):
                system.fetch_rootfs(directory)
            self.assertEqual(list(Path(directory).iterdir()), [])

if __name__ == '__main__':
    unittest.main()
