from simuladorMaze.maze.defs import motores,motor_esq_frente,motor_dir_frente
import threading
import simuladorMaze.maze.constantes as c
from time import sleep
# import estrategias 

conversaoGrauParaCm = 45.7
def centimetros_para_graus(cm):
    return (cm * 1000) / 45.7

def acende_todos_LEDs():
    motores.set_led_rgb_all(220,20,209)

def apaga_todos_LEDs():
    motores.set_led_rgb_all(0,0,0)

def velocidade_4x4(velo_esq=c.VELOCIDADE_NORMAL,velo_dir=c.VELOCIDADE_NORMAL):
    motores.velocidade_motores_4x4(velo_esq,velo_dir)
    motor_esq_frente.velocidade_motor(velo_esq)
    motor_dir_frente.velocidade_motor(velo_dir)


def potencia_4x4(potencia_esq=c.POTENCIA_MEDIA,potencia_dir=c.POTENCIA_MEDIA):
    t = threading.Thread(target=motores.potencia_motores, args=(potencia_esq, potencia_dir))
    t.start()
    resultado = motor_dir_frente.potencia_motor(potencia_esq)
    t.join()
    resultado = motor_esq_frente.potencia_motor(potencia_dir)

def para_motores():
    motores.set_modo_freio(1)
    motores.para_motores()
    motor_esq_frente.para_motor()
    motor_dir_frente.para_motor()

def andar_distancia_velocidade(distanciaEmCm, velocidade):
    if distanciaEmCm > 0:
        direcao = 1
    else:
        direcao = -1
    # distanciaCovertida = distanciaEmCm * conversaoGrauParaCm
    distanciaCovertida = centimetros_para_graus(distanciaEmCm)
    motores.reseta_angulo_motor(1)
    while abs(motores.angulo_motor(1)) < distanciaCovertida:
        # print("andeDistanciaVelocidade",abs(motores.angulo_motor(1)))
        motores.velocidade_motores_4x4(velocidade * direcao, velocidade * direcao)
    para_motores()

def girar_potencia(potencia,direcao):
    potencia_4x4(potencia*direcao,-potencia*direcao)

def girar_angulo_giroscopio_potencia(giro,angulo,potencia=c.POTENCIA_DEVAGAR,parar=lambda:None):
    if angulo > 0:
        direcao = c.DIRECAO_DIREITA
    else:
        direcao = c.DIRECAO_ESQUERDA
    posicaoInicial = giro()
    giro_atual = giro()
    while abs(giro_atual - posicaoInicial) < angulo:
        giro_atual = giro()
        girar_potencia(potencia,direcao)
        if not parar() is None:
            para_motores()
            return
    para_motores()

def alinhar_parachoque(sensor_esquerdo, sensor_direito, velocidade=c.POTENCIA_MEDIA):
    print("sensores",sensor_esquerdo(),sensor_direito())
    while not sensor_esquerdo() or not sensor_direito():
        if sensor_esquerdo() and not sensor_direito():
            # print("sensor_esquerdo() and not sensor_direito()")
            motores.potencia_motores_4x4(-velocidade, velocidade)
        elif not sensor_esquerdo() and sensor_direito():
            # print("not sensor_esquerdo() and sensor_direito()")
            motores.potencia_motores_4x4(velocidade, -velocidade)
    para_motores()


def andar_ate_condicao_ou_distancia(condicao,potencia,direcao,distancia=10):
    variavelCmPraGrau=5.7*distancia*direcao
    velo=potencia*direcao
    distanciaConvertida = centimetros_para_graus(distancia)
    while motores.angulo_motor(2) <= distanciaConvertida:
        flag = condicao()
        if flag:
            print("andar_ate_condicao_ou_distancia flag")
            break
        # print(anguloInicial,(anguloInicial+variavelCmPraGrau))
        velocidade_4x4(velo)
    motores.para_motores()


def virar_angulo_velocidade_suave(giroscopio, angulo, direcao=c.DIRECAO_FRENTE):
    """essa direcao é para frente ou para tras"""
    giroInicial=giroscopio()
    giroAtual=giroscopio()
    while abs(giroAtual - giroInicial) < abs(angulo):
        if (giroAtual - giroInicial) < (angulo):
            giroAtual=giroscopio()
            motores.velocidade_motores_4x4(c.VELOCIDADE_DEVAGAR * direcao, c.VELOCIDADE_NORMAL * direcao)
        if (giroAtual - giroInicial) > (angulo):
            giroAtual=giroscopio()
            motores.velocidade_motores_4x4(c.VELOCIDADE_NORMAL * direcao, c.VELOCIDADE_DEVAGAR * direcao)
    para_motores()

