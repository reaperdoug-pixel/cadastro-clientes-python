<#
.SYNOPSIS
Executa a suite de validacao do DegeHub ERP sem usar o banco operacional.

.DESCRIPTION
Prioriza o interpretador da .venv do projeto. Se ela nao existir, usa o launcher
py ou o comando python. Os testes criam seus proprios bancos SQLite temporarios.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$raizProjeto = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $raizProjeto

$pythonVenv = Join-Path $raizProjeto '.venv\Scripts\python.exe'
$argumentos = @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
$python = $null

if (Test-Path -LiteralPath $pythonVenv -PathType Leaf) {
    $python = $pythonVenv
} else {
    $launcher = Get-Command -Name 'py' -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1

    if ($launcher) {
        $python = $launcher.Source
        $argumentos = @('-3') + $argumentos
    } else {
        $python = Get-Command -Name 'python' -CommandType Application -ErrorAction SilentlyContinue |
            Where-Object { $_.Source -notmatch '\\WindowsApps\\python\.exe$' } |
            Select-Object -ExpandProperty Source -First 1
    }
}

if (-not $python) {
    [Console]::Error.WriteLine('Python 3.10+ nao foi encontrado. Instale o Python e reabra o PowerShell. Depois, na raiz do projeto, execute: py -3 -m venv .venv e .\scripts\verificar.ps1. Se o launcher py nao estiver disponivel, use python -m venv .venv.')
    exit 1
}

& $python --version
if ($LASTEXITCODE -ne 0) {
    if ($python -eq $pythonVenv) {
        [Console]::Error.WriteLine('A .venv do projeto nao consegue iniciar. Recrie-a com py -3 -m venv --clear .venv (ou python -m venv --clear .venv) e execute .\scripts\verificar.ps1 novamente.')
    } else {
        [Console]::Error.WriteLine('O Python nao conseguiu iniciar. Instale Python 3.10+ e reabra o PowerShell; depois crie a .venv com py -3 -m venv .venv (ou python -m venv .venv).')
    }
    exit 1
}

& $python @argumentos
exit $LASTEXITCODE
