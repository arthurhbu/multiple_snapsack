'''
Problema de alocação de alunos em salas com demanda reprimida, ou seja, 
para alunos que aguardam matrícula nas unidades escolares. 
Problema baseado no problema da mochila múltipla.

Onde:
    - Cada aluno tem uma referência para a sala de destino que ele deseja.
    - Cada sala tem uma capacidade.
    - Cada aluno tem um peso e um valor/pontuação que define a importância dele.
    - O objetivo é maximizar o valor total dos alunos alocados.
    - O peso total dos alunos alocados não pode exceder a capacidade da sala.
    - Cada aluno é alocado a no máximo uma sala.
'''

from ortools.linear_solver import pywraplp
import os 

def carregar_instancia(caminho_arquivo):
    """
    Lê e interpreta um arquivo de instância para o problema de alocação de alunos.

    Formato do arquivo esperado:
      - Linha 1: Número total de salas (mochilas).
      - Próximas N linhas: Capacidade de cada uma das N salas.
      - Linha N+2: Número total de alunos (itens).
      - Próximas M linhas: Dados de cada um dos M alunos no formato "peso valor referencia".

    Args:
      caminho_arquivo (str): O caminho para o arquivo da instância.

    Returns:
      tuple: Uma tupla contendo (num_alunos, num_salas, capacidades, referencias, pesos, valores).
    """
    with open(caminho_arquivo, 'r') as f:
        # Remove linhas vazias e espaços em branco para evitar erros de leitura
        linhas = [linha.strip() for linha in f.readlines() if linha.strip()]
    
    # Extrai dados do cabeçalho
    num_salas = int(linhas[0])
    capacidades_salas = [int(linha) for linha in linhas[1:num_salas + 1]]
    num_alunos = int(linhas[num_salas + 1])
    
    # Extrai os dados dos alunos (peso | valor/pontuação | referencia_sala)
    pesos, valores, referencias = [], [], []
    for i in range(num_salas + 2, num_salas + 2 + num_alunos):
        peso, valor, referencia = map(int, linhas[i].split())
        pesos.append(peso)
        valores.append(valor)
        referencias.append(referencia)
    
    return num_alunos, num_salas, capacidades_salas, referencias, pesos, valores 

