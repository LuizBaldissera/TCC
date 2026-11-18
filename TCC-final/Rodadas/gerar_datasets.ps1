$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python .\Parelelos\generate_points.py 5000000 .\Parelelos\points_5M.csv
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar points_5M.csv" }
python .\Parelelos\generate_points.py 15000000 .\Parelelos\points_15M.csv
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar points_15M.csv" }
python .\Parelelos\generate_points.py 40000000 .\Parelelos\points_40M.csv
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar points_40M.csv" }
Write-Host "Datasets 5M, 15M e 40M gerados. Nao execute este script novamente entre os testes." -ForegroundColor Green
