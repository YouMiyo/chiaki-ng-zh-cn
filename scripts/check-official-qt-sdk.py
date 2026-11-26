"""Fail before compiling when Qt SDK binaries differ from the official runtime."""
import hashlib
import os
from pathlib import Path
import subprocess
import zipfile

prefix = Path(subprocess.check_output(['cygpath', '-w', os.environ['MINGW_PREFIX']], text=True).strip())
count = 0
with zipfile.ZipFile('official-runtime.zip') as z:
    for name in z.namelist():
        parts = Path(name).parts
        if len(parts) != 2 or not parts[1].startswith('Qt6') or not parts[1].endswith('.dll'):
            continue
        sdk = prefix / 'bin' / parts[1]
        if not sdk.is_file() or hashlib.sha256(sdk.read_bytes()).digest() != hashlib.sha256(z.read(name)).digest():
            raise SystemExit('Qt SDK does not match official binary: ' + parts[1])
        count += 1
if count == 0:
    raise SystemExit('No Qt runtime files checked')
print('Qt SDK DLLs matching the official package byte-for-byte:', count)
