"""Servidor Flask para detectar círculos em tempo real pela câmera.

Execute: python camera_flask.py [índice_da_câmera]
Abra http://iprobo:5000 no navegador.
"""
import sys
import threading
import time

import cv2
from flask import Flask, Response, jsonify, render_template_string

import os


import simuladorMaze.maze.codigo_le_vitima.circulo_cores_simples as detector


app = Flask(__name__)
lock = threading.Lock()
estado = {
    "jpeg": None,
    "status": {"encontrado": False, "mensagem": "Iniciando câmera..."},
}

os.system("v4l2-ctl -d /dev/video_usb3 -c auto_exposure=1 -c exposure_time_absolute=1000 -c while_balance_automatic=0")


camera = cv2.VideoCapture("/dev/video_usb3")

camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def analisarBolinha():
    try:
        ok, frame = camera.read()
        if not ok:
            print("Falha ao capturar frame da câmera. Tentando novamente...")
            time.sleep(0.1)
            return

        imagem = cv2.resize(frame, (320, 240))
        status = None
        try:
            r = detector.analisar_alvo(imagem)
            nomes = r["cores"]            # externo -> interno, sempre 5 cores distintas
            kits = r["kits"]
            cx, cy = (int(v) for v in r["centro"])

            cv2.drawContours(imagem, [r["contorno"]], -1, (0, 255, 0), 3)
            cv2.circle(imagem, (cx, cy), 5, (0, 255, 0), -1)

            status = {
                "encontrado": True,
                "mensagem": "Circunferência encontrada!",
                "cores": nomes,
                "kits": kits,
                "hora": time.strftime("%H:%M:%S"),
            }
        except (ValueError, cv2.error):
            status = {
                "encontrado": False, 
                "mensagem": "Procurando circunferência..."
            }

        # Codifica e atualiza o estado SEMPRE, independentemente de encontrar o círculo
        ok_enc, buffer = cv2.imencode(".jpg", imagem)
        if ok_enc:
            with lock:
                estado["jpeg"] = buffer.tobytes()
                estado["status"] = status
                
    except Exception as e:
        print(f"Erro no processamento: {e}")


def rodarProcesso():
    while True:
        analisarBolinha()
        time.sleep(0.01)  # Pequena pausa para evitar sobrecarga da CPU


@app.route("/")
def index():
    return render_template_string("""
    <!doctype html><html lang="pt-br"><meta charset="utf-8">
    <title>Detector de circunferências</title>
    <style>body{font:16px Arial;background:#f3f4f6;text-align:center;margin:30px}
    img{max-width:95vw;max-height:75vh;border:2px solid #333}
    #status{font-size:1.5em;font-weight:bold}</style>
    <h1>Detector de circunferências</h1><div id="status">Conectando...</div>
    <p id="detalhes"></p><img src="/video_feed">
    <script>async function atualizar(){try{const r=await fetch('/status');const s=await r.json();
    const el=document.getElementById('status');el.textContent=s.mensagem;
    el.style.color=s.encontrado?'#12812e':'#555';
    document.getElementById('detalhes').textContent=s.encontrado?
    'Cores (externo → interno): '+s.cores.join(' → ')+' | Kits: '+s.kits+' | '+s.hora:'';
    }catch(e){}}setInterval(atualizar,500);atualizar();</script></html>
    """)


@app.route("/status")
def status():
    with lock:
        return jsonify(estado["status"])


@app.route("/video_feed")
def video_feed():
    def quadros():
        while True:
            with lock:
                jpeg = estado["jpeg"]
            if jpeg:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            time.sleep(0.01)
    return Response(quadros(), mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    indice_camera = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    threading.Thread(target=rodarProcesso, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
    # rodarProcesso()
