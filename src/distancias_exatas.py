"""
Distancias exatas na maior componente conexa (MCC): uma BFS a partir de CADA vertice
(|V| x O(V + E)), dividida entre processos. Para cada origem guarda a excentricidade e
a soma das distancias; acumula o histograma de d(u, v).

Saida: results/distancias_mcc.json (diametro, raio, comprimento medio exato, histograma)
       results/excentricidades_mcc.csv.gz
"""
import gzip
import json
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algoritmos import bfs  # noqa: E402
from grafo import RAIZ, carregar_grafo, maior_componente  # noqa: E402

_adj = None


def _inicia():
    global _adj
    adj, peso, _ = carregar_grafo()
    _adj, _, _ = maior_componente(adj, peso)


def _bloco(origens):
    hist = Counter()
    saida = []
    for s in origens:
        d, _ = bfs(_adj, s)
        c = Counter(d)
        hist.update(c)
        saida.append((s, max(d), sum(d)))
    return saida, hist


def main(processos=8):
    t0 = time.perf_counter()
    adj, peso, _ = carregar_grafo()
    adj, _, _ = maior_componente(adj, peso)
    n = len(adj)
    blocos = [list(range(i, min(i + 500, n))) for i in range(0, n, 500)]
    ecc = [0] * n
    soma = [0] * n
    hist = Counter()
    with Pool(processos, initializer=_inicia) as pool:
        for i, (saida, h) in enumerate(pool.imap_unordered(_bloco, blocos)):
            for s, e, sd in saida:
                ecc[s] = e
                soma[s] = sd
            hist.update(h)
            print(f"bloco {i + 1}/{len(blocos)}  {time.perf_counter() - t0:.0f}s", flush=True)
    del hist[0]
    pares = n * (n - 1)  # pares ordenados (u, v), u != v
    resultado = {
        "n_mcc": n,
        "diametro": max(ecc),
        "raio": min(ecc),
        "comprimento_medio_exato": sum(soma) / pares,
        "histograma_distancias_pares_ordenados": {str(k): v for k, v in sorted(hist.items())},
        "processos": processos,
        "tempo_total_s": time.perf_counter() - t0,
    }
    with open(os.path.join(RAIZ, "results", "distancias_mcc.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2)
    with gzip.open(os.path.join(RAIZ, "results", "excentricidades_mcc.csv.gz"), "wt") as f:
        f.write("vertice_mcc,excentricidade,soma_distancias\n")
        for v in range(n):
            f.write(f"{v},{ecc[v]},{soma[v]}\n")
    print(json.dumps({k: v for k, v in resultado.items() if "hist" not in k}, indent=2))


if __name__ == "__main__":
    main()
