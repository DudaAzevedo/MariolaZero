from simuladorMaze.maze.estrategias import mapa
import simuladorMaze.maze.movimentos as mov

mapa= mapa.Mapa
class navegacao:
    # def graus_para_no_vizinho(self,no_vizinho):
    #     direcao_alvo = calcular_direcao(pos_atual, no_vizinho)
    #     quantidade_giros = (direcao_alvo - mapa.direcao_robo + 2) % 4 - 2
    #     print(f'Posição: {pos_atual} | anterior: {pos_anterior} | 'f'alvo: {no_vizinho} | direção atual: {mapa.direcao_robo} | 'f'direção alvo: {direcao_alvo} | giro: {quantidade_giros * 90} graus')
    #     return quantidade_giros * 90

    # def rotacionar_para_no(self,no_alvo, velocidade=config.VEL_BASE):
    #     graus = self.graus_para_no_vizinho(no_alvo)

    #     if graus == 0:
    #         return False

    #     if graus == -90:
    #         return True

    #     if graus == -180:
    #         rotacionar_para_direcao(mapa.esquerda, config.VEL_GIRO_CIDADE)
    #         return True

    #     rotacionar_para_direcao(calcular_direcao(pos_atual, no_alvo), config.VEL_GIRO_CIDADE)
    #     return False

    # def ir_para_coordenada(self, destino):
    #     if not self.grafo.has_node(destino):
    #         print(f'Coordenada inválida: {destino}')
    #         return False


    #     caminho = self.dijkstra_multiplos_destinos(self.pos_atual, {destino})

    #     if not caminho:
    #         print(f'Não existe caminho até {destino}')
    #         return False

    #     while len(caminho) > 1:
    #         proximo = caminho[1]
    #         movimento = self.rotacionar_para_no(proximo)
    #         self.seguir_ate_proxima_encruzilhada(lateralmente=movimento)
    #         caminho = self.dijkstra_multiplos_destinos(self.pos_atual, {destino})

    #     return True
    def navegacao(self):
        if mapa.Mapa.proximo_ladrilho() == "DIREITA":
            mov.virar_angulo_potencia(90,50)
        elif mapa.Mapa.proximo_ladrilho() == "FRENTE":
            mov.andar_distancia_velocidade(300,50)
        elif mapa.Mapa.proximo_ladrilho() == "ESQUERDA":
            mov.virar_angulo_potencia(-90,50)
