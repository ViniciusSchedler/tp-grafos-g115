"""
Representacao do grafo: listas de adjacencia (slide 03: forma compacta para grafos
esparsos, |E| << |V|^2).

  adj[v]  = lista de vizinhos de v
  peso[v] = lista paralela com o peso de cada aresta (v, adj[v][i])

Vertices 0..U-1 sao usuarios; U..U+B-1 sao cervejas (ver preparar_dados.py).
Peso da aresta {usuario, cerveja}: w = 6 - nota_media, com nota em [0, 5] -> w em [1, 6].
"""
import gzip
import os
import random
from collections import deque

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ_ARESTAS = os.path.join(RAIZ, "data", "processed", "arestas.csv.gz")


def carregar_grafo(caminho=ARQ_ARESTAS):
    """Le a lista de arestas tratada e devolve (adj, peso, n_usuarios)."""
    arestas = []
    max_u = -1
    max_v = -1
    with gzip.open(caminho, "rt", encoding="utf-8") as f:
        next(f)  # cabecalho
        for linha in f:
            u, b, nota, _ = linha.split(",")
            u, b = int(u), int(b)
            arestas.append((u, b, 6.0 - float(nota)))
            max_u = max(max_u, u)
            max_v = max(max_v, b)
    n = max_v + 1
    adj = [[] for _ in range(n)]
    peso = [[] for _ in range(n)]
    for u, b, w in arestas:
        adj[u].append(b)
        peso[u].append(w)
        adj[b].append(u)
        peso[b].append(w)
    return adj, peso, max_u + 1


def num_arestas(adj):
    return sum(len(viz) for viz in adj) // 2


def lista_arestas(adj, peso):
    """Arestas nao direcionadas (u < v, w) sem repeticao."""
    return [(u, v, w) for u in range(len(adj)) for v, w in zip(adj[u], peso[u]) if u < v]


def componentes_conexas(adj):
    """Rotula cada vertice com o id da sua componente (BFS a partir de cada vertice nao visitado)."""
    n = len(adj)
    comp = [-1] * n
    tamanhos = []
    for s in range(n):
        if comp[s] != -1:
            continue
        c = len(tamanhos)
        comp[s] = c
        fila = deque([s])
        tam = 0
        while fila:
            u = fila.popleft()
            tam += 1
            for v in adj[u]:
                if comp[v] == -1:
                    comp[v] = c
                    fila.append(v)
        tamanhos.append(tam)
    return comp, tamanhos


def subgrafo_induzido(adj, peso, vertices):
    """Subgrafo induzido por 'vertices', reindexado 0..k-1. Devolve (adj2, peso2, antigo->novo)."""
    novo = {v: i for i, v in enumerate(vertices)}
    adj2 = [[] for _ in vertices]
    peso2 = [[] for _ in vertices]
    for v, i in novo.items():
        for u, w in zip(adj[v], peso[v]):
            j = novo.get(u)
            if j is not None:
                adj2[i].append(j)
                peso2[i].append(w)
    return adj2, peso2, novo


def maior_componente(adj, peso):
    """Subgrafo induzido pela maior componente conexa (MCC)."""
    comp, tamanhos = componentes_conexas(adj)
    c_max = max(range(len(tamanhos)), key=lambda c: tamanhos[c])
    vertices = [v for v in range(len(adj)) if comp[v] == c_max]
    adj2, peso2, novo = subgrafo_induzido(adj, peso, vertices)
    return adj2, peso2, vertices


def amostra_conexa(adj, peso, k, semente):
    """Subgrafo conexo com k vertices: os k primeiros vertices na ordem de uma BFS
    iniciada em um vertice sorteado (a arvore BFS garante que o induzido e conexo).
    Devolve (adj2, peso2, ordem), onde ordem[i] e o vertice original do novo vertice i."""
    rng = random.Random(semente)
    s = rng.randrange(len(adj))
    vistos = {s}
    ordem = [s]
    fila = deque([s])
    while fila and len(ordem) < k:
        u = fila.popleft()
        viz = adj[u][:]
        rng.shuffle(viz)  # evita que a amostra dependa da ordem de leitura
        for v in viz:
            if v not in vistos:
                vistos.add(v)
                ordem.append(v)
                fila.append(v)
                if len(ordem) == k:
                    break
    adj2, peso2, _ = subgrafo_induzido(adj, peso, ordem)
    return adj2, peso2, ordem
