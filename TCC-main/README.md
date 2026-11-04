# Experimentos Monte Carlo — Python, Julia e Java

Os programas originais foram mantidos. Cada um recebe o caminho do CSV, executa o algoritmo e mede o tempo dentro do próprio código. Os scripts PowerShell apenas passam os parâmetros.

## Datasets

Na raiz do projeto, execute uma única vez:

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\gerar_datasets.ps1
```

Serão gerados:
- `Parelelos/points_5M.csv`
- `Parelelos/points_50M.csv`

Os dois usam a mesma seed e são compartilhados por todas as linguagens e configurações. Não rode o gerador novamente entre os benchmarks.

## Execuções sequenciais

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\python_sequencial.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\julia_sequencial.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\java_sequencial.ps1
```

## Execuções paralelas — 6 workers

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\python_paralelo_6_workers.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\julia_paralelo_6_workers.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\java_paralelo_6_workers.ps1
```

## Execuções paralelas — 12 workers

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\python_paralelo_12_workers.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\julia_paralelo_12_workers.ps1
powershell.exe -ExecutionPolicy Bypass -File .\Rodadas\java_paralelo_12_workers.ps1
```

Execute um script por vez. Cada script executa Sphere e Rastrigin para 5M e 50M. Os programas fazem 1 aquecimento e 5 medições e salvam os resultados em arquivos separados na pasta `Resultados`.

## Atenção ao teste de 50 milhões

O arquivo de 50M pode ocupar vários GB em disco. Além disso, os programas atuais carregam todos os pontos na memória antes de iniciar a medição. Com 16 GB de RAM, principalmente os programas Python e Julia podem não conseguir carregar 50M de pontos. Se isso acontecer, será necessário adaptar a leitura/processamento para blocos, mantendo o cronômetro dentro dos próprios programas. Não execute vários benchmarks ao mesmo tempo.
