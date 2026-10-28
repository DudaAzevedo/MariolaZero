
from simuladorMaze.maze.estrategias import mapa
from simuladorMaze.maze.estrategias import tomar_decisoes
from simuladorMaze.maze.threads import cores
from simuladorMaze.maze.threads import sensores_I2C
# robo.giro.reseta_z()    
import simuladorMaze.maze.constantes as const
import simuladorMaze.maze.defs as defs
import time

sensores_I2C.iniciar_thread_sensores_I2C()
cores.iniciar_thread_atualizacao_cores_e_hsv()

# mapa.criar_grafo()
# if const.DEBUG:
#     servico_web.iniciar()

print("Iniciando loop principal")
while True:
    pista=mapa.Mapa()
    tomar_decisoes.navegacao.navegacao(self=pista)
    # print(defs.rgb_meio())
    # print(cores.DefinicaoCores.cor())
    # print(pista.analisar_parede())
    # defs.sensor_distancia_meio_dir.solicita_leitura
    # print("Esquerda frente:", defs.sensor_distancia_meio_dir.leitura_mm())
    # time.sleep(0.2)
    # input("input")
