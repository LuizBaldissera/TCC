import csv
import math
import time
import sys
from pathlib import Path

# ============================================================
# CONFIGURACAO DO EXPERIMENTO
# Os pontos sao gerados uma unica vez e compartilhados por todos
# os programas sequenciais e paralelos.
# ============================================================
DIMENSIONS = 10
WARMUP_RUNS = 1
MEASURED_RUNS = 5
PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_FILE = PROJECT_DIR / "Resultados" / "python_rastrigin_sequencial.csv"
RESULTS_HEADER = [
    "linguagem", "funcao", "modo", "workers", "dimensoes",
    "amostras", "execucao", "tempo_ms", "melhor_valor"
]


# ============================================================
# FUNCAO DE BENCHMARK
# ============================================================
def rastrigin(x):
    total = 10 * len(x)
    for xi in x:
        total += xi * xi - 10 * math.cos(2 * math.pi * xi)
    return total


# ============================================================
# LEITURA DOS PONTOS (NAO cronometrada)
# ============================================================
def load_points(file_path):
    points = []
    with open(file_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for line_number, row in enumerate(reader, start=1):
            if not row:
                continue
            if len(row) != DIMENSIONS:
                raise ValueError(
                    f"Linha {line_number} de {file_path} possui {len(row)} dimensoes; "
                    f"eram esperadas {DIMENSIONS}."
                )
            points.append([float(value) for value in row])

    if not points:
        raise ValueError(f"Nenhum ponto foi encontrado em {file_path}.")
    return points


# ============================================================
# EXECUCAO SEQUENCIAL (uma medicao)
# O cronometro envolve somente a avaliacao das amostras.
# ============================================================
def run_sequential(points):
    best_solution = None
    best_value = math.inf

    start_time = time.perf_counter()
    for solution in points:
        value = rastrigin(solution)
        if value < best_value:
            best_value = value
            best_solution = solution
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000
    return best_value, best_solution, elapsed_ms


# ============================================================
# GRAVACAO DOS RESULTADOS (NAO cronometrada)
# Cada linha representa uma execucao medida.
# ============================================================
def save_results(rows):
    RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_has_data = RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_has_data:
            writer.writerow(RESULTS_HEADER)
        writer.writerows(rows)


def format_solution(solution, max_elements=10):
    if len(solution) <= max_elements:
        return "[" + ", ".join(f"{value:.4f}" for value in solution) + "]"
    limited = ", ".join(f"{value:.4f}" for value in solution[:max_elements])
    return "[" + limited + ", ...]"


# ============================================================
# EXECUCAO
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python monte_carlo_rastrigin.py <points.csv>")
        sys.exit(1)
    points_file = Path(sys.argv[1]).resolve()

    # A leitura do CSV ocorre antes de qualquer medicao.
    points = load_points(points_file)

    # Aquecimento: nao entra no arquivo de resultados nem nas metricas.
    for _ in range(WARMUP_RUNS):
        run_sequential(points)

    times = []
    result_rows = []
    best_value_final = math.inf
    best_solution_final = None

    for run_number in range(1, MEASURED_RUNS + 1):
        best_value, best_solution, elapsed_ms = run_sequential(points)
        times.append(elapsed_ms)
        result_rows.append([
            "Python", "Rastrigin", "Sequencial", 1, DIMENSIONS,
            len(points), run_number, f"{elapsed_ms:.6f}", f"{best_value:.10f}"
        ])
        print(f"run {run_number}: {elapsed_ms:.3f} ms")

        if best_value < best_value_final:
            best_value_final = best_value
            best_solution_final = best_solution

    # A escrita no CSV acontece somente depois das medicoes.
    save_results(result_rows)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("========================================")
    print("Funcao: Rastrigin")
    print("Linguagem: Python")
    print("Execucao: Sequencial")
    print("Workers: 1")
    print(f"Dimensoes: {DIMENSIONS}")
    print(f"Amostras: {len(points)}")
    print("----------------------------------------")
    print(f"Melhor valor: {best_value_final:.6f}")
    print(f"Tempo medio: {avg_time:.2f} ms")
    print(f"Tempo minimo: {min_time:.2f} ms")
    print(f"Tempo maximo: {max_time:.2f} ms")
    print(f"Melhor solucao: {format_solution(best_solution_final)}")
    print(f"Resultados salvos em: {RESULTS_FILE}")
    print("========================================")


if __name__ == "__main__":
    main()