def solve_demanda_reprimida(nome_instancia, nome_solver):
    """
    Resolve uma instância do problema de alocação de alunos.

    Esta função carrega os dados de um arquivo, monta o modelo de otimização,
    aciona o solver e escreve os resultados em um arquivo de saída.

    Args:
        nome_instancia (str): Nome do arquivo da instância (ex: 'instancia_1.txt').
        nome_solver (str): Nome do solver a ser usado pelo OR-Tools (ex: 'SCIP').
    """
    try:
        # Carrega os dados da instância a partir do arquivo
        caminho_instancia = f'instancias/{nome_instancia}'
        num_alunos, num_salas, capacidades, referencias, pesos, valores = carregar_instancia(caminho_instancia)
        nome_instancia = nome_instancia.replace('.txt', '') # Remove a extensão do nome da instância

        # Organiza os dados em um dicionário para fácil acesso
        data = {
            "pesos": pesos,
            "valores": valores,
            "referencias": referencias,
            "num_alunos": num_alunos,
            "all_alunos": range(num_alunos),
            "capacidades": capacidades,
            "num_salas": num_salas,
            "all_salas": range(num_salas),
        }

        # Cria o solver
        solver = pywraplp.Solver.CreateSolver(nome_solver)
        if not solver:
            print(f"Não foi possível criar o solver {nome_solver}.")
            return

        # Cria as variáveis de decisão
        # x[i, b] é 1 se o aluno 'i' for alocado na sala 'b', e 0 caso contrário.
        x = {}
        for i in data["all_alunos"]:
            for b in data["all_salas"]:
                x[i, b] = solver.BoolVar(f"x_{i}_{b}")

        # Adiciona as restrições do modelo
        # Restrição de Compatibilidade (Endereçamento Direto):
        # Um aluno só pode ser alocado na sala indicada por sua referência.
        for i in data["all_alunos"]:
            aluno_ref_destino = data["referencias"][i]
            for b in data["all_salas"]:
                if b != (aluno_ref_destino - 1):
                    solver.Add(x[i, b] == 0)

        # Restrição de Alocação Única
        # Cada aluno pode ser alocado em no máximo uma sala.
        for i in data["all_alunos"]:
            solver.Add(sum(x[i, b] for b in data["all_salas"]) <= 1)

        # Restrição de Capacidade da Sala
        # A soma dos pesos dos alunos não pode exceder a capacidade da sala.
        for b in data["all_salas"]:
            solver.Add(
                sum(x[i, b] * data["pesos"][i] for i in data["all_alunos"]) <= data["capacidades"][b]
            )
        
        # Função Objetivo
        # Maximizar o valor (pontuação) total dos alunos alocados.
        objective = solver.Objective()
        for i in data["all_alunos"]:
            for b in data["all_salas"]:
                objective.SetCoefficient(x[i, b], data["valores"][i])
        objective.SetMaximization()

        # Resolve o problema com o solver escolhido
        print(f"Solving with {solver.SolverVersion()}...")
        status = solver.Solve()

        # Escreve o cabeçalho e a solução no arquivo de saída
        # Arquivo de saída: resultados_instancias/{nome_instancia}_saida.txt
        with open(f'resultados_instancias/{nome_instancia}_saida.txt', 'w', encoding='utf-8') as f:
            f.write(f"Instância '{nome_instancia}' resolvida com {nome_solver}:\n")
            f.write(f"  - Número de Alunos: {num_alunos}\n")
            f.write(f"  - Número de Salas: {num_salas}\n")
            f.write("_______________________________________________________________\n\n")

            if status == pywraplp.Solver.OPTIMAL:
                f.write(f"Solução ótima encontrada:\n")
                f.write(f"  - Valor total otimizado: {objective.Value():.0f}\n")
                f.write("_______________________________________________________________\n\n")
                total_alunos_alocados = 0
                for b in data["all_salas"]:
                    f.write(f"Sala {b+1} (Capacidade: {data['capacidades'][b]}):\n")
                    alunos_na_sala = 0
                    valor_na_sala = 0
                    for i in data["all_alunos"]:
                        if x[i, b].solution_value() > 0.5: # Verifica se x[i,b] == 1
                            f.write(f"  - Aluno {i} (Valor: {data['valores'][i]}, Ref: {data['referencias'][i]})\n")
                            alunos_na_sala += data["pesos"][i] # Assumindo peso=1 por aluno
                            valor_na_sala += data["valores"][i]
                    f.write(f"  Total de alunos na sala: {alunos_na_sala:.0f}\n")
                    f.write(f"  Valor total da sala: {valor_na_sala:.0f}\n")
                    f.write("_______________________________________________________________\n\n")
                    total_alunos_alocados += alunos_na_sala
                
                f.write(f"Resumo Final:\n")
                f.write(f"  - Total de alunos alocados: {total_alunos_alocados:.0f}\n")
                f.write(f"  - Total de alunos não alocados: {num_alunos - total_alunos_alocados:.0f}\n")
            else:
                f.write("O problema não tem uma solução ótima.\n")

    except FileNotFoundError:
        print(f"\nArquivo de instância não encontrado: {caminho_instancia}\n")
    except Exception as e:
        print(f"\nErro ao resolver a instância {nome_instancia}: {e}\n")

def main():
    """
    Executa o solver para todas as instâncias encontradas no diretório 'instancias'.
    """
    path_instancias = "instancias/"
    # Garante que o diretório de resultados exista
    os.makedirs("resultados_instancias", exist_ok=True)
    
    # Itera sobre todos os arquivos no diretório de instâncias
    for file in os.listdir(path_instancias):
        if file.endswith(".txt"): # Garante que apenas arquivos de texto sejam lidos
            print(f"Resolvendo instância {file}...")
            solve_demanda_reprimida(nome_instancia=file, nome_solver="SCIP")
            print(f"Instância {file} finalizada. Resultado salvo em 'resultados_instancias/'.\n")

if __name__ == "__main__":
    main()