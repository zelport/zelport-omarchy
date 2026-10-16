import importlib.util
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bundle', pathlib.Path(__file__).parents[1] / 'scripts' / 'bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)

class BundleTests(unittest.TestCase):
    def fixture(self, root):
        for name in ('LICENSE', 'config.example.json', 'manifest.json', 'Service.qml', 'Widget.qml', 'Panel.qml', 'Model.js', 'helper.py', 'README.md'):
            (root / name).write_text('{}' if name == 'manifest.json' else name)
        (root / 'assets').mkdir()
        (root / 'assets' / 'symbol.svg').write_text('<svg/>')
        (root / 'docs').mkdir()
        for name in ('distribution/PUBLISHING.md', 'CONFIGURATION.md', 'NATIVE_ACCEPTANCE.md', 'GATEWAY_SETUP.md', 'zelport.service.example'):
            (root / 'docs' / name).parent.mkdir(parents=True, exist_ok=True)
            (root / 'docs' / name).write_text('Documentation')

    def test_only_runtime_and_documentation_are_packed_deterministically(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); self.fixture(root)
            (root/'design').mkdir(); (root/'design'/'private.txt').write_text('not included')
            (root/'__pycache__').mkdir(); (root/'__pycache__'/'helper.pyc').write_bytes(b'not included')
            one=bundle.archive(root); two=bundle.archive(root)
            self.assertEqual(one,two)
            import io,tarfile
            with tarfile.open(fileobj=io.BytesIO(one),mode='r:gz') as tar:
                names=tar.getnames()
                self.assertIn('zelport.integration/helper.py',names)
                self.assertFalse(any('design' in n or '__pycache__' in n for n in names))
                self.assertTrue(all(m.uid==0 and m.mtime==0 for m in tar.getmembers()))

    def test_symlink_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); self.fixture(root)
            (root/'assets'/'bad.svg').symlink_to(root/'README.md')
            with self.assertRaises(ValueError): bundle.archive(root)

if __name__=='__main__': unittest.main()
