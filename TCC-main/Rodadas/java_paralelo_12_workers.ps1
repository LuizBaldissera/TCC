$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_25M.csv")
foreach ($data in $datasets) { if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." } }
javac -d Parelelos Parelelos/MonteCarloSphereParallel.java Parelelos/MonteCarloRastriginParallel.java
if ($LASTEXITCODE -ne 0) { throw "Falha ao compilar Java paralelo" }
foreach ($data in $datasets) {
    java -cp Parelelos MonteCarloSphereParallel $data 12; if ($LASTEXITCODE -ne 0) { throw "Falha no Java Sphere (12 threads)" }
    java -cp Parelelos MonteCarloRastriginParallel $data 12; if ($LASTEXITCODE -ne 0) { throw "Falha no Java Rastrigin (12 threads)" }
}
Write-Host "Testes paralelos Java (12 workers) concluidos." -ForegroundColor Green
