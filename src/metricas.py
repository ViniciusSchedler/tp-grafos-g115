"""
Metricas estruturais (Parte I) e de redes complexas (Parte III), implementadas sobre
as listas de adjacencia. Bibliotecas externas sao usadas apenas nos testes/validacao.
"""
import math
import random
from collections import Counter, deque

from algoritmos import INF, bfs


# ------------------------------------------------------------------ graus
def resumo_graus(adj, vertices=None):
    vertices = range(len(adj)) if vertices is None else vertices
    graus = [len(adj[v]) for v in vertices]
    return {"min": min(graus), "max": max(graus), "medio": sum(graus) / len(graus), "n": len(graus)}


def distribuicao_graus(adj, vertices=None):
    """P(k): fracao de vertices com grau k."""
    vertices = list(range(len(adj))) if vertices is None else list(vertices)
    cont = Counter(len(adj[v]) for v in vertices)
    return {k: c / len(vertices) for k, c in sorted(cont.items())}


def densidade(n, m):
    """Grafo simples nao direcionado: 2|E| / (|V|(|V|-1))."""
    return 2 * m / (n * (n - 1))


# ----------------------------------------------------- bipartição (2-coloracao)
def eh_bipartido(adj):
    """BFS colorindo os niveis alternadamente; devolve False se achar aresta entre
    vertices da mesma cor (ciclo impar)."""
    n = len(adj)
    lado = [-1] * n
    for s in range(n):
        if lado[s] != -1:
            continue
        lado[s] = 0
        fila = deque([s])
        while fila:
            u = fila.popleft()
            for v in adj[u]:
                if lado[v] == -1:
                    lado[v] = 1 - lado[u]
                    fila.append(v)
                elif lado[v] == lado[u]:
                    return False
    return True


# ------------------------------------------------- triangulos e clusterizacao
def triangulos_e_clusterizacao(adj):
    """Conta exatamente os triangulos por vertice (T_v = arestas entre vizinhos de v,
    via intersecao de conjuntos) e calcula C_v = 2 T_v / (k_v (k_v - 1)).
    C_v = 0 quando k_v < 2. Devolve (total_triangulos, C_medio, transitividade)."""
    viz = [set(a) for a in adj]
    soma_c = 0.0
    total_t = 0          # soma de T_v (cada triangulo contado 3 vezes)
    triplas = 0          # sum k_v (k_v - 1) / 2  (caminhos de comprimento 2)
    for v, a in enumerate(adj):
        k = len(a)
        if k < 2:
            continue
        # cada aresta {u, w} entre vizinhos de v aparece duas vezes na soma
        t_v = sum(len(viz[u] & viz[v]) for u in a) // 2
        total_t += t_v
        triplas += k * (k - 1) // 2
        soma_c += 2 * t_v / (k * (k - 1))
    transitividade = (total_t / triplas) if triplas else 0.0
    return total_t // 3, soma_c / len(adj), transitividade


# -------------------------------------------------- excentricidade / diametro / raio
def diametro_raio_exatos(adj):
    """Diametro e raio EXATOS de um grafo conexo pelo algoritmo de limitantes de
    excentricidade (Takes & Kosters, 2011): cada BFS de v da ecc(v) e, para todo w,
        max(d(v,w), ecc(v) - d(v,w)) <= ecc(w) <= ecc(v) + d(v,w).
    Vertices cuja excentricidade nao pode mais alterar diametro/raio sao descartados.
    Devolve (diametro, raio, numero_de_BFS)."""
    n = len(adj)
    low = [0] * n
    up = [INF] * n
    candidatos = set(range(n))
    D_low, R_up = 0, INF
    D_up, R_low = INF, 0
    bfs_feitas = 0
    alterna = True
    while candidatos and (D_low < D_up or R_low < R_up):
        if alterna:   # vertice com maior limitante superior (bom para o diametro)
            v = max(candidatos, key=lambda x: (up[x], len(adj[x])))
        else:         # vertice com menor limitante inferior (bom para o raio)
            v = min(candidatos, key=lambda x: (low[x], -len(adj[x])))
        alterna = not alterna
        d, _ = bfs(adj, v)
        bfs_feitas += 1
        e = max(d)
        D_low = max(D_low, e)
        R_up = min(R_up, e)
        remover = []
        for w in candidatos:
            dw = d[w]
            low[w] = max(low[w], dw, e - dw)
            up[w] = min(up[w], e + dw)
        candidatos.discard(v)
        for w in candidatos:
            if low[w] == up[w] or (up[w] <= D_low and low[w] >= R_up):
                remover.append(w)
        for w in remover:
            candidatos.discard(w)
        D_up = max([up[w] for w in candidatos], default=D_low)
        D_up = max(D_up, D_low)
        R_low = min([low[w] for w in candidatos], default=R_up)
        R_low = min(R_low, R_up)
    return D_low, R_up, bfs_feitas


