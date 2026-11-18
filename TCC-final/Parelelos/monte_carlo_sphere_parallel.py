import csv
import math
import os
import time
import sys
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
# ============================================================
DIMENSIONS = 10
NUM_SAMPLES = 5_000_000
MIN_VALUE = -5.12
MAX_VALUE = 5.12
POINTS_FILE = "points.csv"
RESULTS_FILE = "resultados.csv"

WARMUP_RUNS = 1
MEASURED_RUNS = 5


# ============================================================
# FUNCAO DE BENCHMARK: SPHERE
# f(x) = sum(x_i^2)
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
    with open(file_path, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            points.append([float(v) for v in row])
    return points


# ============================================================
# TAREFA: avalia um bloco de pontos e retorna o melhor local.
# Executada em uma thread separada (ThreadPoolExecutor).
# Nenhuma variavel compartilhada e atualizada aqui.
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
# PARTICIONAMENTO (AGGLOMERATION)
# Divide os pontos em NUM_WORKERS blocos aproximadamente iguais,
# reduzindo o overhead de criar uma tarefa por amostra.
# ============================================================
def split_into_blocks(points, num_workers):
    block_size = math.ceil(len(points) / num_workers)
    return [points[i:i + block_size] for i in range(0, len(points), block_size)]


# ============================================================
# EXECUCAO PARALELA (uma medicao)
# Mede apenas: distribuicao dos blocos + calculo + combinacao (reducao).
# A combinacao (min entre os melhores locais) ocorre so depois de
# todas as threads terminarem, sem lock durante o processamento.
# ============================================================
def run_parallel(executor, blocks):
    start_time = time.perf_counter()

    local_results = list(executor.map(evaluate_block, blocks))

    best_value = math.inf
    best_solution = None
    for value, solution in local_results:
        if value < best_value:
            best_value = value
            best_solution = solution

    end_time = time.perf_counter()
    elapsed_ms = (end_time - start_time) * 1000
    return best_value, best_solution, elapsed_ms


def format_solution(solution, max_elements=10):
    if len(solution) <= max_elements:
        return "[" + ", ".join(f"{v:.4f}" for v in solution) + "]"
    else:
        limited = ", ".join(f"{v:.4f}" for v in solution[:max_elements])
        return "[" + limited + ", ...]"


# ============================================================
# SALVAR RESULTADOS EM CSV (NAO cronometrado)
# Uma linha por execucao medida; o arquivo e compartilhado por
# todos os programas (modo append) para facilitar os graficos.
# ============================================================
def save_results(function_name, mode, workers, samples, times, best_values):
    write_header = not os.path.exists(RESULTS_FILE) or os.path.getsize(RESULTS_FILE) == 0

    with open(RESULTS_FILE, "a", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        if write_header:
            writer.writerow(["linguagem", "funcao", "execucao", "workers",
                             "dimensoes", "amostras", "run", "tempo_ms", "melhor_valor"])
        for i in range(len(times)):
            writer.writerow(["Python", function_name, mode, workers, DIMENSIONS,
                             samples, i + 1, f"{times[i]:.3f}", f"{best_values[i]:.6f}"])


# ============================================================
# EXECUCAO
# ============================================================
def main():
    if len(sys.argv) < 3:
        print("Uso: python monte_carlo_sphere_parallel.py <dataset> <num_threads>")
        sys.exit(1)

    points_file = sys.argv[1]
    num_workers = int(sys.argv[2])

    points = load_points(points_file)

    # Carregamento dos dados e particionamento (NAO cronometrados)
    blocks = split_into_blocks(points, num_workers)

    # Configuracao inicial (NAO cronometrada)
    executor = ThreadPoolExecutor(max_workers=num_workers)

    # Execucao de aquecimento - NAO contabilizada nas metricas
    for _ in range(WARMUP_RUNS):
        run_parallel(executor, blocks)

    # Execucoes medidas
    times = []
    best_values = []
    best_value_final = math.inf
    best_solution_final = None

    for i in range(MEASURED_RUNS):
        best_value, best_solution, elapsed_ms = run_parallel(executor, blocks)
        times.append(elapsed_ms)
        best_values.append(best_value)
        print(f"run {i + 1}: {elapsed_ms:.3f} ms")

        if best_value < best_value_final:
            best_value_final = best_value
            best_solution_final = best_solution

    executor.shutdown()

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
    print("========================================")

    # Salvar resultados (NAO cronometrado)
    save_results("Sphere", "Paralela", num_workers, len(points), times, best_values)
    print(f"Resultados salvos em: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
