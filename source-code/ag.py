###################################
## Algoritmo Genetico

###################################
from random import randint
import string
import snoop
from icecream import ic
import os
import sys
import ast
from varname import nameof

class AlgoritmoGenetico():
    """
        Algoritmo genético para encontrar o x para o qual a função x^2 - 3x + 4 assume o valor máximo
    """
    #@snoop
    def __init__(self, x_min, x_max, tam_populacao, taxa_mutacao, taxa_crossover, num_geracoes, param_eq):
        """
            Inicializa todos os atributos da instância
        """
        self.x_min = x_min
        self.x_max = x_max
        self.tam_populacao = tam_populacao
        self.taxa_mutacao = taxa_mutacao
        self.taxa_crossover = taxa_crossover
        self.num_geracoes = num_geracoes
        self.param_eq = param_eq
        # calcula o número de bits do x_min e x_máx no formato binário com sinal
        qtd_bits_x_min = len(bin(x_min).replace('0b', '' if x_min < 0 else '+'))
        qtd_bits_x_max = len(bin(x_max).replace('0b', '' if x_max < 0 else '+'))
        # o maior número de bits representa o número de bits a ser utilizado para gerar individuos
        self.num_bits = qtd_bits_x_max if qtd_bits_x_max >= qtd_bits_x_min else qtd_bits_x_min
        # gera os individuos da população
        self._gerar_populacao()
    #@snoop
    def _gerar_populacao(self):
        """
            Gera uma população de um determinado tamanho com individuos que possuem um número
            expecífico de bits
        """
        # inicializa uma população de "tam_população" inviduos vazios
        self.populacao = [[] for i in range(self.tam_populacao)]
        # preenche a população
        for individuo in self.populacao:
            # para cada individuo da população sorteia números entre "x_min" e "x_max"
            num = randint(self.x_min, self.x_max)
            # converte o número sorteado para formato binário com sinal
            num_bin = bin(num).replace('0b', '' if num < 0 else '+').zfill(self.num_bits)
            # transforma o número binário resultante em um vetor
            for bit in num_bin:
                individuo.append(bit)
    #@snoop
    def _funcao_objetivo(self, num_bin, param_eq):
        """
            Calcula a função objetivo utilizada para avlaiar as soluções produzidas
        """
        # converte o número binário para o formato inteiro
        num = int(''.join(num_bin), 2)
        num_y = 0
        # calcula e retorna o resultado da função objetivo
        return param_eq[0]*num**2 + param_eq[1]*num_y**2 + param_eq[2]*num*num_y + param_eq[3]*num + param_eq[4]*num_y + param_eq[5]
    #@snoop
    def avaliar(self, param_eq):
        """
            Avalia as souluções produzidas, associando uma nota/avalição a cada elemento da população
        """
        self.avaliacao = []
        for individuo in self.populacao:
            self.avaliacao.append(self._funcao_objetivo(individuo, param_eq))
    #@snoop
    def selecionar(self):
        """
            Realiza a seleção do individuo mais apto por torneio, considerando N = 2
        """
        # agrupa os individuos com suas avaliações para gerar os participantes do torneio
        participantes_torneio = list(zip(self.populacao, self.avaliacao))
        # escolhe dois individuos aleatoriamente
        individuo_1 = participantes_torneio[randint(0, self.tam_populacao - 1)]
        individuo_2 = participantes_torneio[randint(0, self.tam_populacao - 1)]
        # retorna individuo com a maior avaliação, ou seja, o vencedor do torneio
        return individuo_1[0] if individuo_1[1] >= individuo_2[1] else individuo_2[0]
    #@snoop
    def _ajustar(self, individuo):
        """
            Caso o individuo esteja fora dos limites de x, ele é ajustado de acordo com o limite mais próximo
        """
        if int(''.join(individuo), 2) < self.x_min:
            # se o individuo é menor que o limite mínimo, ele é substituido pelo próprio limite mínimo
            ajuste = bin(self.x_min).replace('0b', '' if self.x_min < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                individuo[indice] = bit
        elif int(''.join(individuo), 2) > self.x_max:
            # se o individuo é maior que o limite máximo, ele é substituido pelo próprio limite máximo
            ajuste = bin(self.x_max).replace('0b', '' if self.x_max < 0 else '+').zfill(self.num_bits)
            for indice, bit in enumerate(ajuste):
                individuo[indice] = bit
    #@snoop
    def crossover(self, pai, mae):
        """
            Aplica o crossover de acordo com uma dada probabilidade (taxa de crossover)
        """
        if randint(1,100) <= self.taxa_crossover:
            # caso o crossover seja aplicado os pais trocam suas caldas e com isso geram dois filhos
            ponto_de_corte = randint(1, self.num_bits - 1)
            filho_1 = pai[:ponto_de_corte] + mae[ponto_de_corte:]
            filho_2 = mae[:ponto_de_corte] + pai[ponto_de_corte:]
            # se algum dos filhos estiver fora dos limites de x, ele é ajustado de acordo com o limite
            # mais próximo
            self._ajustar(filho_1)
            self._ajustar(filho_2)    
        else:
            # caso contrário os filhos são cópias exatas dos pais
            filho_1 = pai[:]
            filho_2 = mae[:]

        # retorna os filhos obtidos pelo crossover
        return (filho_1, filho_2)
    #@snoop
    def mutar(self, individuo):
        """
            Realiza a mutação dos bits de um indiviuo conforme uma dada probabilidade
            (taxa de mutação)
        """
 
        # cria a tabela com as regras de mutação
        tabela_mutacao = bytes.maketrans(b'+-01', b'-+10')
        
        # caso a taxa de mutação seja atingida, ela é realizada em um bit aleatório
        
        if randint(1,100) <= self.taxa_mutacao:
            bit = randint(0, self.num_bits - 1)
            individuo[bit] = individuo[bit].translate(tabela_mutacao)

        # se o individuo estiver fora dos limites de x, ele é ajustado de acordo com o
        # limite mais próximo
        self._ajustar(individuo)
    #@snoop
    def econtrar_filho_mais_apto(self):
        """
            Busca o individuo com a melhor avaliação dentro da população
        """
        # agrupa os individuos com suas avaliações para gerar os candidatos
        candidatos = list(zip(self.populacao, self.avaliacao))
        # retorna o candidato com a melhor avaliação, ou seja, o mais apto da população
        return max(candidatos, key=lambda elemento: elemento[1])
#@snoop
def main():
    # read file with the initial conditions
    file = open("../inputs/q1_ag.txt", "r")
    # input arguments
    input_args = file.read()
    
    # input data - dictionary
    dict_args = ast.literal_eval(input_args)
    
    #please, close the file :)
    file.close()
    
    param_eq = []
    constraint_eq = []
    
    idx = 0
    
    for arg in dict_args:
        if(idx < 6):
            param_eq.append(dict_args[arg])
            idx += 1
        else:
            constraint_eq.append(dict_args[arg])
            
    #print(param_eq)
    #print(constraint_eq)
    
    # cria uma instância do algoritmo genético com as configurações do enunciado
    algoritmo_genetico = AlgoritmoGenetico(constraint_eq[0], 
                                           constraint_eq[1], 
                                           constraint_eq[2],  
                                           constraint_eq[3],  
                                           constraint_eq[4], 
                                           constraint_eq[5],
                                           param_eq
                                          )
    # realiza a avaliação da população inicial
    algoritmo_genetico.avaliar(param_eq)
    # executa o algoritmo por "num_gerações"
    for i in range(algoritmo_genetico.num_geracoes):
        # imprime o resultado a cada geração, começando da população original
        print( 'Resultado {}: {}'.format(i, algoritmo_genetico.econtrar_filho_mais_apto()) )
        # cria uma nova população e a preenche enquanto não estiver completa
        nova_populacao = []
        while len(nova_populacao) < algoritmo_genetico.tam_populacao:
            # seleciona os pais
            pai = algoritmo_genetico.selecionar()
            mae = algoritmo_genetico.selecionar()
            # realiza o crossover dos pais para gerar os filhos
            filho_1, filho_2 = algoritmo_genetico.crossover(pai, mae)
            # realiza a mutação dos filhos e os adiciona à nova população
            algoritmo_genetico.mutar(filho_1)
            algoritmo_genetico.mutar(filho_2)
            nova_populacao.append(filho_1)
            nova_populacao.append(filho_2)
        # substitui a população antiga pela nova e realiza sua avaliação
        algoritmo_genetico.populacao = nova_populacao
        algoritmo_genetico.avaliar(param_eq)

    # procura o filho mais apto dentro da população e exibe o resultado do algoritmo genético
    print( 'Resultado {}: {}'.format(i+1, algoritmo_genetico.econtrar_filho_mais_apto()) )

    # encerra a execução da função main
    return 0

if __name__ == '__main__':
    main()