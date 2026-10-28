import threading
import cv2
import time
import os

frame_atual = None
frame_transmissao = None

camera = cv2.VideoCapture("/dev/video_usb3")
os.system("v4l2-ctl -d /dev/video_usb3 -c auto_exposure=1 -c exposure_time_absolute=300 -c while_balance_automatic=0")
# camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
frame_lock = threading.Lock()

def pegar_frame():
    global frame_atual
    while True:
        ok, frame_invertido = camera.read()
        if not ok:
            print("Falha ao capturar frame da câmera. Tentando novamente...")
            time.sleep(0.1)
            continue
        frame_atual = cv2.flip(frame_invertido, 0)
        time.sleep(0.03)

pegarFrame_thread = threading.Thread(target=pegar_frame)
pegarFrame_thread.daemon = True
pegarFrame_thread.start()