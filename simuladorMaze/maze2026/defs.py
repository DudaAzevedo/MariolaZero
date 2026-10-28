from libs.placaControleMotor import PlacaControleMotor
from libs.motores import Motores
from libs.giroscopio import Giroscopio
from libs.sensorCorReflexao import CorReflexao
from libs.portas import Portas
# from libs.teclado import Teclado
# from libs.tela import Tela
from libs.cronometro import Cronometro
# from libs.tcs34725 import TCS34725
from libs.vl53 import VL53L0X
from simuladorMaze.maze.libs.botoes import Botoes
from libs.pinosDigitais import PinosDigitais
import simuladorMaze.maze.constantes as const

crono_while = Cronometro()
crono_while.inicia()
relogio_temporario = Cronometro()
relogio_temporario.inicia()
relogio_processar_vitima_letra = Cronometro()
relogio_processar_vitima_letra.inicia()

# giro = Giroscopio(3)
portas = Portas()
portaSerialbarramento = portas.abre_porta_serial(Portas.SERIAL2, 250000, timeout=0.005)
sensor_de_linha= CorReflexao(Portas.SERIAL6)

def calibrarMotoresFrontais():
    # resultado = motores.obtem_calibracao_motores()
    # print(resultado)
    motor_esq_frente.calibracao_manual(32, -32)
    motor_dir_frente.calibracao_manual(32, -32)

motores = Motores(True)
motor_esq_frente = PlacaControleMotor(portaSerialbarramento, id_equipamento=5)
motor_dir_frente = PlacaControleMotor(portaSerialbarramento, id_equipamento=72)
motores.direcao_motor(1, Motores.INVERTIDO)
motor_esq_frente.direcao_motor(Motores.INVERTIDO)
motores.pid_motor(2,2,2)
motores.set_modo_freio(Motores.HOLD)
motor_esq_frente.set_freio(PlacaControleMotor.FREIO_TRAVADO)
motor_dir_frente.set_freio(PlacaControleMotor.FREIO_TRAVADO)
motor_esq_frente.set_kp_freio(3)
motor_esq_frente.set_kd_freio(10)
motor_dir_frente.set_kp_freio(3)
motor_dir_frente.set_kd_freio(10)
motor_esq_frente.set_delta_freio(20)
motor_dir_frente.set_delta_freio(20) 
motor_esq_frente.set_kp(2)
motor_esq_frente.set_kd(2)
motor_esq_frente.set_ki(2)
motor_dir_frente.set_kp(2)
motor_dir_frente.set_kd(2)
motor_dir_frente.set_ki(2)
calibrarMotoresFrontais()


def rgb_dir():
      return sensor_de_linha.le_rgbc(1)

def rgb_meio():
      return sensor_de_linha.le_rgbc(2)

def rgb_esq():
      return sensor_de_linha.le_rgbc(3)
      


def hsv_esq():
      return sensor_de_linha.le_hsv120(1)

def hsv_meio():
      return sensor_de_linha.le_hsv120(2)

def hsv_dir():
      return sensor_de_linha.le_hsv120(3)


# Sensor de linha 
def esquerdo_exeterno():
    return sensor_de_linha.le_reflexao()[3]

def esquerdo_interno():
    return sensor_de_linha.le_reflexao()[2]

def direito_interno():
    return sensor_de_linha.le_reflexao()[1]

def direito_externo():
    return sensor_de_linha.le_reflexao()[0]


# sensor_distancia_frente = VL53L0X(Portas.I2C1)
sensor_distancia_meio_esq = VL53L0X(Portas.I2C3)
sensor_distancia_meio_dir = VL53L0X(Portas.I2C6)
# sensor_distancia_borda_esq = VL53L0X(Portas.I2C2)
sensor_distancia_borda_dir = VL53L0X(Portas.I2C7)
# sensor_distancia_tras = VL53L0X(Portas.I2C4)

botoes = Botoes()

g = Giroscopio(Portas.SERIAL4)