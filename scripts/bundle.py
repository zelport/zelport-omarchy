#!/usr/bin/env python3
"""Create a deterministic source bundle; never install or execute the plugin."""
import gzip
import hashlib
import io
from pathlib import Path
import tarfile

REQUIRED = ('docs/distribution/PUBLISHING.md', 'LICENSE', 'config.example.json', 'docs/CONFIGURATION.md', 'manifest.json', 'Service.qml', 'Widget.qml', 'Panel.qml', 'Model.js', 'helper.py', 'README.md', 'docs/NATIVE_ACCEPTANCE.md', 'docs/GATEWAY_SETUP.md', 'docs/zelport.service.example')


def archive(root):
    paths = [root / name for name in REQUIRED]
    paths += sorted((root / 'assets').glob('*.svg'))
    paths += sorted((root / 'tests').glob('*.py'))
    paths += sorted((root / 'tests').glob('*.cjs'))
    if (root / 'scripts' / 'bundle.py').is_file():
        paths.append(root / 'scripts' / 'bundle.py')
    if not any(p.suffix == '.svg' for p in paths):
        raise ValueError('Missing symbol assets')
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode='w', format=tarfile.USTAR_FORMAT) as tar:
        for path in paths:
            if path.is_symlink() or not path.is_file():
                raise ValueError('Missing or unsafe bundle file: ' + path.name)
            relative = path.relative_to(root)
            if any((root / parent).is_symlink() for parent in relative.parents):
                raise ValueError('Unsafe bundle directory')
            content = path.read_bytes()
            info = tarfile.TarInfo('zelport.integration/' + relative.as_posix())
            info.size = len(content)
            info.mode = 0o644
            info.mtime = 0
            info.uid = info.gid = 0
            tar.addfile(info, io.BytesIO(content))
    return gzip.compress(data.getvalue(), mtime=0)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    output = root / 'bin' / 'zelport-omarchy.tar.gz'
    content = archive(root)
    output.parent.mkdir(exist_ok=True)
    output.write_bytes(content)
    output.with_suffix(output.suffix + '.sha256').write_text(hashlib.sha256(content).hexdigest() + '  ' + output.name + '\n')
    print(output)
