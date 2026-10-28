import time
import threading
from simuladorMaze.maze.threads.sensores_I2C import evento_encerramento
from simuladorMaze.maze.defs import botoes 

parachoque_esquerdo = None
parachoque_direito = None

def lerValoresBotoes():
    global parachoque_esquerdo
    global parachoque_direito
    while not evento_encerramento.is_set():
        parachoque_esquerdo = botoes.botao_pressionado(botoes.P1)
        parachoque_direito = botoes.botao_pressionado(botoes.P8)
        time.sleep(0.02)

def qualquer_parachoque_pressionado():
    global parachoque_esquerdo
    global parachoque_direito
    if parachoque_esquerdo is True or parachoque_direito is True:
        return True
    return False
        
thread_parachoque = None

def iniciar_thread_parachoque():
    global thread_parachoque
    thread_parachoque = threading.Thread(target=lerValoresBotoes,name="Parachoque",daemon=False)
    thread_parachoque.start()
    return thread_parachoque

