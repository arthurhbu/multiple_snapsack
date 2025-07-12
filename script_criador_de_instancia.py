'''
    Script para criar uma instância de problema de mochila múltipla.

    A instão criada é baseada no arquivo .dat do problema da demanda reprimida. 
    O arquivo .dat é a forma original das informações do problema. 
'''

def get_arquivo(filename):
    with open(filename, 'r') as file:
        return file.readlines()
    

get_arquivo('instancia_6.dat')

def parse_dat_file(filename):
    dados = {}
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Detecta início de bloco de conjunto
        if line.startswith('#'):
            # print(line)
            i += 1
            continue

        elif line.startswith('set a:'):
            nome = line.split()[1].replace(':=', '')
            bloco = []
            i += 1
            while i < len(lines) and ';' not in lines[i]:
                bloco.extend(lines[i].strip().split())
                i += 1
            # Pega a última linha (com ;)
            if i < len(lines):
                bloco.extend(lines[i].replace(';', '').strip().split())
            dados[nome] = bloco
        # Detecta início de bloco de parâmetro

        elif line.startswith('set v:'):
            nome = line.split()[1].replace(':=', '')
            line = line.replace('set v:=', '').strip()
            line = line.replace(';', '')
            bloco = [valor.strip() for valor in line.split() if valor.strip()]
            dados[nome] = bloco

        elif line.startswith('param:'):
            nome = line.split(':')[1].split(':')[0].strip()
            bloco = []
            i += 1
            while i < len(lines) and ';' not in lines[i]:
                valores = lines[i].strip().split('\t')
                if len(valores) >= 2:
                    bloco.append(valores[1].strip())
                i += 1
            if i < len(lines):
                valores = lines[i].replace(';', '').strip().split('\t')
                if len(valores) >= 2:
                    bloco.append(valores[1].strip())
            dados[nome] = bloco

            
        i += 1
    return dados


def create_instance(dados):
    with open('instancia_criada_6.txt', 'w', encoding='utf-8') as file:
        file.write(f'{len(dados["v"])}')
        file.write('\n')
        for i in range(len(dados["v"])):
            vagas_int = int(dados['vagas'][i])
            file.write(f'{vagas_int}')
            file.write('\n')
        file.write(f'{len(dados["a"])}')
        file.write('\n')
        for i in range(len(dados["a"])):
            pontos_int = int(dados['pontos'][i])
            referencia_aluno_int = int(dados['referencia_aluno'][i])
            line = f'{int(1)} {pontos_int} {referencia_aluno_int}'
            file.write(f'{line}')
            file.write('\n')
    return
    
dados = parse_dat_file('instancia_6.dat')
create_instance(dados)




'''
len(v)
todas as vagas
len(a)
peso | pontos | referencia_aluno
'''