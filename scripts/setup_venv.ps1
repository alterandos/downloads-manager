Param(
    [string]$Python = "py",
    [string]$VenvPath = ".venv",
    [string]$ReqIn = "requirements.in",
    [string]$ReqTxt = "requirements.txt"
)

Write-Host "[setup] Creating virtual environment at $VenvPath"
& $Python -m venv $VenvPath

$Pip = Join-Path $VenvPath "Scripts\pip.exe"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

Write-Host "[setup] Upgrading pip"
& $Pip install --upgrade pip

Write-Host "[setup] Installing pip-tools"
& $Pip install pip-tools

if (Test-Path $ReqIn) {
    Write-Host "[setup] Compiling locked requirements from $ReqIn"
    & $PythonExe -m piptools compile $ReqIn --output-file $ReqTxt --quiet
}

Write-Host "[setup] Installing dependencies from $ReqTxt"
& $Pip install -r $ReqTxt

Write-Host "[setup] Done. Activate with: `"$VenvPath\Scripts\Activate.ps1`""
