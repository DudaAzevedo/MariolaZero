# import defs
import simuladorMaze.maze.constantes as const
# import camera
from simuladorMaze.maze.threads import sensores_I2C as I2C
from simuladorMaze.maze.threads import cores 
import networkx as nx


class Ladrilho():

    COR_LADRILHO_DESCONHECIDO = 0
    COR_LADRILHO_AZUL= 1
    COR_LADRILHO_CINZA = 2
    COR_LADRILHO_PRETO = 3
    COR_LADRILHO_BRANCO = 4
    COR_LADRILHO_VERMELHO = 5
   

    TIPO_PAREDE_COM_VITIMA = 1
    TIPO_PAREDE_VAZIA = 2
    TIPO_PAREDE_PREENCHIDA = 3
    TIPO_PAREDE_DESCONHECIDA = 4

    visitado = False
    cor_chao = COR_LADRILHO_DESCONHECIDO
    paredes = [TIPO_PAREDE_DESCONHECIDA,TIPO_PAREDE_DESCONHECIDA,TIPO_PAREDE_DESCONHECIDA,TIPO_PAREDE_DESCONHECIDA]    


class Mapa:

    ################   grafo
    mapa = [[Ladrilho() for _ in range(50)] for _ in range(50)]    
    grafo = None
    ALTURA_MAPA =50
    LARGURA_MAPA = 50

    ############# CONHECIMENTOS
    CONHECIMENTO_INVALIDO = {'peso': 2, 'cor': 'gray'}
    CONHECIMENTO_CONHECIDO = {'peso': 1, 'cor': 'pink'}
    CONHECIMENTO_DESCONHECIDO = {'peso': 0, 'cor': 'gray'}

    def ha_conhecimento_desconhecido(self):
        if grafo is None:
            return False
        return any(dados['conhecimento'] == self.CONHECIMENTO_DESCONHECIDO for _, _, dados in grafo.edges.data())


    def marcar_aresta_ladrilho_invalido(self, no1, no2):
        if grafo is None or not grafo.has_edge(no1, no2):
            return False

        grafo.edges[no1, no2]['conhecimento'] = self.CONHECIMENTO_INVALIDO
        return True

    def criar_grafo(self):
        global grafo

        grafo = nx.grid_2d_graph(self.ALTURA_MAPA, self.LARGURA_MAPA)
        for aresta in grafo.edges:
            grafo.edges[aresta]['conhecimento'] = self.CONHECIMENTO_DESCONHECIDO


        return grafo

    def dijkstra_multiplos_destinos(self, origem, destinos):
        """Caminho mais curto da origem até qualquer um dos nós em `destinos`, ou None se nenhum for alcançável."""
        try:
            _, caminho = nx.multi_source_dijkstra(
                self.grafo,
                sources=destinos,
                target=origem,
                weight=lambda u, v, aresta: aresta['conhecimento']['peso'],
            )
        except nx.NetworkXNoPath:
            return None

        caminho.reverse()  # a lib devolve do destino até a origem
        return caminho


    def nos_com_arestas_desconhecidas(self):
        """Nós com arestas não exploradas, ordenados do menor pro maior número de vizinhos desconhecidos."""
        nos_desconhecidos = set()
        for u, v, conhecimento in self.grafo.edges.data('conhecimento'):
            if conhecimento == self.CONHECIMENTO_DESCONHECIDA:
                nos_desconhecidos.add(u)
                nos_desconhecidos.add(v)
        nos_desconhecidos = list(nos_desconhecidos)

        def contar_vizinhos_desconhecidos(self, no):
            vizinhos_desconhecidos = set()
            for vizinho in self.grafo.neighbors(no):
                if self.grafo.edges[no, vizinho]['conhecimento'] == self.CONHECIMENTO_DESCONHECIDA:
                    vizinhos_desconhecidos.add(vizinho)

                diferenca = (vizinho[0] - no[0], vizinho[1] - no[1])
                vizinho_vizinho = (vizinho[0] + diferenca[0], vizinho[1] + diferenca[1])

                if (
                    self.grafo.has_edge(vizinho, vizinho_vizinho)
                    and self.grafo.edges[vizinho, vizinho_vizinho]['conhecimento'] == self.CONHECIMENTO_DESCONHECIDA
                ):
                    vizinhos_desconhecidos.add(vizinho_vizinho)

            return len(vizinhos_desconhecidos)

        nos_desconhecidos.sort(key=contar_vizinhos_desconhecidos, reverse=True)
        return nos_desconhecidos



    
    NORTE = 0
    LESTE = 1
    SUL = 2
    OESTE = 3

    TAMANHO_MATRIZ = 50
    INICIO_MATRIZ = TAMANHO_MATRIZ/2

    esquerda = 0
    direita = 1
    frente = 2
    tras = 3
    direcao_atual = NORTE
    posicao_y_atual = TAMANHO_MATRIZ/2
    posicao_x_atual = TAMANHO_MATRIZ/2


    
    def cordenada_proximo_ladrilho( self, direcao):
        """Pega e retorna a cordenada"""

        if direcao == self.NORTE:
            return self.posicao_x_atual ,self.posicao_y_atual+1

        if direcao == self.LESTE:
            return self.posicao_x_atual+1,self.posicao_y_atual

        if direcao == self.SUL:
            return self.posicao_x_atual,self.posicao_y_atual-1

        if direcao == self.OESTE:
            return self.posicao_x_atual-1,self.posicao_y_atual


    # def registrar_ladrilho(self):
    #     i= self.posicao_x_atual
    #     j=self.posicao_y_atual
    #     const.mapa[i][j] = self.analisar_ladrilho()
    #     self.ladrilho_visitado = True