# ------------------------------------------------------ comprimento medio
def caminho_medio_amostrado(adj, k, semente):
    """Estimativa do comprimento medio dos caminhos minimos (grafo conexo):
    BFS a partir de k origens sorteadas sem reposicao; para cada origem s calcula a
    media de d(s, v) sobre os n-1 destinos. Como todas as origens tem n-1 destinos,
    a media das medias estima sem vies a media sobre todos os pares.
    Devolve (lista_medias_por_origem, histograma_de_distancias)."""
    rng = random.Random(semente)
    n = len(adj)
    origens = rng.sample(range(n), k)
    medias = []
    hist = Counter()
    for s in origens:
        d, _ = bfs(adj, s)
        soma = 0
        for x in d:
            hist[x] += 1
            soma += x
        medias.append(soma / (n - 1))
    del hist[0]
    return medias, dict(sorted(hist.items()))


# ------------------------------------------------- clusterizacao bipartida
def clusterizacao_bipartida_latapy(adj, vertices):
    """Coeficiente de agrupamento bipartido de Latapy, Magnien & Del Vecchio (2008):
        cc(u) = media, sobre v a distancia 2 de u, de |N(u) ∩ N(v)| / |N(u) ∪ N(v)|.
    Devolve a lista de cc(u) para os vertices pedidos (vertices sem vizinhos a
    distancia 2 sao ignorados)."""
    valores = []
    for u in vertices:
        comuns = Counter()
        for w in adj[u]:
            comuns.update(adj[w])  # cada ocorrencia de v = um vizinho em comum
        comuns.pop(u, None)
        if not comuns:
            continue
        ku = len(adj[u])
        soma = sum(c / (ku + len(adj[v]) - c) for v, c in comuns.items())
        valores.append(soma / len(comuns))
    return valores


# ----------------------------------------------------------- lei de potencia
def ajuste_lei_potencia(graus, k_min):
    """MLE discreto aproximado (Clauset, Shalizi & Newman, 2009, eq. 3.7):
        gamma = 1 + n [ sum ln(k_i / (k_min - 1/2)) ]^-1 ,  k_i >= k_min
    e distancia KS entre a CCDF empirica e a CCDF do modelo continuo aproximado
    P(K >= k) = (k / k_min)^(1 - gamma) (mesma aproximacao)."""
    cauda = sorted(k for k in graus if k >= k_min)
    n = len(cauda)
    gamma = 1 + n / sum(math.log(k / (k_min - 0.5)) for k in cauda)
    ks = 0.0
    cont = Counter(cauda)
    acumulado = 0
    for k in sorted(cont):
        ccdf_emp = 1 - acumulado / n          # P(K >= k) empirica
        ccdf_mod = ((k - 0.5) / (k_min - 0.5)) ** (1 - gamma)
        ks = max(ks, abs(ccdf_emp - ccdf_mod))
        acumulado += cont[k]
    erro = (gamma - 1) / math.sqrt(n)
    return {"gamma": gamma, "erro_padrao": erro, "k_min": k_min, "n_cauda": n, "ks": ks}


def melhor_k_min(graus, candidatos):
    """Escolhe k_min que minimiza a distancia KS (metodo de Clauset et al., 2009)."""
    melhores = [ajuste_lei_potencia(graus, k) for k in candidatos
                if sum(1 for g in graus if g >= k) >= 50]
    return min(melhores, key=lambda r: r["ks"])
