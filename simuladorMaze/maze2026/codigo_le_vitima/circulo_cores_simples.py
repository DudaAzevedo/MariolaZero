"""Lê as cores dos 5 aros do alvo (externo -> centro).

Uso: python circulo_cores_simples.py imagem.png
"""
import sys
from itertools import permutations

import cv2
import numpy as np

import simuladorMaze.maze.codigo_le_vitima.constantes as cons

# Cor de referência (L, a, b) no Lab do OpenCV. O preto só olha o brilho.

REFERENCIAS = {
    cons.PRETO:    (35, 128, 128),
    cons.VERMELHO: (110, 175, 95),
    cons.AMARELO:  (235, 155, 205),
    cons.VERDE:    (125, 80, 160),
    cons.AZUL:     (130, 115, 70),
}

NOMES = list(REFERENCIAS)
PONTOS = {cons.AZUL: cons.AZUL_SOMAR, cons.VERDE: cons.VERDE_SOMAR,
          cons.AMARELO: cons.AMARELO_SOMAR, cons.VERMELHO: cons.VERMELHO_SOMAR,
          cons.PRETO: cons.PRETO_SOMAR}


def calculo_kits(cores):

    #ajeitar somatória kits

    soma = 0

    for c in cores:

        soma += PONTOS[c]


    print(f'KITS {soma} ')
    
    return soma


def custo(lab, nome):
    """Quão longe uma cor medida está da cor de referência."""
    L, a, b = lab
    Lr, ar, br = REFERENCIAS[nome]
    if nome == cons.PRETO:
        return 2 * abs(L - Lr)
    return np.hypot(a - ar, b - br) + 0.25 * abs(L - Lr)


