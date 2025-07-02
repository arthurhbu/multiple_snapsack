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
        (int): número de itens
        (int): número de mochilas
        (list): lista de lucros dos itens
        (list): lista de pesos dos itens
        (list): lista de capacidades das mochilas
    """
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()
        
    # Remove linhas vazias e espaços em branco
    linhas = [linha.strip() for linha in linhas if linha.strip()]
    
    # Lê o número de mochilas
    num_mochilas = int(linhas[0])
    
    # Lê as capacidades das mochilas
    capacidades = []
    for i in range(1, num_mochilas + 1):
        capacidades.append(int(linhas[i]))
    
    # Lê o número de alunos
    num_alunos = int(linhas[num_mochilas + 1])
    
    # Lê os dados dos alunos (peso valor)
    referencias = []
    lucros = []
    pesos = []
    for i in range(num_mochilas + 2, num_mochilas + 2 + num_alunos):
        peso, valor, referencia = map(int, linhas[i].split())
        pesos.append(peso)
        lucros.append(valor)
        referencias.append(referencia)
    
    num_itens = num_alunos

    print(f"Instância '{caminho_arquivo}' carregada:")
    print(f"  - Número de Itens: {num_itens}")
    print(f"  - Número de Mochilas: {num_mochilas}")
    print(f"  - Lucros (primeiros 5): {lucros[:5]}...")
    print(f"  - Pesos (primeiros 5): {pesos[:5]}...")
    print(f"  - Capacidades: {capacidades}")
    print(f"  - Referencia: {referencias}")
    
    return num_itens, num_mochilas, lucros, pesos, capacidades, referencia

def main():

    try:
        num_i, num_m, lucros, pesos, caps, referencia = carregar_instancia_mkp('instancia_4.txt')

        data = {}

        data["weights"] = pesos
        data["values"] = lucros
        data["num_items"] = num_i
        data["all_items"] = range(data["num_items"])
        data["bin_capacities"] = caps
        data["num_bins"] = num_m
        data["all_bins"] = range(data["num_bins"])
        data["referencia"] = referencia 

        solver = pywraplp.Solver.CreateSolver('SCIP')
        if solver is None: 
            print("Não foi possível criar o solver SCIP.")
            return
        
        x = {}
        for i in data["all_items"]:
            for b in data["all_bins"]:
                x[i, b] = solver.BoolVar(f"x_{i}_{b}")

        # Each ite m is assigned to at most one bin.
        for i in data["all_items"]:
            solver.Add(sum(x[i, b] for b in data["all_bins"]) <= 1)

        # The amount packed in each bin cannot exceed its capacity.
        for b in data["all_bins"]:
            solver.Add(
                sum(x[i, b] * data["weights"][i] for i in data["all_items"])
                <= data["bin_capacities"][b]
            )

        # Maximize total value of packed items.
        objective = solver.Objective()
        for i in data["all_items"]:
            for b in data["all_bins"]:
                objective.SetCoefficient(x[i, b], data["values"][i])
        objective.SetMaximization()

        print(f"Solving with {solver.SolverVersion()}")
        status = solver.Solve() 

        if status == pywraplp.Solver.OPTIMAL:
            print(f"Total packed value: {objective.Value()}")
            total_weight = 0
            for b in data["all_bins"]:
                print(f"Bin {b}")
                bin_weight = 0
                bin_value = 0
                for i in data["all_items"]:
                    if x[i, b].solution_value() > 0:
                        print(
                            f"Item {i} weight: {data['weights'][i]} value:"
                            f" {data['values'][i]}"
                        )
                        bin_weight += data["weights"][i]
                        bin_value += data["values"][i]
                print(f"Packed bin weight: {bin_weight}")
                print(f"Packed bin value: {bin_value}\n")
                total_weight += bin_weight
            print(f"Total packed weight: {total_weight}")
        else:
            print("The problem does not have an optimal solution.")

    except FileNotFoundError:
        print("\nArquivo 'instancia_pequena.txt' não encontrado.")
        print("Por favor, crie o arquivo com o conteúdo da Instância 1 para testar a função.")

if __name__ == "__main__":
    main()