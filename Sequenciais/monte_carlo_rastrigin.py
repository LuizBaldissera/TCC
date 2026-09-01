import random
import math
import time

# ============================================================
# PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
# ============================================================
DIMENSIONS = 10
ITERATIONS = 1000000
MIN_VALUE = -5.12
MAX_VALUE = 5.12
SEED = 42


# ============================================================
# FUNCAO DE BENCHMARK: RASTRIGIN
# f(x) = 10n + sum(x_i^2 - 10*cos(2*pi*x_i))
# ============================================================
def rastrigin(x):
    n = len(x)
    total = 10 * n
    for xi in x:
        total += xi * xi - 10 * math.cos(2 * math.pi * xi)
    return total


# ============================================================
# GERACAO DE UMA SOLUCAO ALEATORIA
# Estrutura isolada em funcao propria para facilitar, no futuro,
# a substituicao por leitura de pontos pre-gerados em arquivo.
# ============================================================
def generate_random_solution(dimensions, min_value, max_value):
    return [random.uniform(min_value, max_value) for _ in range(dimensions)]


# ============================================================
# ALGORITMO MONTE CARLO (BUSCA ALEATORIA)
# Cada amostra e avaliada de forma independente, o que facilita
# a futura substituicao do loop sequencial por paralelizacao.
# ============================================================
def monte_carlo(dimensions, iterations, min_value, max_value, objective_function):
    best_solution = None
    best_value = math.inf

    for _ in range(iterations):
        solution = generate_random_solution(dimensions, min_value, max_value)
        value = objective_function(solution)

        if value < best_value:
            best_value = value
            best_solution = solution

    return best_solution, best_value


# ============================================================
# FORMATACAO DA SOLUCAO PARA IMPRESSAO
# ============================================================
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
    random.seed(SEED)

    start_time = time.perf_counter()
    best_solution, best_value = monte_carlo(
        DIMENSIONS, ITERATIONS, MIN_VALUE, MAX_VALUE, rastrigin
    )
    end_time = time.perf_counter()

    elapsed_ms = (end_time - start_time) * 1000

    # ============================================================
    # IMPRESSAO DOS RESULTADOS
    # ============================================================
    print("Funcao: Rastrigin")
    print(f"Dimensoes: {DIMENSIONS}")
    print(f"Iteracoes: {ITERATIONS}")
    print(f"Melhor valor: {best_value:.6f}")
    print(f"Tempo de execucao: {elapsed_ms:.3f} ms")
    print(f"Melhor solucao: {format_solution(best_solution)}")


if __name__ == "__main__":
    main()
