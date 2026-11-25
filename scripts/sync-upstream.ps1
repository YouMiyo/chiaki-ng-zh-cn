param([Parameter(Mandatory=$true)][ValidatePattern('^v[0-9]+\.[0-9]+\.[0-9]+$')][string]$Tag,
      [string]$LUpdate = 'lupdate')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    if ((& git status --porcelain)) { throw 'Working tree must be clean before syncing.' }
    & git fetch https://github.com/chiaki-ng/chiaki-ng.git "refs/tags/${Tag}:refs/tags/${Tag}"
    if ($LASTEXITCODE -ne 0) { throw 'Fetch failed; nothing merged.' }
    & git switch -c "sync/$Tag"
    if ($LASTEXITCODE -ne 0) { throw 'Branch creation failed; nothing merged.' }
    & git merge --no-edit $Tag
    if ($LASTEXITCODE -ne 0) { throw 'Resolve the merge conflicts, then run update-zh-translations.ps1. No automatic reset is performed.' }
    & "$PSScriptRoot/update-zh-translations.ps1" -LUpdate $LUpdate
    Write-Host 'Review translations, build and test. Commit the changes and open a PR to main. Nothing was pushed automatically.'
} finally { Pop-Location }
