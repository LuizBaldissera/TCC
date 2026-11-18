$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_15M.csv", ".\Parelelos\points_40M.csv")
foreach ($data in $datasets) {
    if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." }
    julia Sequenciais/monte_carlo_sphere.jl $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Julia Sphere" }
    julia Sequenciais/monte_carlo_rastrigin.jl $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Julia Rastrigin" }
}
Write-Host "Testes sequenciais julia concluidos." -ForegroundColor Green
