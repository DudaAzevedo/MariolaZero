import simuladorMaze.maze.movimentos as mov
from simuladorMaze.maze.codigo_le_vitima.identificar_simbolos import procurar_diferente_de_branco, processar_vitima_letra
import simuladorMaze.maze.defs as defs
import simuladorMaze.maze.constantes as c
from time import sleep
import simuladorMaze.maze.threads.parachoque as choque
import simuladorMaze.maze.threads.sensores_I2C as i2c
# from codigo_le_vitima.camera_flask import analisarBolinha

contadorWhile = 0
quantOmega=0
quantPsi=0
quantPhi=0

def inicia_threads():
    i2c.iniciar_thread_sensores_I2C()
    choque.iniciar_thread_parachoque()

def procuraLetra():
    global quantOmega,quantPsi,quantPhi
    # if procurar_diferente_de_branco():
    #     print("achou algo na parede")
    #     para_motores()
    defs.relogio_processar_vitima_letra.reseta()
    letra = processar_vitima_letra(lambda:defs.relogio_processar_vitima_letra.tempo(), c.tempo_verificando_letra)
    return letra
    # else:
    #     return None

def o_que_fazer_se_ver_vitima(letra):
    if letra is not None:
        print("achou vítima", letra)
        mov.acende_todos_LEDs()
        mov.para_motores()
        mov.andar_distancia_velocidade(10,40)
        mov.apaga_todos_LEDs()
    else:
        print("não achou vítima")
        mov.andar_distancia_velocidade(5,40)

try:   
    inicia_threads()
    while True:
        # mov.potencia_4x4(25,-25)
        # mov.alinhar_parede_potencia(lambda:i2c.distancia_borda_esq,lambda:i2c.distancia_meio_esq,lambda:i2c.distancia_borda_dir,lambda:i2c.distancia_meio_dir)
        # mov.andar_alinhando_parede_por_distancia(lambda:i2c.distancia_borda_esq,lambda:i2c.distancia_meio_esq,lambda:i2c.distancia_borda_dir,lambda:i2c.distancia_meio_dir, 15)
        # mov.alinhar_parachoque(lambda:choque.parachoque_esquerdo,lambda:choque.parachoque_direito)
        # mov.girar_angulo_giroscopio_potencia(lambda:defs.g.le_angulo_z(),87,c.POTENCIA_MEDIA)
        mov.andar_ate_condicao_ou_distancia(lambda:choque.qualquer_parachoque_pressionado,c.POTENCIA_MEDIA,c.DIRECAO_FRENTE,12)
        # mov.alinhar_parachoque(lambda:choque.parachoque_esquerdo,lambda:choque.parachoque_direito)
        # mov.andar_distancia_velocidade(-10,c.VELOCIDADE_NORMAL)
        # mov.girar_angulo_giroscopio_potencia(lambda:defs.g.le_angulo_z(),-87,c.POTENCIA_MEDIA)
        input("Pressione Enter para continuar...")# ELE ANDOU 45.7CM COM 1000 GRAUS
        # procuraLetra()
        # tremdeBolinha = analisarBolinha()
        # print("trem de bolinha",tremdeBolinha)
        # relogioTemporario.reseta()
        # mov.andar_alinhando_parede(i2c.distancia_borda_esq,i2c.distancia_meio_esq, i2c.distancia_borda_dir, i2c.distancia_meio_dir)
        # letra = procurarVitimaLetra(relogioTemporario)
        # print("contador While",c.contador_while)
        quantPhi = 0
        quantOmega = 0
        quantPsi = 0
        c.contador_while+=1
        if defs.crono_while.tempo() >= 10:
            c.contador_while=0
            defs.crono_while.reseta()

#Essa parte do código é responsável por lidar com a interrupção do programa quando no terminal apertamos Ctrl+C 
#ou interrompemos o programa pelo teclado do brick
except KeyboardInterrupt as e:
    print("\nInterrupção detectada! Encerrando...")
finally:
    # Primeiro solicita o encerramento das threads.
    i2c.evento_encerramento.set()
    # Depois para os motores.
    mov.para_motores()
    # Aguarda a thread realmente terminar.
    i2c.threadI2C.join(timeout=1.0)
    choque.thread_parachoque.join(timeout=1.0)
    if i2c.threadI2C.is_alive():
        print("Aviso: a thread I2C não encerrou dentro do prazo.")
    if choque.thread_parachoque.is_alive():
        print("Aviso: deu ruim a thread")
    print("Programa encerrado com segurança.")