import java.util.Random;

public class MonteCarloRastrigin {

    // ============================================================
    // PARAMETROS (mesmos valores devem ser usados em todas as linguagens)
    // ============================================================
    static final int DIMENSIONS = 10;
    static final int ITERATIONS = 1000000;
    static final double MIN_VALUE = -5.12;
    static final double MAX_VALUE = 5.12;
    static final long SEED = 42L;

    // ============================================================
    // FUNCAO DE BENCHMARK: RASTRIGIN
    // f(x) = 10n + sum(x_i^2 - 10*cos(2*pi*x_i))
    // ============================================================
    static double rastrigin(double[] x) {
        int n = x.length;
        double total = 10 * n;
        for (int i = 0; i < n; i++) {
            total += x[i] * x[i] - 10 * Math.cos(2 * Math.PI * x[i]);
        }
        return total;
    }

    // ============================================================
    // GERACAO DE UMA SOLUCAO ALEATORIA
    // Estrutura isolada em metodo proprio para facilitar, no futuro,
    // a substituicao por leitura de pontos pre-gerados em arquivo.
    // ============================================================
    static double[] generateRandomSolution(Random random, int dimensions, double minValue, double maxValue) {
        double[] solution = new double[dimensions];
        for (int i = 0; i < dimensions; i++) {
            solution[i] = minValue + random.nextDouble() * (maxValue - minValue);
        }
        return solution;
    }

    // ============================================================
    // FORMATACAO DA SOLUCAO PARA IMPRESSAO
    // ============================================================
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

    // ============================================================
    // EXECUCAO
    // ============================================================
    public static void main(String[] args) {
        Random random = new Random(SEED);

        double[] bestSolution = null;
        double bestValue = Double.POSITIVE_INFINITY;

        // ============================================================
        // ALGORITMO MONTE CARLO (BUSCA ALEATORIA)
        // Cada amostra e avaliada de forma independente, o que facilita
        // a futura substituicao do loop sequencial por paralelizacao.
        // ============================================================
        long startTime = System.nanoTime();

        for (int i = 0; i < ITERATIONS; i++) {
            double[] solution = generateRandomSolution(random, DIMENSIONS, MIN_VALUE, MAX_VALUE);
            double value = rastrigin(solution);

            if (value < bestValue) {
                bestValue = value;
                bestSolution = solution;
            }
        }

        long endTime = System.nanoTime();
        double elapsedMs = (endTime - startTime) / 1_000_000.0;

        // ============================================================
        // IMPRESSAO DOS RESULTADOS
        // ============================================================
        System.out.println("Funcao: Rastrigin");
        System.out.println("Dimensoes: " + DIMENSIONS);
        System.out.println("Iteracoes: " + ITERATIONS);
        System.out.println("Melhor valor: " + String.format("%.6f", bestValue));
        System.out.println("Tempo de execucao: " + String.format("%.3f", elapsedMs) + " ms");
        System.out.println("Melhor solucao: " + formatSolution(bestSolution, 10));
    }
}
