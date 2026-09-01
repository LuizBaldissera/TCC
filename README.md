mbiente de testes — TCC

Este documento contém os softwares necessários para preparar o computador que será utilizado nos experimentos do TCC.

Sistema operacional: Windows 10 ou Windows 11, 64 bits.

1. Linguagens e versões

Software

Versão recomendada

Python

3.14.7

Java

JDK 25 LTS

Julia

1.12.7

A página oficial da Oracle informa que o JDK 26 é a versão mais recente do Java SE, enquanto o JDK 25 é a versão LTS mais recente. Para o TCC, será utilizado o JDK 25 LTS, mantendo o ambiente de experimentação estável e fixo.

Fontes oficiais:

Python: https://www.python.org/downloads/

Java: https://www.oracle.com/java/technologies/downloads/

Julia: https://julialang.org/downloads/

2. Python

Python 3.14.7

Instalar Python 3.14.7 para Windows 64 bits.

Durante a instalação, habilitar:

Add Python to PATH

Verificar:

python --version

Esperado:

Python 3.14.7

pip

O pip será utilizado para instalar as bibliotecas do projeto.

Verificar:

python -m pip --version

NumPy , Matplotlib e pandas

Instalar:

python -m pip install numpy matplotlib pandas

Testar:

python -c "import numpy; import matplotlib; import pandas;  print('Python, NumPy, Matplotlib e Pandas OK')"

3. Java

JDK 25 LTS

Instalar o JDK 25 LTS para Windows 64 bits.

É necessário o JDK, pois os programas Java serão compilados durante o desenvolvimento e os testes.

Verificar:

java -version

e:

javac -version

Não será necessária nenhuma biblioteca externa de paralelização.

Serão utilizados recursos da própria plataforma Java, principalmente:

Thread
ExecutorService
java.util.concurrent

4. Julia

Julia 1.12.7

Instalar Julia 1.12.7 para Windows 64 bits.

A documentação oficial recomenda a utilização da versão estável mais recente.

Verificar:

julia --version

Paralelização por threads

Não é necessário instalar biblioteca externa para a utilização de threads.

Serão utilizados recursos nativos:

using Base.Threads
Threads.@threads

Verificar:

julia -e "println(Threads.nthreads())"

5. Ambientes de desenvolvimento

IntelliJ IDEA — Java

Instalar o IntelliJ IDEA para desenvolvimento dos códigos Java.

Download:
https://www.jetbrains.com/idea/download/

PyCharm — Python

Instalar o PyCharm para desenvolvimento dos códigos Python.

Download:
https://www.jetbrains.com/pycharm/download/

Visual Studio Code

Instalar também o Visual Studio Code.

Download:
https://code.visualstudio.com/

No VS Code, instalar as seguintes extensões:

Python

Python — Microsoft

Julia

Julia — julialang.language-julia

Java

Extension Pack for Java — Microsoft

A extensão oficial de Julia para VS Code fornece suporte à linguagem, REPL, execução e depuração.



7. Checklist

Instalar

Python 3.14.7

pip

NumPy

Matplotlib

JDK 25 LTS

Julia 1.12.7

IntelliJ IDEA

PyCharm

Visual Studio Code

Extensão Python para VS Code

Extensão Julia para VS Code

Extension Pack for Java para VS Code

8. Teste final

Após a instalação, executar:

python --version
python -m pip --version
java -version
javac -version
julia --version

Python:

python -c "import numpy; import matplotlib; print('Ambiente Python OK')"

Julia:

julia -e "using Base.Threads; println(Threads.nthreads())"

Depois desses testes, o computador estará preparado para receber e executar os códigos do TCC.
