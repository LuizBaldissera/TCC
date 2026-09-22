import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class MonteCarloSphereParallel {

    // ============================================================
    // PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
    // ============================================================
    static final int DIMENSIONS = 10;
    static final long NUM_SAMPLES = 5_000_000;
    static final double MIN_VALUE = -5.12;
    static final double MAX_VALUE = 5.12;
    static final String POINTS_FILE = "points.csv";

    static final int WARMUP_RUNS = 1;
    static final int MEASURED_RUNS = 5;

    // ============================================================
    // FUNCAO DE BENCHMARK: SPHERE
    // f(x) = sum(x_i^2)
    // ============================================================
    static double sphere(double[] x) {
        double total = 0.0;
        for (int i = 0; i < x.length; i++) {
            total += x[i] * x[i];
        }
        return total;
    }

    // ============================================================
    // RESULTADO LOCAL DE UMA TAREFA (melhor valor + melhor solucao)
    // ============================================================
    static class LocalResult {
        final double bestValue;
        final double[] bestSolution;

        LocalResult(double bestValue, double[] bestSolution) {
            this.bestValue = bestValue;
            this.bestSolution = bestSolution;
        }
    }

    // ============================================================
    // TAREFA: avalia um bloco de pontos e retorna o melhor local.
    // Nenhuma variavel compartilhada e atualizada aqui.
    // ============================================================
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
                double value = sphere(solution);
                if (value < bestValue) {
                    bestValue = value;
                    bestSolution = solution;
                }
            }

            return new LocalResult(bestValue, bestSolution);
        }
    }

    // ============================================================
    // LEITURA DOS PONTOS (NAO cronometrada)
    // ============================================================
    static List<double[]> loadPoints(String filePath) throws IOException {
        List<double[]> points = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            while ((line = br.readLine()) != null) {
                if (line.isBlank()) {
                    continue;
                }
                String[] parts = line.split(",");
                double[] point = new double[parts.length];
                for (int i = 0; i < parts.length; i++) {
                    point[i] = Double.parseDouble(parts[i]);
                }
                points.add(point);
            }
        }
        return points;
    }

    // ============================================================
    // PARTICIONAMENTO (AGGLOMERATION)
    // Divide os pontos em blocos aproximadamente iguais, um por worker,
    // reduzindo o overhead de criar uma tarefa por amostra.
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
    // Mede apenas: submissao das tarefas + calculo + combinacao (reducao).
    // Cada thread mantem seu proprio melhor local (LocalResult); nao ha
    // variavel global atualizada dentro do loop, evitando contencao.
    // ============================================================
    static Object[] runParallel(ExecutorService executor, List<List<double[]>> blocks)
            throws InterruptedException, ExecutionException {

        long startTime = System.nanoTime();

        List<Future<LocalResult>> futures = new ArrayList<>();
        for (List<double[]> block : blocks) {
            futures.add(executor.submit(new BlockTask(block)));
        }

        // Combinacao (reducao) dos melhores locais -> melhor global
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

        return new Object[]{bestValue, bestSolution, elapsedMs};
    }

    static String formatSolution(double[] solution, int maxElements) {
        StringBuilder sb = new StringBuilder("[");
        int limit = Math.min(solution.length, maxElements);
        for (int i = 0; i < limit; i++) {
            sb.append(String.format("%.4f", solution[i]));
            if (i < limit - 1) {
                sb.append(", ");
            }
        }
        if (solution.length > maxElements) {
            sb.append(", ...");
        }
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
        if (args.length < 1) {
            System.out.println("Uso: java MonteCarloSphereParallel <num_threads>");
            return;
        }

        int numWorkers = Integer.parseInt(args[0]);

        // Carregamento dos dados e particionamento (NAO cronometrados)
        List<double[]> points = loadPoints(POINTS_FILE);
        List<List<double[]>> blocks = splitIntoBlocks(points, numWorkers);

        // Configuracao inicial (NAO cronometrada)
        ExecutorService executor = Executors.newFixedThreadPool(numWorkers);

        // Execucao de aquecimento (JIT/GC) - NAO contabilizada nas metricas
        for (int i = 0; i < WARMUP_RUNS; i++) {
            runParallel(executor, blocks);
        }

        // Execucoes medidas
        double[] times = new double[MEASURED_RUNS];
        double bestValueFinal = Double.POSITIVE_INFINITY;
        double[] bestSolutionFinal = null;

        for (int i = 0; i < MEASURED_RUNS; i++) {
            Object[] result = runParallel(executor, blocks);
            double bestValue = (double) result[0];
            double[] bestSolution = (double[]) result[1];
            double elapsedMs = (double) result[2];

            times[i] = elapsedMs;
            System.out.printf("run %d: %.3f ms%n", i + 1, elapsedMs);

            if (bestValue < bestValueFinal) {
                bestValueFinal = bestValue;
                bestSolutionFinal = bestSolution;
            }
        }

        executor.shutdown();

        double sum = 0;
        double min = Double.POSITIVE_INFINITY;
        double max = Double.NEGATIVE_INFINITY;
        for (double t : times) {
            sum += t;
            if (t < min) min = t;
            if (t > max) max = t;
        }
        double avg = sum / times.length;

        System.out.println("========================================");
        System.out.println("Funcao: Sphere");
        System.out.println("Linguagem: Java");
        System.out.println("Execucao: Paralela");
        System.out.println("Workers: " + numWorkers);
        System.out.println("Dimensoes: " + DIMENSIONS);
        System.out.println("Amostras: " + points.size());
        System.out.println("----------------------------------------");
        System.out.println("Melhor valor: " + String.format("%.6f", bestValueFinal));
        System.out.println("Tempo medio: " + String.format("%.2f", avg) + " ms");
        System.out.println("Tempo minimo: " + String.format("%.2f", min) + " ms");
        System.out.println("Tempo maximo: " + String.format("%.2f", max) + " ms");
        System.out.println("Melhor solucao: " + formatSolution(bestSolutionFinal, 10));
        System.out.println("========================================");
    }
}
