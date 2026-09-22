import csv
import random

# ============================================================
# Gera o arquivo de pontos compartilhado por Python, Java e Julia.
# Executar apenas UMA VEZ; o mesmo points.csv deve ser usado
# pelos 6 programas sequenciais e pelos 6 programas paralelos,
# para garantir comparacao justa entre as linguagens.
#
# A geracao dos dados NAO faz parte da medicao de desempenho.
# ============================================================

DIMENSIONS = 10
NUM_SAMPLES = 5_000_000
MIN_VALUE = -5.12
MAX_VALUE = 5.12
SEED = 42
OUTPUT_FILE = "points.csv"


def main():
    random.seed(SEED)

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        for _ in range(NUM_SAMPLES):
            row = [f"{random.uniform(MIN_VALUE, MAX_VALUE):.8f}" for _ in range(DIMENSIONS)]
            writer.writerow(row)

    print(f"Arquivo gerado: {OUTPUT_FILE}")
    print(f"Amostras: {NUM_SAMPLES}")
    print(f"Dimensoes: {DIMENSIONS}")
    print(f"Dominio: [{MIN_VALUE}, {MAX_VALUE}]")


if __name__ == "__main__":
    main()
