$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python .\Parelelos\generate_points.py 5000000 .\Parelelos\points_5M.csv
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar points_5M.csv" }
python .\Parelelos\generate_points.py 20000000 .\Parelelos\points_25M.csv
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar points_25M.csv" }
Write-Host "Datasets 5M e 25M gerados. Nao execute este script novamente entre os testes." -ForegroundColor Green
