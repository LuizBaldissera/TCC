$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_25M.csv")
foreach ($data in $datasets) {
    if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." }
    python Sequenciais/monte_carlo_sphere.py $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Python Sphere" }
    python Sequenciais/monte_carlo_rastrigin.py $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Python Rastrigin" }
}
Write-Host "Testes sequenciais python concluidos." -ForegroundColor Green
