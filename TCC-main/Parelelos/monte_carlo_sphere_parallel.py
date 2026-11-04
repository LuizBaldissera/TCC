import csv
import math
import time
import sys
import multiprocessing
from pathlib import Path

# ============================================================
# CONFIGURACAO DO EXPERIMENTO
# ============================================================
DIMENSIONS = 10
WARMUP_RUNS = 1
MEASURED_RUNS = 5
PROJECT_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_DIR / "Resultados"
RESULTS_FILE = RESULTS_DIR / "python_sphere_paralelo_workers.csv"
RESULTS_HEADER = [
    "linguagem", "funcao", "modo", "workers", "dimensoes",
    "amostras", "execucao", "tempo_ms", "melhor_valor"
]


# ============================================================
# FUNCAO DE BENCHMARK
# ============================================================
def sphere(x):
    total = 0.0
    for xi in x:
        total += xi * xi
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
# TAREFA: avalia um bloco e retorna o melhor resultado local.
# ============================================================
def evaluate_block(block):
    best_value = math.inf
    best_solution = None
    for solution in block:
        value = sphere(solution)
        if value < best_value:
            best_value = value
            best_solution = solution
    return best_value, best_solution


# ============================================================
# PARTICIONAMENTO (NAO cronometrado)
# ============================================================
def split_into_blocks(points, num_workers):
    block_size = math.ceil(len(points) / num_workers)
    return [points[i:i + block_size] for i in range(0, len(points), block_size)]


# ============================================================
# EXECUCAO PARALELA (uma medicao)
# Mede o envio/execucao das tarefas e a reducao dos resultados.
# Leitura do CSV, particionamento e escrita dos resultados ficam fora.
# ============================================================
def run_parallel(pool, blocks):
    start_time = time.perf_counter()
    local_results = pool.map(evaluate_block, blocks)

    best_value = math.inf
    best_solution = None
    for value, solution in local_results:
        if value < best_value:
            best_value = value
            best_solution = solution

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    return best_value, best_solution, elapsed_ms


# ============================================================
# GRAVACAO DOS RESULTADOS (NAO cronometrada)
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
    if len(sys.argv) < 3:
        print("Uso: python monte_carlo_sphere_parallel.py <points.csv> <num_processos>")
        sys.exit(1)

    global RESULTS_FILE
    points_file = Path(sys.argv[1]).resolve()
    num_workers = int(sys.argv[2])
    RESULTS_FILE = RESULTS_DIR / f"python_sphere_paralelo_{num_workers}_workers.csv"
    if num_workers < 1:
        raise ValueError("O numero de processos deve ser maior que zero.")

    # Leitura e particionamento antes da medicao.
    points = load_points(points_file)
    blocks = split_into_blocks(points, num_workers)

    times = []
    result_rows = []
    best_value_final = math.inf
    best_solution_final = None

    # Criacao do pool e aquecimento fora das medicoes.
    with multiprocessing.Pool(processes=num_workers) as pool:
        for _ in range(WARMUP_RUNS):
            run_parallel(pool, blocks)

        for run_number in range(1, MEASURED_RUNS + 1):
            best_value, best_solution, elapsed_ms = run_parallel(pool, blocks)
            times.append(elapsed_ms)
            result_rows.append([
                "Python", "Sphere", "Paralela", num_workers, DIMENSIONS,
                len(points), run_number, f"{elapsed_ms:.6f}", f"{best_value:.10f}"
            ])
            print(f"run {run_number}: {elapsed_ms:.3f} ms")

            if best_value < best_value_final:
                best_value_final = best_value
                best_solution_final = best_solution

    # Escrita somente depois de terminar todas as medicoes.
    save_results(result_rows)

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print("========================================")
    print("Funcao: Sphere")
    print("Linguagem: Python")
    print("Execucao: Paralela")
    print(f"Workers: {num_workers}")
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
