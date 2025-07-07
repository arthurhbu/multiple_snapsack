from ortools.linear_solver import pywraplp

def carregar_instancia_mkp(caminho_arquivo):
    """
    Lê um arquivo de instância do Problema da Mochila Múltipla.
    Formato esperado:
    - Linha 1: número de mochilas
    - Linhas 2 a (1+num_mochilas): capacidades das mochilas (uma por linha)
    - Linha (2+num_mochilas): número de alunos
    - Linhas seguintes: peso valor (um aluno por linha)

    Retorna:
        (int): número de alunos
        (int): número de salas
        (list): lista de lucros dos itens
        (list): lista de pesos dos itens
        (list): lista de capacidades das mochilas
    """
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
        
    # Remove linhas vazias e espaços em branco
    linhas = [linha.strip() for linha in linhas if linha.strip()]
    
    # Lê o número de salas
    num_salas = int(linhas[0])
    
    # Lê as capacidades das salas
    capacidades_salas = []
    for i in range(1, num_salas + 1):
        capacidades_salas.append(int(linhas[i]))
    
    # Lê o número de alunos
    num_alunos = int(linhas[num_salas + 1])
    
    # Lê os dados dos alunos (peso valor)
    referencias = []
    lucros = []
    pesos = []
    for i in range(num_salas + 2, num_salas + 2 + num_alunos):
        peso, valor, referencia = map(int, linhas[i].split())
        pesos.append(peso)
        lucros.append(valor)
        referencias.append(referencia)
    
    # print(f"Instância '{caminho_arquivo}' carregada:")
    # print(f"  - Número de Alunos: {num_alunos}")
    # print(f"  - Número de Salas: {num_salas}")
    # print(f"  - Lucros (primeiros 5): {lucros[:5]}...")
    # print(f"  - Pesos (primeiros 5): {pesos[:5]}...")
    # print(f"  - Capacidades: {capacidades_salas}")
    # print(f"  - Referencia: {referencias}")
    
    return num_alunos, num_salas, capacidades_salas, referencias, pesos, lucros 

def main():
    try:
        num_alunos, num_salas, capacidades_salas, referencias_alunos, pesos, lucros = carregar_instancia_mkp('instancia_4.txt')

        data = {}
        data["weights"] = pesos
        data["values"] = lucros
        data["num_items"] = num_alunos
        data["all_items"] = range(data["num_items"])
        data["bin_capacities"] = capacidades_salas
        data["num_bins"] = num_salas
        data["all_bins"] = range(data["num_bins"])
        data["referencia_aluno"] = referencias_alunos

        
        print(f"Instância 'instancia_4.txt' carregada:")
        print(f"  - Número de Alunos: {num_alunos}")
        print(f"  - Número de Salas: {num_salas}")
        print(f"  - Lucros (primeiros 5): {lucros[:5]}...")
        print(f"  - Pesos (primeiros 5): {pesos[:5]}...")
        print(f"  - Capacidades: {capacidades_salas}")
        print(f"  - Referencia: {referencias_alunos}")


        referencias_unicas = sorted(list(set(data["referencia_aluno"])))
        print(f"  - Referências únicas encontradas nos alunos: {referencias_unicas}")


        data["referencia_sala"] = [None]*data["num_bins"]

        num_mapeamentos_possiveis = min(len(referencias_unicas), data["num_bins"])
        for i in range(num_mapeamentos_possiveis):
            data["referencia_sala"][i] = referencias_unicas[i]

        print(f"  - Referências mapeadas para as {data['num_bins']} salas: {data['referencia_sala']}")

        if len(referencias_unicas) != data["num_bins"]:
            print("\nAVISO: O número de salas na instância não corresponde ao número de tipos de referência únicos.")
            print(f"         Salas declaradas: {data['num_bins']}, Tipos de referência encontrados: {len(referencias_unicas)}")

        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None:
            print("Não foi possível criar o solver SCIP.")
            return

        x = {}
        for i in data["all_items"]:
            for b in data["all_bins"]:
                x[i, b] = solver.BoolVar(f"x_{i}_{b}")

        # Adiciona a restrição de compatibilidade CORRIGIDA E DINÂMICA
        for i in data["all_items"]:
            for b in data["all_bins"]:
                sala_ref = data["referencia_sala"][b]
                aluno_ref = data["referencia_aluno"][i]

                if sala_ref is None:
                    solver.Add(x[i, b] == 0)
                elif sala_ref != aluno_ref:
                    solver.Add(x[i, b] == 0)

        # Restrição: Cada aluno é alocado a no máximo uma sala.
        for i in data["all_items"]:
            solver.Add(sum(x[i, b] for b in data["all_bins"]) <= 1)

        # Restrição: A soma dos pesos dos alunos em uma sala não pode exceder a capacidade.
        for b in data["all_bins"]:
            solver.Add(
                sum(x[i, b] * data["weights"][i] for i in data["all_items"])
                <= data["bin_capacities"][b]
            )

        # Função Objetivo: Maximizar o valor total dos alunos alocados.
        objective = solver.Objective()
        for i in data["all_items"]:
            for b in data["all_bins"]:
                objective.SetCoefficient(x[i, b], data["values"][i])
        objective.SetMaximization()

        print(f"\nSolving with {solver.SolverVersion()}...")
        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            total_weight = 0
            for b in data["all_bins"]:
                print(f"\n--- Sala {b} (Capacidade: {data['bin_capacities'][b]}, Referência: {data['referencia_sala'][b]}) ---")
                bin_weight = 0
                bin_value = 0
                for i in data["all_items"]:
                    if x[i, b].solution_value() > 0:
                        print(
                            f"  - Aluno {i} (Valor: {data['values'][i]}, "
                            f"Ref: {data['referencia_aluno'][i]})"
                        )
                        bin_weight += data["weights"][i]
                        bin_value += data["values"][i]
                print(f"  Alunos na sala: {bin_weight:.0f}")
                print(f"  Valor da sala: {bin_value:.0f}")
                total_weight += bin_weight
            print(f"\nTotal de alunos alocados: {total_weight:.0f}")
            print(f"\nValor total otimizado: {objective.Value():.0f}")
        else:
            print("O problema não tem uma solução ótima.")

    except FileNotFoundError:
        print("\nArquivo de instância não encontrado.")
    except Exception as e:
        raise e

if __name__ == "__main__":
    main()