import csv
import math
import time
import sys
import multiprocessing

# ============================================================
# PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
# ============================================================
DIMENSIONS = 10
NUM_SAMPLES = 5_000_000
MIN_VALUE = -5.12
MAX_VALUE = 5.12
POINTS_FILE = "points.csv"

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
# Executada em um processo separado (multiprocessing.Pool).
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
# todos os processos terminarem, sem lock durante o processamento.
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


def format_solution(solution, max_elements=10):
    if len(solution) <= max_elements:
        return "[" + ", ".join(f"{v:.4f}" for v in solution) + "]"
    else:
        limited = ", ".join(f"{v:.4f}" for v in solution[:max_elements])
        return "[" + limited + ", ...]"


# ============================================================
# EXECUCAO
# ============================================================
def main():
    if len(sys.argv) < 2:
        print("Uso: python monte_carlo_sphere_parallel.py <num_processos>")
        sys.exit(1)

    num_workers = int(sys.argv[1])

    # Carregamento dos dados e particionamento (NAO cronometrados)
    points = load_points(POINTS_FILE)
    blocks = split_into_blocks(points, num_workers)

    # Configuracao inicial (NAO cronometrada)
    pool = multiprocessing.Pool(processes=num_workers)

    # Execucao de aquecimento - NAO contabilizada nas metricas
    for _ in range(WARMUP_RUNS):
        run_parallel(pool, blocks)

    # Execucoes medidas
    times = []
    best_value_final = math.inf
    best_solution_final = None

    for i in range(MEASURED_RUNS):
        best_value, best_solution, elapsed_ms = run_parallel(pool, blocks)
        times.append(elapsed_ms)
        print(f"run {i + 1}: {elapsed_ms:.3f} ms")

        if best_value < best_value_final:
            best_value_final = best_value
            best_solution_final = best_solution

    pool.close()
    pool.join()

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


if __name__ == "__main__":
    main()
