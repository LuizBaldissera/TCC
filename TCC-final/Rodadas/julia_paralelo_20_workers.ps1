$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_15M.csv", ".\Parelelos\points_40M.csv")
foreach ($data in $datasets) { if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." } }
foreach ($data in $datasets) {
    julia -t 20 Parelelos/monte_carlo_sphere_parallel.jl $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Julia Sphere (20 threads)" }
    julia -t 20 Parelelos/monte_carlo_rastrigin_parallel.jl $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Julia Rastrigin (20 threads)" }
}
Write-Host "Testes paralelos Julia (20 workers) concluidos." -ForegroundColor Green
