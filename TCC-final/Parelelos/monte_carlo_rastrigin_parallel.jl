using DelimitedFiles
using Printf
using Base.Threads

# ============================================================
# CONFIGURACAO DO EXPERIMENTO
# ============================================================
const DIMENSIONS = 10
const WARMUP_RUNS = 1
const MEASURED_RUNS = 5
const PROJECT_DIR = normpath(joinpath(@__DIR__, ".."))
const RESULTS_DIR = joinpath(PROJECT_DIR, "Resultados")
const RESULTS_FILE = joinpath(RESULTS_DIR, "julia_rastrigin_paralelo_$(Threads.nthreads())_workers.csv")
const RESULTS_HEADER = "linguagem,funcao,modo,workers,dimensoes,amostras,execucao,tempo_ms,melhor_valor"


# ============================================================
# FUNCAO DE BENCHMARK
# ============================================================
function rastrigin(x)
    total = 10 * length(x)
    for xi in x
        total += xi^2 - 10 * cos(2 * pi * xi)
    end
    return total
end


# ============================================================
# LEITURA DOS PONTOS (NAO cronometrada)
# ============================================================
function load_points(file_path)
    if !isfile(file_path)
        error("Arquivo de pontos nao encontrado: $file_path. Execute generate_points.py primeiro.")
    end
    data = readdlm(file_path, ',', Float64)
    if size(data, 2) != DIMENSIONS
        error("O arquivo $file_path possui $(size(data, 2)) dimensoes; eram esperadas $DIMENSIONS.")
    end
    if size(data, 1) == 0
        error("Nenhum ponto foi encontrado em $file_path.")
    end
    return [collect(data[i, :]) for i in axes(data, 1)]
end


# ============================================================
# PARTICIONAMENTO (NAO cronometrado)
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
# Mede o processamento paralelo e a reducao dos resultados.
# Leitura, particionamento e escrita ficam fora do cronometro.
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
            value = rastrigin(solution)
            if value < best_value
                best_value = value
                best_solution = solution
            end
        end
        local_best_values[t] = best_value
        local_best_solutions[t] = best_solution
    end

    # Reducao dos melhores resultados locais.
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


# ============================================================
# GRAVACAO DOS RESULTADOS (NAO cronometrada)
# ============================================================
function save_results(rows)
    mkpath(RESULTS_DIR)
    has_data = isfile(RESULTS_FILE) && filesize(RESULTS_FILE) > 0
    open(RESULTS_FILE, "a") do file
        if !has_data
            println(file, RESULTS_HEADER)
        end
        for row in rows
            println(file, join(row, ","))
        end
    end
end


function format_solution(solution, max_elements=10)
    n = length(solution)
    if n <= max_elements
        return "[" * join([@sprintf("%.4f", value) for value in solution], ", ") * "]"
    end
    limited = join([@sprintf("%.4f", value) for value in solution[1:max_elements]], ", ")
    return "[" * limited * ", ...]"
end


# ============================================================
# EXECUCAO
# O numero de threads e definido externamente (julia -t N).
# ============================================================
function main()
    if length(ARGS) < 1
        error("Uso: julia -t N monte_carlo_rastrigin_parallel.jl <points.csv>")
    end
    points_file = abspath(ARGS[1])
    num_workers = Threads.nthreads()
    if num_workers < 1
        error("A execucao exige pelo menos uma thread.")
    end

    # Carregamento e particionamento antes das medicoes.
    points = load_points(points_file)
    blocks = split_into_blocks(points, num_workers)

    # Aquecimento (compilacao JIT): nao contabilizado.
    for _ in 1:WARMUP_RUNS
        run_parallel(blocks)
    end

    times = zeros(MEASURED_RUNS)
    result_rows = Vector{Vector{String}}()
    best_value_final = Inf
    best_solution_final = nothing

    for run_number in 1:MEASURED_RUNS
        best_value, best_solution, elapsed_ms = run_parallel(blocks)
        times[run_number] = elapsed_ms
        push!(result_rows, [
            "Julia", "Rastrigin", "Paralela", string(num_workers), string(DIMENSIONS),
            string(length(points)), string(run_number), @sprintf("%.6f", elapsed_ms),
            @sprintf("%.10f", best_value)
        ])
        @printf("run %d: %.3f ms\n", run_number, elapsed_ms)

        if best_value < best_value_final
            best_value_final = best_value
            best_solution_final = best_solution
        end
    end

    # Escrita somente depois das medicoes.
    save_results(result_rows)

    avg_time = sum(times) / length(times)
    min_time = minimum(times)
    max_time = maximum(times)

    println("========================================")
    println("Funcao: Rastrigin")
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
    println("Resultados salvos em: ", RESULTS_FILE)
    println("========================================")
end

main()
