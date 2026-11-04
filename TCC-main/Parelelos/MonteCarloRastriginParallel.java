import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class MonteCarloRastriginParallel {

    // ============================================================
    // CONFIGURACAO DO EXPERIMENTO
    // ============================================================
    static final int DIMENSIONS = 10;
    static final int WARMUP_RUNS = 1;
    static final int MEASURED_RUNS = 5;
    static final String RESULTS_HEADER =
            "linguagem,funcao,modo,workers,dimensoes,amostras,execucao,tempo_ms,melhor_valor";

    // ============================================================
    // FUNCAO DE BENCHMARK
    // ============================================================
    static double rastrigin(double[] x) {
        double total = 10 * x.length;
        for (int i = 0; i < x.length; i++) {
            total += x[i] * x[i] - 10 * Math.cos(2 * Math.PI * x[i]);
        }
        return total;
    }

    static class LocalResult {
        final double bestValue;
        final double[] bestSolution;

        LocalResult(double bestValue, double[] bestSolution) {
            this.bestValue = bestValue;
            this.bestSolution = bestSolution;
        }
    }

    static class RunResult {
        final double bestValue;
        final double[] bestSolution;
        final double elapsedMs;

        RunResult(double bestValue, double[] bestSolution, double elapsedMs) {
            this.bestValue = bestValue;
            this.bestSolution = bestSolution;
            this.elapsedMs = elapsedMs;
        }
    }

    static class BlockTask implements Callable<LocalResult> {
        private final List<double[]> block;

        BlockTask(List<double[]> block) {
            this.block = block;
        }

        @Override
        public LocalResult call() {
            double bestValue = Double.POSITIVE_INFINITY;
            double[] bestSolution = null;
            for (double[] solution : block) {
                double value = rastrigin(solution);
                if (value < bestValue) {
                    bestValue = value;
                    bestSolution = solution;
                }
            }
            return new LocalResult(bestValue, bestSolution);
        }
    }

    // ============================================================
    // LOCALIZA A PASTA RAIZ DO PROJETO
    // ============================================================
    static Path findProjectDirectory(Path start) {
        Path current = start.toAbsolutePath().normalize();
        while (current != null) {
            if (Files.isDirectory(current.resolve("Parelelos"))
                    && Files.isDirectory(current.resolve("Sequenciais"))) {
                return current;
            }
            current = current.getParent();
        }
        return null;
    }

    static Path projectDirectory() {
        Path fromWorkingDirectory = findProjectDirectory(Paths.get("."));
        if (fromWorkingDirectory != null) return fromWorkingDirectory;
        try {
            Path classDirectory = Paths.get(
                    MonteCarloRastriginParallel.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            Path fromClassLocation = findProjectDirectory(classDirectory);
            if (fromClassLocation != null) return fromClassLocation;
            if (classDirectory.getFileName() != null
                    && (classDirectory.getFileName().toString().equals("Parelelos")
                    || classDirectory.getFileName().toString().equals("Sequenciais"))) {
                return classDirectory.getParent();
            }
        } catch (Exception ignored) {
            // Usa o diretorio atual como alternativa.
        }
        return Paths.get(".").toAbsolutePath().normalize();
    }

    // ============================================================
    // LEITURA DOS PONTOS (NAO cronometrada)
    // ============================================================
    static List<double[]> loadPoints(Path filePath) throws IOException {
        if (!Files.exists(filePath)) {
            throw new IOException("Arquivo de pontos nao encontrado: " + filePath
                    + ". Execute generate_points.py primeiro.");
        }
        List<double[]> points = new ArrayList<>();
        try (BufferedReader reader = Files.newBufferedReader(filePath, StandardCharsets.UTF_8)) {
            String line;
            int lineNumber = 0;
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                if (line.isBlank()) continue;
                String[] parts = line.split(",", -1);
                if (parts.length != DIMENSIONS) {
                    throw new IOException("Linha " + lineNumber + " de " + filePath
                            + " possui " + parts.length + " dimensoes; eram esperadas " + DIMENSIONS + ".");
                }
                double[] point = new double[DIMENSIONS];
                for (int i = 0; i < DIMENSIONS; i++) {
                    point[i] = Double.parseDouble(parts[i]);
                }
                points.add(point);
            }
        }
        if (points.isEmpty()) throw new IOException("Nenhum ponto foi encontrado em " + filePath + ".");
        return points;
    }

    // ============================================================
    // PARTICIONAMENTO (NAO cronometrado)
    // ============================================================
    static List<List<double[]>> splitIntoBlocks(List<double[]> points, int numWorkers) {
        List<List<double[]>> blocks = new ArrayList<>();
        int blockSize = (int) Math.ceil((double) points.size() / numWorkers);
        for (int start = 0; start < points.size(); start += blockSize) {
            int end = Math.min(start + blockSize, points.size());
            blocks.add(points.subList(start, end));
        }
        return blocks;
    }

    // ============================================================
    // EXECUCAO PARALELA (uma medicao)
    // Mede submissao das tarefas, processamento e reducao.
    // Leitura, particionamento e gravacao ficam fora do cronometro.
    // ============================================================
    static RunResult runParallel(ExecutorService executor, List<List<double[]>> blocks)
            throws InterruptedException, ExecutionException {
        long startTime = System.nanoTime();

        List<Future<LocalResult>> futures = new ArrayList<>();
        for (List<double[]> block : blocks) {
            futures.add(executor.submit(new BlockTask(block)));
        }

        double bestValue = Double.POSITIVE_INFINITY;
        double[] bestSolution = null;
        for (Future<LocalResult> future : futures) {
            LocalResult result = future.get();
            if (result.bestValue < bestValue) {
                bestValue = result.bestValue;
                bestSolution = result.bestSolution;
            }
        }

        long endTime = System.nanoTime();
        double elapsedMs = (endTime - startTime) / 1_000_000.0;
        return new RunResult(bestValue, bestSolution, elapsedMs);
    }

    // ============================================================
    // GRAVACAO DOS RESULTADOS (NAO cronometrada)
    // ============================================================
    static void saveResults(Path resultsFile, List<String> rows) throws IOException {
        Files.createDirectories(resultsFile.getParent());
        boolean hasData = Files.exists(resultsFile) && Files.size(resultsFile) > 0;
        List<String> lines = new ArrayList<>();
        if (!hasData) lines.add(RESULTS_HEADER);
        lines.addAll(rows);
        Files.write(resultsFile, lines, StandardCharsets.UTF_8,
                StandardOpenOption.CREATE, StandardOpenOption.APPEND);
    }

    static String formatSolution(double[] solution, int maxElements) {
        StringBuilder result = new StringBuilder("[");
        int limit = Math.min(solution.length, maxElements);
        for (int i = 0; i < limit; i++) {
            result.append(String.format(Locale.US, "%.4f", solution[i]));
            if (i < limit - 1) result.append(", ");
        }
        if (solution.length > maxElements) result.append(", ...");
        result.append("]");
        return result.toString();
    }

    // ============================================================
    // EXECUCAO
    // ============================================================
    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
        if (args.length < 2) {
            System.out.println("Uso: java MonteCarloRastriginParallel <points.csv> <num_threads>");
            return;
        }
        Path pointsFile = Paths.get(args[0]).toAbsolutePath().normalize();
        int numWorkers = Integer.parseInt(args[1]);
        if (numWorkers < 1) throw new IllegalArgumentException("O numero de threads deve ser maior que zero.");

        Path projectDir = projectDirectory();
        Path resultsFile = projectDir.resolve("Resultados").resolve("java_rastrigin_paralelo_" + numWorkers + "_workers.csv");

        // Leitura e particionamento antes das medicoes.
        List<double[]> points = loadPoints(pointsFile);
        List<List<double[]>> blocks = splitIntoBlocks(points, numWorkers);
        ExecutorService executor = Executors.newFixedThreadPool(numWorkers);

        double[] times = new double[MEASURED_RUNS];
        List<String> resultRows = new ArrayList<>();
        double bestValueFinal = Double.POSITIVE_INFINITY;
        double[] bestSolutionFinal = null;

        try {
            // Aquecimento da JVM: nao contabilizado.
            for (int i = 0; i < WARMUP_RUNS; i++) runParallel(executor, blocks);

            for (int i = 0; i < MEASURED_RUNS; i++) {
                RunResult result = runParallel(executor, blocks);
                times[i] = result.elapsedMs;
                resultRows.add(String.format(Locale.US,
                        "Java,Rastrigin,Paralela,%d,%d,%d,%d,%.6f,%.10f",
                        numWorkers, DIMENSIONS, points.size(), i + 1,
                        result.elapsedMs, result.bestValue));
                System.out.printf(Locale.US, "run %d: %.3f ms%n", i + 1, result.elapsedMs);

                if (result.bestValue < bestValueFinal) {
                    bestValueFinal = result.bestValue;
                    bestSolutionFinal = result.bestSolution;
                }
            }
        } finally {
            executor.shutdown();
        }

        // Gravacao somente depois das medicoes.
        saveResults(resultsFile, resultRows);

        double sum = 0.0;
        double min = Double.POSITIVE_INFINITY;
        double max = Double.NEGATIVE_INFINITY;
        for (double time : times) {
            sum += time;
            min = Math.min(min, time);
            max = Math.max(max, time);
        }
        double average = sum / times.length;

        System.out.println("========================================");
        System.out.println("Funcao: Rastrigin");
        System.out.println("Linguagem: Java");
        System.out.println("Execucao: Paralela");
        System.out.println("Workers: " + numWorkers);
        System.out.println("Dimensoes: " + DIMENSIONS);
        System.out.println("Amostras: " + points.size());
        System.out.println("----------------------------------------");
        System.out.printf(Locale.US, "Melhor valor: %.6f%n", bestValueFinal);
        System.out.printf(Locale.US, "Tempo medio: %.2f ms%n", average);
        System.out.printf(Locale.US, "Tempo minimo: %.2f ms%n", min);
        System.out.printf(Locale.US, "Tempo maximo: %.2f ms%n", max);
        System.out.println("Melhor solucao: " + formatSolution(bestSolutionFinal, 10));
        System.out.println("Resultados salvos em: " + resultsFile);
        System.out.println("========================================");
    }
}
