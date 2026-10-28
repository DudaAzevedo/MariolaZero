import sys
import threading
import time
import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template_string, request

app = Flask(__name__)
lock = threading.Lock()

# Valores iniciais dos sliders HSV
config_hsv = {
    "h_min": 0, "h_max": 179,
    "s_min": 0, "s_max": 255,
    "v_min": 0, "v_max": 255
}

estado = {
    "jpeg": None
}

camera = cv2.VideoCapture("/dev/video_usb3")
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

def processarCalibracao():
    while True:
        try:
            ok, frame = camera.read()
            if not ok:
                time.sleep(0.1)
                continue

            frame = cv2.resize(frame, (640, 480))
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Pega os valores atuais configurados no navegador
            with lock:
                h_min = config_hsv["h_min"]
                h_max = config_hsv["h_max"]
                s_min = config_hsv["s_min"]
                s_max = config_hsv["s_max"]
                v_min = config_hsv["v_min"]
                v_max = config_hsv["v_max"]

            lower = np.array([h_min, s_min, v_min])
            upper = np.array([h_max, s_max, v_max])

            # Cria a máscara e aplica ao frame
            mask = cv2.inRange(hsv, lower, upper)
            resultado = cv2.bitwise_and(frame, frame, mask=mask)

            ok_enc, buffer = cv2.imencode(".jpg", resultado)
            if ok_enc:
                with lock:
                    estado["jpeg"] = buffer.tobytes()
        except Exception as e:
            print(f"Erro: {e}")
            
        time.sleep(0.01)

@app.route("/")
def index():
    return render_template_string("""
    <!doctype html><html lang="pt-br"><meta charset="utf-8">
    <title>Calibrador HSV Flask</title>
    <style>
        body{font:16px Arial;background:#f3f4f6;text-align:center;margin:20px}
        .controls{display:inline-block;text-align:left;background:#fff;padding:15px;border-radius:8px;box-shadow:0 2px 5px rgba(0,0,0,0.1);margin-bottom:15px}
        .slider-group{margin:8px 0}
        label{display:inline-block;width:70px;font-weight:bold}
        img{max-width:95vw;max-height:60vh;border:2px solid #333;display:block;margin:auto}
    </style>
    <h1>Calibrador de Cores HSV</h1>
    
    <div class="controls">
        <div class="slider-group"><label>H Min: <span id="val_h_min">0</span></label><input type="range" id="h_min" min="0" max="179" value="0" oninput="atualizar(this)"></div>
        <div class="slider-group"><label>H Max: <span id="val_h_max">179</span></label><input type="range" id="h_max" min="0" max="179" value="179" oninput="atualizar(this)"></div>
        <div class="slider-group"><label>S Min: <span id="val_s_min">0</span></label><input type="range" id="s_min" min="0" max="255" value="0" oninput="atualizar(this)"></div>
        <div class="slider-group"><label>S Max: <span id="val_s_max">255</span></label><input type="range" id="s_max" min="0" max="255" value="255" oninput="atualizar(this)"></div>
        <div class="slider-group"><label>V Min: <span id="val_v_min">0</span></label><input type="range" id="v_min" min="0" max="255" value="0" oninput="atualizar(this)"></div>
        <div class="slider-group"><label>V Max: <span id="val_v_max">255</span></label><input type="range" id="v_max" min="0" max="255" value="255" oninput="atualizar(this)"></div>
    </div>

    <div><img src="/video_feed"></div>

    <script>
        function atualizar(element) {
            const id = element.id;
            const val = element.value;
            document.getElementById('val_' + id).textContent = val;
            
            fetch('/atualizar_slider', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({param: id, valor: parseInt(val)})
            });
        }
    </script>
    </html>
    """)

@app.route("/atualizar_slider", methods=["POST"])
def atualizar_slider():
    dados = request.json
    param = dados.get("param")
    valor = dados.get("valor")
    with lock:
        if param in config_hsv:
            config_hsv[param] = valor
    return jsonify(sucesso=True)

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
    threading.Thread(target=processarCalibracao, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)