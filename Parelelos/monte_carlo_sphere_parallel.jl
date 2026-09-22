using Printf
using DelimitedFiles
using Base.Threads

# ============================================================
# PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
# ============================================================
const DIMENSIONS = 10
const NUM_SAMPLES = 5_000_000
const MIN_VALUE = -5.12
const MAX_VALUE = 5.12
const POINTS_FILE = "points.csv"

const WARMUP_RUNS = 1
const MEASURED_RUNS = 5


# ============================================================
# FUNCAO DE BENCHMARK: SPHERE
# f(x) = sum(x_i^2)
# ============================================================
function sphere(x)
    total = 0.0
    for xi in x
        total += xi^2
    end
    return total
end


# ============================================================
# LEITURA DOS PONTOS (NAO cronometrada)
# ============================================================
function load_points(file_path)
    data = readdlm(file_path, ',', Float64)
    n = size(data, 1)
    return [data[i, :] for i in 1:n]
end


# ============================================================
# PARTICIONAMENTO (AGGLOMERATION)
# Divide os pontos em blocos aproximadamente iguais, um por thread,
# reduzindo o overhead de criar uma tarefa por amostra.
# ============================================================
function split_into_blocks(points, num_workers)
    n = length(points)
    block_size = ceil(Int, n / num_workers)
    blocks = Vector{Vector{Vector{Float64}}}()
    for start in 1:block_size:n
        stop = min(start + block_size - 1, n)
        push!(blocks, points[start:stop])
    end
    return blocks
end


# ============================================================
# EXECUCAO PARALELA (uma medicao)
# Cada thread processa um bloco e mantem seu proprio melhor local
# (vetor local_best_values/local_best_solutions, uma posicao por
# bloco, sem concorrencia). A combinacao (reducao) ocorre depois
# do Threads.@threads, sobre um vetor pequeno de resultados.
# ============================================================
function run_parallel(blocks)
    num_blocks = length(blocks)
    local_best_values = fill(Inf, num_blocks)
    local_best_solutions = Vector{Any}(undef, num_blocks)

    start_time = time_ns()

    Threads.@threads for t in 1:num_blocks
        best_value = Inf
        best_solution = nothing
        for solution in blocks[t]
            value = sphere(solution)
            if value < best_value
                best_value = value
                best_solution = solution
            end
        end
        local_best_values[t] = best_value
        local_best_solutions[t] = best_solution
    end

    # Combinacao (reducao) dos melhores locais -> melhor global
    best_value = Inf
    best_solution = nothing
    for t in 1:num_blocks
        if local_best_values[t] < best_value
            best_value = local_best_values[t]
            best_solution = local_best_solutions[t]
        end
    end

    end_time = time_ns()
    elapsed_ms = (end_time - start_time) / 1_000_000.0

    return best_value, best_solution, elapsed_ms
end


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
# O numero de threads e definido externamente (julia -t N).
# ============================================================
function main()
    num_workers = Threads.nthreads()

    # Carregamento dos dados e particionamento (NAO cronometrados)
    points = load_points(POINTS_FILE)
    blocks = split_into_blocks(points, num_workers)

    # Execucao de aquecimento (compilacao JIT) - NAO contabilizada
    for _ in 1:WARMUP_RUNS
        run_parallel(blocks)
    end

    # Execucoes medidas
    times = zeros(MEASURED_RUNS)
    best_value_final = Inf
    best_solution_final = nothing

    for i in 1:MEASURED_RUNS
        best_value, best_solution, elapsed_ms = run_parallel(blocks)
        times[i] = elapsed_ms
        @printf("run %d: %.3f ms\n", i, elapsed_ms)

        if best_value < best_value_final
            best_value_final = best_value
            best_solution_final = best_solution
        end
    end

    avg_time = sum(times) / length(times)
    min_time = minimum(times)
    max_time = maximum(times)

    println("========================================")
    println("Funcao: Sphere")
    println("Linguagem: Julia")
    println("Execucao: Paralela")
    println("Threads: ", num_workers)
    println("Dimensoes: ", DIMENSIONS)
    println("Amostras: ", length(points))
    println("----------------------------------------")
    @printf("Melhor valor: %.6f\n", best_value_final)
    @printf("Tempo medio: %.2f ms\n", avg_time)
    @printf("Tempo minimo: %.2f ms\n", min_time)
    @printf("Tempo maximo: %.2f ms\n", max_time)
    println("Melhor solucao: ", format_solution(best_solution_final))
    println("========================================")
end

main()