def achar_alvo(img):
    """Contorno do alvo: tudo que é 'tinta' (saturado), diferente do papel."""
    hsv = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2HSV)
    tinta = ((hsv[..., 1] > 55) & (hsv[..., 2] > 50)).astype(np.uint8) * 255
    tinta = cv2.morphologyEx(tinta, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    contornos, _ = cv2.findContours(tinta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        raise ValueError("Alvo não encontrado.")
    maior = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(maior) < 0.02 * img.shape[0] * img.shape[1]:
        raise ValueError("Alvo muito pequeno.")
    return maior


def analisar_alvo(img):
    """Reconhece cinco aros em ordem externo -> interno; cores podem repetir."""
    contorno = achar_alvo(img)
    (cx, cy), eixos, _ = cv2.fitEllipse(cv2.convexHull(contorno))
    rx = max(float(eixos[0]) / 2.0, 1.0)
    ry = max(float(eixos[1]) / 2.0, 1.0)
    h, w = img.shape[:2]

    # Raio elíptico normalizado. Calculado uma vez, sem criar 100 máscaras da imagem.
    yy, xx = np.indices((h, w), dtype=np.float32)
    raio = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    del xx, yy

    mascara = np.zeros((h, w), np.uint8)
    cv2.drawContours(mascara, [contorno], -1, 255, -1)
    k = max(3, int(min(eixos) * 0.035)) | 1
    mascara = cv2.erode(mascara, np.ones((k, k), np.uint8))

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Remover papel claro e sobreposições de depuração.
    # As linhas verdes neon da depuração têm matiz verde, saturação alta e brilho alto;
    # excluí-las da amostragem para que não sejam confundidas com a tinta do alvo.
    mascara[(hsv[..., 1] < 40) & (hsv[..., 2] > 135)] = 0
    neon_verde = (
        (hsv[..., 0] >= 35) & (hsv[..., 0] <= 90) &
        (hsv[..., 1] >= 150) & (hsv[..., 2] >= 175)
    )
    mascara[neon_verde] = 0
    mascara[(hsv[..., 1] > 220) & (hsv[..., 2] > 240)] = 0

    lab = cv2.cvtColor(cv2.GaussianBlur(img, (3, 3), 0), cv2.COLOR_BGR2LAB)
    labf = lab.astype(np.float32)

    # Evita bordas de transição entre aros, calculando gradiente uma única vez.
    grad = np.zeros((h, w), np.float32)
    for ch in range(3):
        gx = cv2.Sobel(labf[..., ch], cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(labf[..., ch], cv2.CV_32F, 0, 1, ksize=3)
        grad += cv2.magnitude(gx, gy)
    mascara[grad > 75] = 0

    # Perfil radial com bins; amostras agrupadas uma única vez.
    N = 64
    rmin, rmax = 0.06, 0.98
    valid = (mascara > 0) & (raio >= rmin) & (raio < rmax)
    ys, xs = np.nonzero(valid)
    if len(xs) < 40:
        raise ValueError("Poucos pixels válidos para reconhecer os aros.")

    bin_id = ((raio[ys, xs] - rmin) * (N / (rmax - rmin))).astype(np.int32)
    bin_id = np.clip(bin_id, 0, N - 1)
    pix = labf[ys, xs]
    perfil = np.full((N, 3), np.nan, np.float32)
    qtd = np.bincount(bin_id, minlength=N)

    # A mediana é calculada apenas nos pixels já selecionados, não na imagem inteira.
    for b in range(N):
        sel = bin_id == b
        if np.count_nonzero(sel) >= 3:
            perfil[b] = np.median(pix[sel], axis=0)

    ok = np.isfinite(perfil[:, 0])
    if ok.sum() < 12:
        raise ValueError("Poucos pixels válidos para reconhecer os aros.")
    indices = np.arange(N)
    bons = np.flatnonzero(ok)
    for ch in range(3):
        perfil[:, ch] = np.interp(indices, bons, perfil[bons, ch])

    # Custos de classificação por bin. Preto recebe uma regra explícita por luminosidade:
    # no Lab do OpenCV, L vai de 0 a 255 e a/b neutros ficam perto de 128.
    C = len(NOMES)
    custos = np.empty((N, C), np.float32)
    for i in range(N):
        L, a, b = perfil[i]
        for j, nome in enumerate(NOMES):
            if nome == cons.PRETO:
                # O preto fotografado pode ficar cinza por iluminação/reflexo.
                # Prioriza luminosidade e usa cromaticidade apenas como fator secundário.
                chroma = np.hypot(a - 128.0, b - 128.0)
                custos[i, j] = max(0.0, L - 72.0) * 1.35 + chroma * 0.22
            else:
                custos[i, j] = custo((L, a, b), nome)
                # Cores vivas não devem ganhar uma faixa escura só por semelhança de matiz.
                if L < 82.0:
                    custos[i, j] += (82.0 - L) * 0.9
        # Reforço para preto em faixas escuras; não exige neutralidade perfeita,
        # pois o balanço de branco pode dar um tom ao preto real.
        chroma = np.hypot(a - 128.0, b - 128.0)
        if L < 72.0 and cons.PRETO in NOMES:
            custos[i, NOMES.index(cons.PRETO)] *= 0.45

    # DP para cinco segmentos radiais contíguos. Cores não são exclusivas.
    # O cálculo é sobre 64 bins (não sobre cada pixel), reduzindo bastante o custo.
    prefix = np.vstack([np.zeros((1, C), np.float64), np.cumsum(custos, axis=0, dtype=np.float64)])
    K = 5
    min_bins = 5
    dp = np.full((K + 1, N + 1), np.inf, np.float64)
    prev = np.full((K + 1, N + 1), -1, np.int32)
    chosen = np.full((K + 1, N + 1), -1, np.int32)
    dp[0, 0] = 0.0

    for kseg in range(1, K + 1):
        lo_end = kseg * min_bins
        hi_end = N - (K - kseg) * min_bins
        for end in range(lo_end, hi_end + 1):
            lo_start = (kseg - 1) * min_bins
            hi_start = end - min_bins
            starts = np.arange(lo_start, hi_start + 1)
            valid_starts = np.isfinite(dp[kseg - 1, starts])
            if not np.any(valid_starts):
                continue
            starts = starts[valid_starts]
            segment_costs = prefix[end][None, :] - prefix[starts]
            best_color = np.argmin(segment_costs, axis=1)
            best_cost = segment_costs[np.arange(len(starts)), best_color] + dp[kseg - 1, starts]
            pos = int(np.argmin(best_cost))
            dp[kseg, end] = best_cost[pos]
            prev[kseg, end] = starts[pos]
            chosen[kseg, end] = best_color[pos]

    if not np.isfinite(dp[K, N]):
        raise ValueError("Não foi possível separar os cinco aros.")

    # A reconstrução começa no segmento externo e caminha para dentro.
    cores = []
    end = N
    for kseg in range(K, 0, -1):
        color_idx = int(chosen[kseg, end])
        start = int(prev[kseg, end])
        if color_idx < 0 or start < 0:
            raise ValueError("Falha ao reconstruir os aros.")
        cores.append(NOMES[color_idx])
        end = start

    return {
        "cores": cores,
        "kits": calculo_kits(cores),
        "centro": (int(cx), int(cy)),
        "contorno": contorno,
    }

def custo_cor(lab, nome):
    """Compatibilidade explícita para a classificação do perfil radial."""
    return custo(lab, nome)

def main():
    if len(sys.argv) != 2:
        return print("Uso: python circulo_cores_simples.py imagem.png")
    img = cv2.imread(sys.argv[1])
    if img is None:
        raise FileNotFoundError("Não consegui abrir a imagem.")
    r = analisar_alvo(img)
    print("Cores (externo -> interno):", " -> ".join(r["cores"]))
    print("CALCULO DE KITS:", r["kits"])


if __name__ == "__main__":
    main()
