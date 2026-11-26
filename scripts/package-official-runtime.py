"""Build a localized package without substituting any official runtime DLL.

The upstream ZIP is checksum pinned. Every original file except chiaki.exe must
remain byte-identical. Only our executable, translations and notices are added.
PE imports of our new executable are checked against the official runtime.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import pefile

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
ARCHIVE = ROOT / 'official-runtime.zip'
EXPECTED = '6ca3f5e6780608104d79345ab7755cfa77fefc33a41ae10651a874c43f54ea57'
OUT = ROOT / 'dist-aligned'
PREFIX = Path(os.environ['MINGW_PREFIX'])
if not PREFIX.is_dir():
    PREFIX = Path(subprocess.check_output(['cygpath', '-w', os.environ['MINGW_PREFIX']], text=True).strip())


def digest(data):
    return hashlib.sha256(data).hexdigest()


if digest(ARCHIVE.read_bytes()) != EXPECTED:
    raise SystemExit('Official archive checksum mismatch')
if OUT.exists():
    raise SystemExit('Refusing to overwrite an existing package directory')
official = {}
with zipfile.ZipFile(ARCHIVE) as z:
    for entry in z.infolist():
        parts = Path(entry.filename).parts
        if not parts or parts[0] != 'chiaki-ng-Win' or '..' in parts or ':' in entry.filename:
            raise SystemExit('Unexpected upstream archive path')
        if not entry.is_dir():
            official[entry.filename] = digest(z.read(entry))
    z.extractall(OUT)
dest = OUT / 'chiaki-ng-Win'
shutil.copy2(ROOT / 'build-aligned/gui/chiaki.exe', dest / 'chiaki.exe')

# Check imported symbols against the original DLL exports. Windows system DLLs
# are resolved by the runner; imported non-system DLLs must be in the ZIP.
system32 = Path(os.environ['WINDIR']) / 'System32'
imports = pefile.PE(str(dest / 'chiaki.exe'))
checked = []
for desc in imports.DIRECTORY_ENTRY_IMPORT:
    name = desc.dll.decode('ascii')
    dll = dest / name
    if not dll.exists():
        if name.lower().startswith(('api-ms-win-', 'ext-ms-win-')) or (system32 / name).exists():
            continue
        raise SystemExit('Missing runtime dependency: ' + name)
    lib = pefile.PE(str(dll))
    symbols = lib.DIRECTORY_ENTRY_EXPORT.symbols
    names = {s.name for s in symbols}
    ordinals = {s.ordinal for s in symbols}
    for symbol in desc.imports:
        if (symbol.name is not None and symbol.name not in names) or (symbol.name is None and symbol.ordinal not in ordinals):
            raise SystemExit('Imported symbol missing in official DLL: ' + name + ' ' + str(symbol.name or symbol.ordinal))
    checked.append(name)
    lib.close()
imports.close()

for rel, expected in official.items():
    if rel == 'chiaki-ng-Win/chiaki.exe':
        continue
    if digest((OUT / rel).read_bytes()) != expected:
        raise SystemExit('An official runtime file changed: ' + rel)

for name in ('COPYING', 'README.zh-CN.md'):
    shutil.copy2(ROOT / name, dest / name)
shutil.copytree(ROOT / 'LICENSES', dest / 'LICENSES', dirs_exist_ok=True)
(dest / 'translations').mkdir(exist_ok=True)
shutil.copy2(ROOT / 'build-aligned/qtbase_zh_CN.qm', dest / 'translations/qtbase_zh_CN.qm')
(dest / 'qt.conf').write_text('[Paths]\nTranslations=translations\n', encoding='utf-8')
sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
submodules = subprocess.check_output(['git', 'submodule', 'status'], text=True)
(dest / 'SOURCE-INFO.txt').write_text(
    'Unofficial Simplified Chinese build, modified 2026-11-26.\n'
    'Source: https://github.com/YouMiyo/chiaki-ng-zh-cn/tree/' + sha + '\n'
    'License: AGPL v3; preserve applicable OpenSSL exception and component notices.\n'
    'Build instructions and exact commands: .github/workflows/zh-windows.yml in that source revision.\n'
    'Clone that revision and initialize the desktop submodules listed in the workflow.\n'
    'Upstream runtime: https://github.com/chiaki-ng/chiaki-ng/releases/tag/v1.10.1\n'
    'Upstream archive SHA256: ' + EXPECTED + '\n'
    'FFmpeg SDK/build recipes: https://github.com/streetpea/FFmpeg-Builds/tree/867f543\n'
    'libplacebo SDK source: https://github.com/haasn/libplacebo/tree/275f7dea27924cdd34ab2e6c20e448b6bc4fab65\n'
    'Qt Chinese catalog source: https://github.com/qt/qttranslations/tree/v6.12.0\n'
    'Runtime DLLs and QML resources are copied byte-for-byte from upstream.\n'
    'sdk-packages.txt lists BUILD SDK packages, not proof of runtime package provenance.\n'
    'The SDK license copies supplement, but do not replace, applicable upstream runtime notices.\n'
    'Streaming stability still requires a comparison test; this package is not a confirmed freeze fix.\n\n'
    + submodules, encoding='utf-8')
shutil.copy2(ROOT / 'build-aligned/sdk-packages.txt', dest / 'sdk-packages.txt')
sdk_licenses = PREFIX / 'share/licenses'
if sdk_licenses.is_dir():
    shutil.copytree(sdk_licenses, dest / 'THIRD-PARTY-NOTICES/build-sdk', dirs_exist_ok=True)
for source, target in [('SDL3-3.4.18/LICENSE.txt', 'SDL3.txt'),
                       ('sdl2-compat-2.32.74/LICENSE.txt', 'sdl2-compat.txt'),
                       ('hidapi/LICENSE.txt', 'hidapi.txt'),
                       ('third-party/curl/COPYING', 'curl.txt')]:
    path = ROOT / source
    if path.is_file():
        (dest / 'THIRD-PARTY-NOTICES').mkdir(exist_ok=True)
        shutil.copy2(path, dest / 'THIRD-PARTY-NOTICES' / target)
for rel, expected in official.items():
    if rel != 'chiaki-ng-Win/chiaki.exe' and digest((OUT / rel).read_bytes()) != expected:
        raise SystemExit('Package additions overwrote an official file: ' + rel)
report = dict(source_commit=sha, official_archive_sha256=EXPECTED,
              unchanged_official_files=len(official)-1, verified_executable_import_dlls=checked,
              official_file_sha256=official,
              note='Only chiaki.exe is replaced. Added translations/notices are separate. Not a streaming acceptance test.')
(dest / 'RUNTIME-VERIFICATION.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Verified byte-identical official runtime files:', len(official)-1)
print('Verified executable DLL imports:', len(checked))