def se_aproximar_ate_distancia_parede(sensor_distancia,giroscopio, distancia, direcao):
    """anda ate se aproximar de uma parede, com os sensores de distancia, sai da função se acahar algo."""
    velocidade = c.VELOCIDADE_NORMAL
    delta = 10
    while sensor_distancia() > distancia:
        virar_angulo_velocidade(giroscopio, 15, velocidade)
        virar_angulo_velocidade_suave(giroscopio, -15, velocidade)
        andar_distancia_velocidade(1, velocidade)
    para_motores()

def alinhar_parede_potencia(borda_esquerda,meio_esquerda,borda_direita,meio_direita):
    potencia = c.POTENCIA_MEDIA
    distancia_da_parede = 97
    meio_dir = meio_direita()
    borda_dir = borda_direita() - 37
    diferenca = meio_dir - borda_dir
    while abs(diferenca) > 1:
        # Executa as lambdas e obtém os valores atuais
        meio_esq = meio_esquerda()
        borda_esq = borda_esquerda()
        meio_dir = meio_direita()
        borda_dir = borda_direita() - 37
        distancia_media_dir = (meio_dir + borda_dir) / 2
        diferenca = meio_dir - borda_dir
        if diferenca >= 0 :#vira para direita
            potencia_esq = potencia
            potencia_dir = -potencia 
        else:#vira para esquerda
            potencia_esq = -potencia
            potencia_dir = potencia
        # print(f'POTENCIA_ESQUERDA: {potencia_esq} AND POTENCIA_DIREITA: {potencia_dir}')
        motores.potencia_motores_4x4(potencia_esq, potencia_dir)
    print("diferenca",diferenca)
    para_motores()

def andar_alinhando_parede(borda_esquerda,meio_esquerda,borda_direita,meio_direita):
    """anda seguindo a(s) parede(s) com os sensores de distancia, sai da função se acahar algo."""
    velocidade = c.VELOCIDADE_NORMAL
    meio_dir = meio_direita
    meio_esq = meio_esquerda
    borda_dir = borda_direita - 37
    borda_esq = borda_esquerda
    distancia_media_dir = (meio_dir + borda_dir) / 2
    distancia_da_parede = 97
    if meio_dir <= c.DISTANCIA_SEM_PAREDE:
        print("meio_dir borda_dir",meio_dir,borda_dir)
        diferenca = meio_dir - borda_dir
        correcao = int(abs(diferenca*5))
        if diferenca >= 0 or distancia_media_dir > distancia_da_parede: #vira para direita
            # print("virando para direita",velocidade,velocidade-correcao)
            velo_esq=velocidade
            velo_dir=velocidade-correcao
        if diferenca < 0 or distancia_media_dir < distancia_da_parede: #vira para esquerda
            # print("virando para esquerda",velocidade-correcao, velocidade)
            velo_esq=velocidade-correcao
            velo_dir=velocidade
        # print(meio_dir,borda_dir,diferenca)
        motores.velocidade_motores_4x4(velo_esq,velo_dir)

def andar_alinhando_parede_por_distancia(borda_esquerda,meio_esquerda,borda_direita,meio_direita,distancia):
    potencia = c.POTENCIA_DEVAGAR
    distancia_da_parede = 97
    distanciaConvertida = centimetros_para_graus(distancia)
    motores.reseta_angulo_motor(1)
    motores.reseta_angulo_motor(2)
    media_motores = (motores.angulo_motor(1) + motores.angulo_motor(2)) / 2

    while media_motores <= distanciaConvertida:
        # Executa as lambdas e obtém os valores atuais
        meio_esq = meio_esquerda()
        borda_esq = borda_esquerda()
        meio_dir = meio_direita()
        borda_dir = borda_direita() - 37
        distancia_media_dir = (meio_dir + borda_dir) / 2
        diferenca = meio_dir - borda_dir
        margem_de_erro = 10
        media_motores = (motores.angulo_motor(1) + motores.angulo_motor(2)) / 2
        print("diferenca",diferenca)
        if meio_dir <= c.DISTANCIA_SEM_PAREDE and borda_dir <= c.DISTANCIA_SEM_PAREDE:
            correcao = int(abs(diferenca * 2.97))
            if diferenca >= 0 :#vira para direita
                potencia_esq = potencia
                potencia_dir = potencia - correcao
            elif diferenca < 0:#vira para esquerda
                potencia_esq = potencia - correcao
                potencia_dir = potencia
            potencia_4x4(int(potencia_esq),int(potencia_dir))
    para_motores()
