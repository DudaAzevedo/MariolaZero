from libs.vl53 import VL53L0X
import simuladorMaze.maze.defs as defs 
import threading
from time import sleep

evento_encerramento = threading.Event()

distancia_tras = 8000 
distancia_frente= 8000
distancia_meio_esq = 8000
distancia_meio_dir = 8000
distancia_borda_esq = 8000
distancia_borda_dir = 8000

def thread_I2C(): 
    global distancia_tras,distancia_frente, distancia_meio_esq, distancia_meio_dir, distancia_borda_esq, distancia_borda_dir
    while not evento_encerramento.is_set():
        # defs.sensor_distancia_tras.solicita_leitura()
        # defs.sensor_distancia_frente.solicita_leitura()
        defs.sensor_distancia_meio_esq.solicita_leitura()
        defs.sensor_distancia_meio_dir.solicita_leitura()
        # defs.sensor_distancia_borda_esq.solicita_leitura()
        defs.sensor_distancia_borda_dir.solicita_leitura()

        # distancia_tras = defs.sensor_distancia_tras.leitura_mm()
        # distancia_frente = defs.sensor_distancia_frente.leitura_mm()
        distancia_meio_esq = defs.sensor_distancia_meio_esq.leitura_mm()
        distancia_meio_dir = defs.sensor_distancia_meio_dir.leitura_mm()
        # distancia_borda_esq = defs.sensor_distancia_borda_esq.leitura_mm()
        distancia_borda_dir = defs.sensor_distancia_borda_dir.leitura_mm()

        # print(f"Distancia frontal: {distancia_frontal} mm, Distancia lateral esquerda: {distancia_lateral_esquerda} mm, Distancia lateral direita: {distancia_lateral_direita} mm")
        
thread12C = None

def iniciar_thread_sensores_I2C():
    global threadI2C
    threadI2C = threading.Thread(target=thread_I2C,name="Sensores-I2C",daemon=False)
    threadI2C.start()
    return threadI2C