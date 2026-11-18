import csv
import random
import sys
from pathlib import Path

# ============================================================
# Gera o arquivo de pontos compartilhado por Python, Java e Julia.
# Executar apenas UMA VEZ; o mesmo points.csv deve ser usado
# pelos 6 programas sequenciais e pelos 6 programas paralelos,
# para garantir comparacao justa entre as linguagens.
#
# A geracao dos dados NAO faz parte da medicao de desempenho.
# ============================================================

DIMENSIONS = 10
DEFAULT_NUM_SAMPLES = 5_000_000
MIN_VALUE = -5.12
MAX_VALUE = 5.12
SEED = 42


def main():
    num_samples = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_NUM_SAMPLES
    output_file = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path(__file__).resolve().parent / "points.csv"
    if num_samples <= 0:
        raise ValueError("A quantidade de amostras deve ser maior que zero.")

    random.seed(SEED)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        for _ in range(num_samples):
            row = [f"{random.uniform(MIN_VALUE, MAX_VALUE):.8f}" for _ in range(DIMENSIONS)]
            writer.writerow(row)

    print(f"Arquivo gerado: {output_file}")
    print(f"Amostras: {num_samples}")
    print(f"Dimensoes: {DIMENSIONS}")
    print(f"Dominio: [{MIN_VALUE}, {MAX_VALUE}]")


if __name__ == "__main__":
    main()