#     #### analisa todas as informaçoes reunidas e define a rota
#     def rota(self):
#         self.analisar_ladrilho()
#         self.registrar_ladrilho()
#         self.proximo_ladrilho()

#         return
    
    def analisar_ladrilho(self):
        self.analisar_parede()
        self.analisar_chao()

        return self.analisar_parede(),self.analisar_chao()

    def analisar_parede(self):

        self.encontrar_direcao_atual()

        i= int(self.posicao_x_atual)
        j= int(self.posicao_y_atual)

        if I2C.distancia_frente >= const.DISTANCIA_SEM_PAREDE : 
            self.mapa[i][j].paredes[self.frente] = Ladrilho.TIPO_PAREDE_VAZIA
        else:
            self.mapa[i][j].paredes[self.frente] = Ladrilho.TIPO_PAREDE_PREENCHIDA
            

        if I2C.distancia_meio_esq >= const.DISTANCIA_SEM_PAREDE :
            self.mapa[i][j].paredes[self.esquerda] = Ladrilho.TIPO_PAREDE_VAZIA
        else:
            self.mapa[i][j].paredes[self.esquerda] = Ladrilho.TIPO_PAREDE_PREENCHIDA

        if I2C.distancia_meio_dir >= const.DISTANCIA_SEM_PAREDE :
            self.mapa[i][j].paredes[self.direita] = Ladrilho.TIPO_PAREDE_VAZIA
        else:
            self.mapa[i][j].paredes[self.direita] = Ladrilho.TIPO_PAREDE_PREENCHIDA

        if I2C.distancia_tras >= const.DISTANCIA_SEM_PAREDE :
            self.mapa[i][j].paredes[self.tras] = Ladrilho.TIPO_PAREDE_VAZIA
        else:
            self.mapa[i][j].paredes[self.tras] = Ladrilho.TIPO_PAREDE_PREENCHIDA
        
        return Ladrilho.paredes

    def analisar_chao(self):
            # return cores.hsv_vendo_cor
            return cores.DefinicaoCores.cor()


    def encontrar_direcao_atual(self):

        if (self.direcao_atual == self.NORTE):
            self.direita= self.LESTE
            self.esquerda= self.OESTE
            self.tras= self.SUL
            self.frente= self.NORTE

            return self.NORTE
        
        if (self.direcao_atual == self.LESTE):
            self.direita=self.SUL
            self.esquerda= self.NORTE
            self.tras=self.OESTE
            self.frente= self.LESTE

            return self.LESTE
        
        if (self.direcao_atual == self.SUL):
            self.direita= self.OESTE
            self.esquerda= self.LESTE
            self.tras=self.NORTE
            self.frente=self.SUL

            return self.SUL
        
        if (self.direcao_atual == self.OESTE):
            self.direita=self.NORTE
            self.esquerda= self.SUL
            self.tras=self.LESTE
            self.frente=self.OESTE

            return self.OESTE

#     #### analisa e define todas as informações do ladrilho atual


    def proximo_ladrilho(self):

        if  Ladrilho.paredes[self.direita] == Ladrilho.TIPO_PAREDE_PREENCHIDA  or Ladrilho.visitado == False:
            # virar 90 graus para a direita e seguir
            # print("vou virar pra direita")
            return "DIREITA"

        elif Ladrilho.paredes[self.frente] == Ladrilho.TIPO_PAREDE_PREENCHIDA  or Ladrilho.visitado == False:
            # seguir reto
            return "FRENTE"

        elif Ladrilho.paredes[self.esquerda] == Ladrilho.TIPO_PAREDE_PREENCHIDA  or Ladrilho.visitado == False:
            # virar 90 graus para a esquerda e seguir
            return "ESQUERDA"

        else:
            # virar 180 graus e voltar
            return "VOLTAR"