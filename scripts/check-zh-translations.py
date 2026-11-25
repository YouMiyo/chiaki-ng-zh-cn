#!/usr/bin/env python3
"""Check active Qt translations, placeholders, rich text and mnemonic escapes."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

catalog = Path(__file__).resolve().parents[1] / 'gui/translations/chiaki_zh_CN.ts'
root = ET.parse(catalog).getroot()
errors = []
total = 0
for context in root.findall('context'):
    for message in context.findall('message'):
        translation = message.find('translation')
        if translation is not None and translation.get('type') in ('obsolete', 'vanished'):
            continue
        source = message.findtext('source') or ''
        if not source:
            continue
        total += 1
        label = f"{context.findtext('name')}: {source[:80]}"
        if translation is None or translation.get('type') == 'unfinished':
            errors.append(f'Unfinished: {label}')
            continue
        forms = translation.findall('numerusform') or [translation]
        for form in forms:
            text = ''.join(form.itertext())
            if not text:
                errors.append(f'Empty: {label}')
            if Counter(re.findall(r'%(?:L?\d+|n)', source)) != Counter(re.findall(r'%(?:L?\d+|n)', text)):
                errors.append(f'Placeholder mismatch: {label}')
            if Counter(re.findall(r'</?[A-Za-z][^>]*>', source)) != Counter(re.findall(r'</?[A-Za-z][^>]*>', text)):
                errors.append(f'Rich text mismatch: {label}')
            if source.count('\n') != text.count('\n'):
                errors.append(f'Newline mismatch: {label}')
print(f'Checked {total} nonempty active translations; {len(errors)} issue(s).')
for error in errors:
    print(error)
sys.exit(bool(errors))
