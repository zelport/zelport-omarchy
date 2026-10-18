import importlib.util
import json
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
        for name in ('distribution/PUBLISHING.md', 'CONFIGURATION.md', 'NATIVE_ACCEPTANCE.md', 'ZELPORT_SETUP.md', 'zelport.service.example'):
            (root / 'docs' / name).parent.mkdir(parents=True, exist_ok=True)
            (root / 'docs' / name).write_text('Documentation')

    def test_release_metadata_and_current_document_names(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        manifest = json.loads((root / 'manifest.json').read_text())
        self.assertEqual(manifest['version'], '0.10.0')
        self.assertIn('docs/ZELPORT_SETUP.md', bundle.REQUIRED)
        old_setup = 'docs/' + ''.join(('GATE', 'WAY')) + '_SETUP.md'
        self.assertNotIn(old_setup, bundle.REQUIRED)

    def test_systemd_example_uses_product_name(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        unit = (root / 'docs' / 'zelport.service.example').read_text()
        descriptions = [line for line in unit.splitlines() if line.startswith('Description=')]
        self.assertEqual(descriptions, ['Description=Zelport App'])

    def test_active_product_text_has_no_retired_variants(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        retired = (''.join(('gate', 'way')), ''.join(('pre', 'view')))
        paths = [root / 'README.md', root / 'helper.py', root / 'Model.js',
                 root / 'Panel.qml', root / 'Service.qml', root / 'Widget.qml',
                 root / 'docs' / 'CONFIGURATION.md', root / 'docs' / 'NATIVE_ACCEPTANCE.md',
                 root / 'docs' / 'ZELPORT_SETUP.md', root / 'docs' / 'distribution' / 'PUBLISHING.md',
                 root / 'docs' / 'zelport.service.example']
        for path in paths:
            text = path.read_text().lower()
            for token in retired:
                with self.subTest(path=path.relative_to(root), token=token):
                    self.assertNotIn(token, text)
        missing_variant = ''.join(('un', 'supported'))
        for path in (root / 'README.md', root / 'docs' / 'ZELPORT_SETUP.md'):
            self.assertNotIn(missing_variant, path.read_text().lower())
        state_branch = "row.state !== '" + missing_variant + "'"
        self.assertNotIn(state_branch, (root / 'Model.js').read_text())
        self.assertNotIn("model.state!=='" + missing_variant + "'", (root / 'Panel.qml').read_text())

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
