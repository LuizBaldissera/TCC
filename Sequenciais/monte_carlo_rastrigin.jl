using Random
using Printf

# ============================================================
# PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
# ============================================================
const DIMENSIONS = 10
const ITERATIONS = 1_000_000
const MIN_VALUE = -5.12
const MAX_VALUE = 5.12
const SEED = 42


# ============================================================
# FUNCAO DE BENCHMARK: RASTRIGIN
# f(x) = 10n + sum(x_i^2 - 10*cos(2*pi*x_i))
# ============================================================
function rastrigin(x)
    n = length(x)
    total = 10 * n
    for xi in x
        total += xi^2 - 10 * cos(2 * pi * xi)
    end
    return total
end


# ============================================================
# GERACAO DE UMA SOLUCAO ALEATORIA
# Estrutura isolada em funcao propria para facilitar, no futuro,
# a substituicao por leitura de pontos pre-gerados em arquivo.
# ============================================================
function generate_random_solution(rng, dimensions, min_value, max_value)
    return [min_value + rand(rng) * (max_value - min_value) for _ in 1:dimensions]
end


# ============================================================
# ALGORITMO MONTE CARLO (BUSCA ALEATORIA)
# Cada amostra e avaliada de forma independente, o que facilita
# a futura substituicao do loop sequencial por paralelizacao.
# ============================================================
function monte_carlo(rng, dimensions, iterations, min_value, max_value, objective_function)
    best_solution = nothing
    best_value = Inf

    for i in 1:iterations
        solution = generate_random_solution(rng, dimensions, min_value, max_value)
        value = objective_function(solution)

        if value < best_value
            best_value = value
            best_solution = solution
        end
    end

    return best_solution, best_value
end


# ============================================================
# FORMATACAO DA SOLUCAO PARA IMPRESSAO
# ============================================================
function format_solution(solution, max_elements=10)
    n = length(solution)
    if n <= max_elements
        return "[" * join([@sprintf("%.4f", v) for v in solution], ", ") * "]"
    else
        limited = join([@sprintf("%.4f", v) for v in solution[1:max_elements]], ", ")
        return "[" * limited * ", ...]"
    end
end


# ============================================================
# EXECUCAO
# ============================================================
function main()
    rng = MersenneTwister(SEED)

    start_time = time_ns()
    best_solution, best_value = monte_carlo(rng, DIMENSIONS, ITERATIONS, MIN_VALUE, MAX_VALUE, rastrigin)
    end_time = time_ns()

    elapsed_ms = (end_time - start_time) / 1_000_000.0

    # ============================================================
    # IMPRESSAO DOS RESULTADOS
    # ============================================================
    println("Funcao: Rastrigin")
    println("Dimensoes: ", DIMENSIONS)
    println("Iteracoes: ", ITERATIONS)
    @printf("Melhor valor: %.6f\n", best_value)
    @printf("Tempo de execucao: %.3f ms\n", elapsed_ms)
    println("Melhor solucao: ", format_solution(best_solution))
end

main()
