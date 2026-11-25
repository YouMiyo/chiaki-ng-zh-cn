param([string]$LUpdate = 'lupdate')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
Push-Location $repoRoot
try {
    & $LUpdate gui/src gui/include -no-obsolete -locations relative -source-language en_US -target-language zh_CN -ts gui/translations/chiaki_zh_CN.ts
    if ($LASTEXITCODE -ne 0) { throw 'lupdate failed' }
    & python scripts/check-zh-translations.py
    if ($LASTEXITCODE -ne 0) { throw 'Translate or review the reported entries before releasing.' }
} finally { Pop-Location }
