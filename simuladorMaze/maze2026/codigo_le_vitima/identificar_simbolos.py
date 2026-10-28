import cv2
import numpy as np
import time
from simuladorMaze.maze.codigo_le_vitima import camera
from simuladorMaze.maze.codigo_le_vitima.camera import frame_lock

# --- Configurações a calibrar ---
LARGURA_TEMPLATE = 67
ALTURA_TEMPLATE = 67
AREA_MIN = 1500
AREA_MAX = 13000
LIMIAR_SCORE = 0.55

# --- variaveis ---
quant_phi = 0
quant_psi = 0
quant_omega = 0
frame_transmissao_letra = None

# -- corzinhas --
altoBranco = np.array([255,255,255])
baixoBranco = np.array([150,150,150])

SALVAR_DEBUG = True          # deixe True enquanto estiver diagnosticando

def procurar_diferente_de_branco():
    """Ve se tem algo diferente de branco, podendo ser circulo ou letra. Retorna boolean"""
    global frame_transmissao_letra
    iniciox= 60
    fimx = 260
    inicioy = 10
    fimy = 210
    quantMinPixelsNaoBranco = 500
    frame = camera.frame_atual
    if frame is None:
        return False
    roi = frame[inicioy:fimy,iniciox:fimx]
    rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    maskBranco = cv2.inRange(rgb,baixoBranco,altoBranco)
    # frame_transmissao_letra = maskBranco
    contornos, descarte = cv2.findContours(maskBranco,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contornos:
        for cBranco in contornos:
            area = cv2.contourArea(cBranco)
            # print("procurarVitimaNaParede() area",area)
            if area>quantMinPixelsNaoBranco:
                return True
    return False

def carregar_templates_letras(diretorio="/home/banana/maze2026"):
    nomes = ["PHI", "PSI", "OMEGA"]
    templates = {}
    for nome in nomes:
        caminho = f"{diretorio}/{nome.lower()}.png"
        img = cv2.imread(caminho, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Não achei {caminho}")
        _, img_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # recorta no bounding box da letra (maior contorno, ignora pontinhos soltos)
        inv = cv2.bitwise_not(img_bin)   # letra = 255
        contornos, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = cv2.boundingRect(max(contornos, key=cv2.contourArea))
        img_bin = img_bin[y:y+h, x:x+w]

        img_bin = cv2.resize(img_bin, (LARGURA_TEMPLATE, ALTURA_TEMPLATE))
        _, img_bin = cv2.threshold(img_bin, 127, 255, cv2.THRESH_BINARY)
        templates[nome] = img_bin
    return templates


def binarizar_frame(frame_bgr):
    global frame_transmissao_letra
    cinza = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    # cinza = cv2.GaussianBlur(cinza, (3, 3), 0)
    # Mantemos INV aqui de propósito: é conveniente pro findContours
    # (que espera o "objeto" em branco/255 sobre fundo preto/0).
    # A correção de convenção acontece na hora de comparar, não aqui.
    _, binaria = cv2.threshold(cinza, 100, 255, cv2.THRESH_BINARY_INV)
    # frame_transmissao_letra = binaria
    return binaria


def extrair_candidato_letra(binaria, contorno):
    rect = cv2.minAreaRect(contorno)
    (cx, cy), (w, h), angulo = rect
    # print("extrairCandidatoLetra w,h",w,h)
    if w < h:
        angulo += 90

    lado = int(max(w, h) * 1.6) + 8   # um pouco mais de folga que antes
    x0, y0 = int(cx - lado / 2), int(cy - lado / 2)
    x1, y1 = x0 + lado, y0 + lado

    alt, larg = binaria.shape
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(larg, x1), min(alt, y1)
    recorte = binaria[y0:y1, x0:x1]
    if recorte.size == 0:
        return None

    centro_recorte = (recorte.shape[1] // 2, recorte.shape[0] // 2)
    matriz = cv2.getRotationMatrix2D(centro_recorte, angulo, 1.0)
    rotacionado = cv2.warpAffine(recorte, matriz, (recorte.shape[1], recorte.shape[0]))

    contornos2, _ = cv2.findContours(rotacionado, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos2:
        return None
    maior = max(contornos2, key=cv2.contourArea)
    bx, by, bw, bh = cv2.boundingRect(maior)
    letra = rotacionado[by:by + bh, bx:bx + bw]
    if letra.size == 0:
        return None

    letra = cv2.resize(letra, (LARGURA_TEMPLATE, ALTURA_TEMPLATE))
    # re-binariza pra tirar cinza-intermediário criado pelo resize
    _, letra = cv2.threshold(letra, 107, 255, cv2.THRESH_BINARY)
    letra = cv2.bitwise_not(letra)
    return letra

def recortar_quadrado(binaria, contorno):
    """Recorta um quadrado folgado em volta do contorno (sem rotacionar)."""
    (cx, cy), (w, h), _ = cv2.minAreaRect(contorno)
    lado = int(max(w, h) * 1.6) + 7
    # padding evita o centro "escorregar" quando a letra está perto da borda
    pad = lado
    b = cv2.copyMakeBorder(binaria, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    x0, y0 = int(cx - lado / 2) + pad, int(cy - lado / 2) + pad
    recorte = b[y0:y0 + lado, x0:x0 + lado]
    return recorte if recorte.size else None


def letra_no_angulo(recorte, angulo):
    centro = (recorte.shape[1] // 2, recorte.shape[0] // 2)
    M = cv2.getRotationMatrix2D(centro, angulo, 1.0)
    rot = cv2.warpAffine(recorte, M, (recorte.shape[1], recorte.shape[0]))
    cs, _ = cv2.findContours(rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cs:
        return None
    x, y, w, h = cv2.boundingRect(max(cs, key=cv2.contourArea))
    letra = cv2.resize(rot[y:y + h, x:x + w], (LARGURA_TEMPLATE, ALTURA_TEMPLATE))
    _, letra = cv2.threshold(letra, 127, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_not(letra)          # mesma convenção dos templates (letra = 0)


def classificar_melhor_letra(recorte, templates, passo=10):
    melhor = (None, -1.0, 0)
    for ang in range(0, 360, passo):
        letra = letra_no_angulo(recorte, ang)
        if letra is None:
            continue
        pl = letra == 0                      # pixels da letra no candidato
        for nome, tpl in templates.items():
            pt = tpl == 0                    # pixels da letra no template
            uniao = np.count_nonzero(pl | pt)
            if uniao == 0:
                continue
            score = np.count_nonzero(pl & pt) / uniao   # IoU
            if score > melhor[1]:
                melhor = (nome, score, ang)
    return melhor

def processar_possiveil_letra(frame, templates):
    iniciox= 40
    fimx = 280
    inicioy = 1
    fimy = 240
    roi = frame[inicioy:fimy,iniciox:fimx]
    binaria = binarizar_frame(roi)
    contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    melhor_resultado = None
    for c in contornos:
        area = cv2.contourArea(c)
        if area < AREA_MIN or area > AREA_MAX:
            continue

        recorte = recortar_quadrado(binaria, c)
        if recorte is None:
            continue
        nome, score, ang = classificar_melhor_letra(recorte, templates)
        # print(nome, round(score, 3), ang)   # debug
        if score > LIMIAR_SCORE:
            if melhor_resultado is None or score > melhor_resultado[1]:
                melhor_resultado = (nome, score, cv2.boundingRect(c))
    return melhor_resultado


def procurar_vitima_letra(quantidade_ciclos):
    global frame_transmissao_letra
    templates = carregar_templates_letras()
    ciclos = 0
    while ciclos < quantidade_ciclos:
        frame = camera.frame_atual
        if frame is None:
            ciclos += 1
            time.sleep(0.1)
            continue
        frame = frame.copy()
        resultado = processar_possiveil_letra(frame, templates)
        if resultado:
            nome, score, (x, y, w, h) = resultado
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{nome} {score:.2f}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # copia DEPOIS de desenhar, para o retângulo aparecer no stream
        with frame_lock:
            frame_transmissao_letra = frame.copy()
        if resultado:
            return nome
        ciclos += 1
    return False

def vi_vitima_letra(omega, psi, phi):
    """retorna quantos kits precisam ser depositados"""
    quantMinima = 4
    if omega >= quantMinima:
        print("vítima crítica")
        return 2
    elif psi >= quantMinima:
        print("vítima estável")
        return 1
    elif phi >= quantMinima:
        print("vítima ilesa")
        return 0

def processar_vitima_letra(relogio_processar_vitima_letra,tempo_verificando_letra,ciclosDeVerificacao=700):
    quant_omega = 0
    quant_psi = 0
    quant_phi = 0
    relogio = relogio_processar_vitima_letra()
    while relogio < tempo_verificando_letra:
        print("while achou algo quant o,psi,phi",quant_omega,quant_psi,quant_phi)
        # print(relogio_processar_vitima_letra())
        relogio = relogio_processar_vitima_letra()
        letra = procurar_vitima_letra(ciclosDeVerificacao)
        if not False:
            if letra == "OMEGA":
                quant_omega += 1
            elif letra == "PSI":
                quant_psi += 1
            elif letra == "PHI":
                quant_phi += 1
    vitima = vi_vitima_letra(quant_omega, quant_psi, quant_phi)
    return vitima