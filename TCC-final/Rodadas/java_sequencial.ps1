$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$datasets = @(".\Parelelos\points_5M.csv", ".\Parelelos\points_15M.csv", ".\Parelelos\points_40M.csv")
foreach ($data in $datasets) {
    if (-not (Test-Path $data)) { throw "Dataset nao encontrado: $data. Execute gerar_datasets.ps1 primeiro." }
}
javac -d Sequenciais Sequenciais/MonteCarloSphere.java Sequenciais/MonteCarloRastrigin.java
if ($LASTEXITCODE -ne 0) { throw "Falha ao compilar Java sequencial" }
foreach ($data in $datasets) {
    java -cp Sequenciais MonteCarloSphere $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Java Sphere" }
    java -cp Sequenciais MonteCarloRastrigin $data; if ($LASTEXITCODE -ne 0) { throw "Falha no Java Rastrigin" }
}
Write-Host "Testes sequenciais java concluidos." -ForegroundColor Green
