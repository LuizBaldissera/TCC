using DelimitedFiles
using Printf

# ============================================================
# CONFIGURACAO DO EXPERIMENTO
# ============================================================
const DIMENSIONS = 10
const WARMUP_RUNS = 1
const MEASURED_RUNS = 5
const PROJECT_DIR = normpath(joinpath(@__DIR__, ".."))
const RESULTS_DIR = joinpath(PROJECT_DIR, "Resultados")
const RESULTS_FILE = joinpath(RESULTS_DIR, "julia_sphere_sequencial.csv")
const RESULTS_HEADER = "linguagem,funcao,modo,workers,dimensoes,amostras,execucao,tempo_ms,melhor_valor"


# ============================================================
# FUNCAO DE BENCHMARK
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
# EXECUCAO SEQUENCIAL (uma medicao)
# O cronometro envolve somente a avaliacao das amostras.
# ============================================================
function run_sequential(points)
    best_solution = nothing
    best_value = Inf

    start_time = time_ns()
    for solution in points
        value = sphere(solution)
        if value < best_value
            best_value = value
            best_solution = solution
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
# ============================================================
function main()
    if length(ARGS) < 1
        error("Uso: julia monte_carlo_sphere.jl <points.csv>")
    end
    points_file = abspath(ARGS[1])

    # A leitura do CSV ocorre antes de qualquer medicao.
    points = load_points(points_file)

    # Aquecimento (compilacao JIT): nao contabilizado nas metricas.
    for _ in 1:WARMUP_RUNS
        run_sequential(points)
    end

    times = Float64[]
    result_rows = Vector{Vector{String}}()
    best_value_final = Inf
    best_solution_final = nothing

    for run_number in 1:MEASURED_RUNS
        best_value, best_solution, elapsed_ms = run_sequential(points)
        push!(times, elapsed_ms)
        push!(result_rows, [
            "Julia", "Sphere", "Sequencial", "1", string(DIMENSIONS),
            string(length(points)), string(run_number), @sprintf("%.6f", elapsed_ms),
            @sprintf("%.10f", best_value)
        ])
        @printf("run %d: %.3f ms\n", run_number, elapsed_ms)

        if best_value < best_value_final
            best_value_final = best_value
            best_solution_final = best_solution
        end
    end

    # A escrita no CSV acontece somente depois das medicoes.
    save_results(result_rows)

    avg_time = sum(times) / length(times)
    min_time = minimum(times)
    max_time = maximum(times)

    println("========================================")
    println("Funcao: Sphere")
    println("Linguagem: Julia")
    println("Execucao: Sequencial")
    println("Workers: 1")
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
