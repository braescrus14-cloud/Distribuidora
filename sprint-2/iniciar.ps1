param([int]$Puerto = 8080)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$runtimes = @()
if (Get-Command python -ErrorAction SilentlyContinue) {
    $runtimes += (Get-Command python).Source
}
if (Get-Command Get-AppxPackage -ErrorAction SilentlyContinue) {
    foreach ($package in Get-AppxPackage 'OpenAI.CodexPrimaryRuntime*') {
        $runtimes += (Join-Path $package.InstallLocation 'dependencies/python/python.exe')
    }
}
$runtimes += 'C:\Program Files\WindowsApps\OpenAI.CodexPrimaryRuntime.v26-1030-493-0_26.1030.493.0_x64__3k8sg7r9htsxt\dependencies\python\python.exe'
$selected = $null
foreach ($runtime in $runtimes) {
    if ($runtime -like '*Microsoft\WindowsApps\python.exe') { continue }
    try {
        & $runtime -c 'import sys, openpyxl; sys.exit(sys.version_info < (3, 10))' 2>$null
        if ($LASTEXITCODE -eq 0) { $selected = $runtime; break }
    } catch {
        continue
    }
}
if (!$selected) {
    throw 'Instala Python 3.10 o posterior y ejecuta python -m pip install -r requirements.txt.'
}
& $selected 'app.py' --setup-if-needed --port $Puerto
exit $LASTEXITCODE
