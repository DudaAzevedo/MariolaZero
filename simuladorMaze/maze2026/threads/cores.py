from simuladorMaze.maze.defs import sensor_de_linha,esquerdo_exeterno,esquerdo_interno,direito_interno,direito_externo,rgb_meio, rgb_esq,rgb_dir
from time import sleep
import simuladorMaze.maze.constantes as const
import threading
from simuladorMaze.maze.estrategias import mapa
rgb_sensor_de_linha = [None,None, None]
rgb_vendo_cor = [None, None, None]
sensor_reflexivo = [None,None,None,None]
reflexivo_vendo_preto = [None,None,None,None]
threadsencor = None



def iniciar_thread_atualizacao_cores_e_hsv():
    global threadsencor
    threadsencor = threading.Thread(target=thread_atualizacao_cores_e_hsv)
    threadsencor.daemon = True
    threadsencor.start()



def thread_atualizacao_cores_e_hsv():
    global sensor_reflexivo, rgb #rgb_sensor_de_linha, rgb_vendo_cor,reflexivo_vendo_preto

    while True:
        sensor_reflexivo = (esquerdo_exeterno(),esquerdo_interno(),direito_interno(), direito_externo())
        rgb = rgb_esq(), rgb_meio(), rgb_dir()

        # reflexivo_vendo_preto = all(valor < 20 for valor in sensor_reflexivo)
        #Atualiza os valores do sensor
        # rgb_sensor_de_linha = [sensor_de_linha.le_rgb(indice_sensor) for indice_sensor in (1, 2, 3)] 

        #define a cor atual sendo lida com os valores atualizados do sensor
        # rgb_vendo_cor = [DefinicaoCores.cor(tuple(rgb)) for rgb in rgb_sensor_de_linha]
        sleep(0.02)

class DefinicaoCores:

    def e_vermelho():
        r = rgb_meio()[0]
        g = rgb_meio()[1]
        b = rgb_meio()[2]
         
        return 100 <= r <= 125 and 15 <= g <= 35 and 15 <= b <= 35
  
    def e_azul():
        r = rgb_meio()[0]
        g = rgb_meio()[1]
        b = rgb_meio()[2]
        return 10 <= r <= 30 and 35 <= g <= 60 and 100 <= b <= 127


    def e_cinza():
        r = rgb_meio()[0]
        g = rgb_meio()[1]
        b = rgb_meio()[2]
        return 180 <= r <= 200 and 185 <= g <= 210 and 90 <= b <= 210

    
    def e_preto():
        r = rgb_meio()[0]
        g = rgb_meio()[1]
        b = rgb_meio()[2]
        return r <= 15 and g <= 15 and b <= 15

 
    def e_branco():
        r = rgb_meio()[0]
        g = rgb_meio()[1]
        b = rgb_meio()[2]
        return 100 <= r <= 140 and 100 <= g <= 140 and 100 <= b <= 140


    def cor():
        if DefinicaoCores.e_vermelho():
            mapa.Ladrilho.cor_chao==mapa.Ladrilho.COR_LADRILHO_VERMELHO
            return mapa.Ladrilho.COR_LADRILHO_VERMELHO
        if DefinicaoCores.e_azul():
            mapa.Ladrilho.cor_chao==mapa.Ladrilho.COR_LADRILHO_AZUL
            return mapa.Ladrilho.COR_LADRILHO_AZUL
        if DefinicaoCores.e_cinza():
            mapa.Ladrilho.cor_chao==mapa.Ladrilho.COR_LADRILHO_CINZA
            return mapa.Ladrilho.COR_LADRILHO_CINZA
        if DefinicaoCores.e_preto():
            mapa.Ladrilho.cor_chao==mapa.Ladrilho.COR_LADRILHO_PRETO
            return mapa.Ladrilho.COR_LADRILHO_PRETO
        if DefinicaoCores.e_branco():
            mapa.Ladrilho.cor_chao==mapa.Ladrilho.COR_LADRILHO_BRANCO
            return mapa.Ladrilho.COR_LADRILHO_BRANCO
        return None