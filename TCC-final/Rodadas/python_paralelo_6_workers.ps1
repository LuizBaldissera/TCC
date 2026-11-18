$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_15M.csv", ".\Parelelos\points_40M.csv")
foreach ($data in $datasets) { if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." } }
foreach ($data in $datasets) {
    python Parelelos/monte_carlo_sphere_parallel.py $data 6; if ($LASTEXITCODE -ne 0) { throw "Falha no Python Sphere (6 workers)" }
    python Parelelos/monte_carlo_rastrigin_parallel.py $data 6; if ($LASTEXITCODE -ne 0) { throw "Falha no Python Rastrigin (6 workers)" }
}
Write-Host "Testes paralelos Python (6 workers) concluidos." -ForegroundColor Green
