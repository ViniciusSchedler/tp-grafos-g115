"""
Algoritmos da Parte II, escritos seguindo os pseudocodigos dos slides de MATA53
(nomes d[v], f[v], pi[v], cor, key[v], Relaxa, IniciaOrigemUnica).

Todos recebem o grafo como listas de adjacencia (adj, peso), ver grafo.py.
As versoes de DFS e Tarjan sao iterativas (pilha explicita) porque a recursao do
Python estoura com ~10^5 vertices; a ordem de visita e a mesma da versao recursiva.
"""
import heapq
from collections import deque

INF = float("inf")
BRANCO, CINZA, PRETO = 0, 1, 2


# ---------------------------------------------------------------- BFS  O(V + E)
def bfs(adj, s):
    """BuscaEmLargura(G, s) do slide: devolve (d, pi)."""
    n = len(adj)
    cor = [BRANCO] * n
    d = [INF] * n
    pi = [None] * n
    cor[s] = CINZA
    d[s] = 0
    Q = deque([s])
    while Q:
        u = Q.popleft()
        for v in adj[u]:
            if cor[v] == BRANCO:
                d[v] = d[u] + 1
                pi[v] = u
                cor[v] = CINZA
                Q.append(v)
        cor[u] = PRETO
    return d, pi


# ---------------------------------------------------------------- DFS  O(V + E)
def dfs(adj):
    """DFS(G) + VisitaDFS(v) do slide: devolve (d, f, pi, numero_de_arvores)."""
    n = len(adj)
    cor = [BRANCO] * n
    pi = [None] * n
    d = [0] * n
    f = [0] * n
    tempo = 0
    arvores = 0
    for s in range(n):
        if cor[s] != BRANCO:
            continue
        arvores += 1
        cor[s] = CINZA
        tempo += 1
        d[s] = tempo
        pilha = [(s, 0)]  # (vertice, proximo indice de Adj[v] a examinar)
        while pilha:
            v, i = pilha[-1]
            if i < len(adj[v]):
                pilha[-1] = (v, i + 1)
                u = adj[v][i]
                if cor[u] == BRANCO:  # equivale a chamar VisitaDFS(u)
                    pi[u] = v
                    cor[u] = CINZA
                    tempo += 1
                    d[u] = tempo
                    pilha.append((u, 0))
            else:  # fim de VisitaDFS(v)
                pilha.pop()
                cor[v] = PRETO
                tempo += 1
                f[v] = tempo
    return d, f, pi, arvores


# ------------------------------------------------------- Eulerianidade  O(V + E)
def verificar_euleriano(adj):
    """Teoremas do slide 05: G (com arestas) tem circuito euleriano sse e conexo
    (desconsiderando vertices isolados) e todo vertice tem grau par; tem caminho
    euleriano (nao fechado) sse e conexo e tem exatamente 2 vertices de grau impar."""
    n = len(adj)
    impares = sum(1 for v in range(n) if len(adj[v]) % 2 == 1)
    com_arestas = [v for v in range(n) if adj[v]]
    conexo = True
    if com_arestas:
        d, _ = bfs(adj, com_arestas[0])
        conexo = all(d[v] != INF for v in com_arestas)
    return {
        "vertices_grau_impar": impares,
        "conexo_ignorando_isolados": conexo,
        "circuito_euleriano": conexo and impares == 0,
        "caminho_euleriano": conexo and impares == 2,
    }


# ---------------------------------------------- Relaxa / IniciaOrigemUnica
def inicia_origem_unica(n, s):
    d = [INF] * n
    pi = [None] * n
    d[s] = 0
    return d, pi


# ------------------------------------------------ Dijkstra  O((V + E) log V)
def dijkstra(adj, peso, s):
    """Dijkstra(G, w, s) com Q = heap minimo (heapq).
    heapq nao tem DiminuirChave: cada Relaxa bem-sucedido insere (d[v], v) de novo e
    entradas antigas sao ignoradas ao sair do heap (S[u] ja True). Sao no maximo |E|
    insercoes, logo o custo continua O((V + E) log V)."""
    n = len(adj)
    d, pi = inicia_origem_unica(n, s)
    S = [False] * n
    Q = [(0, s)]
    while Q:
        du, u = heapq.heappop(Q)  # ExtrairMinimo(Q)
        if S[u]:
            continue
        S[u] = True
        for v, w in zip(adj[u], peso[u]):
            if d[v] > du + w:  # Relaxa(u, v, w)
                d[v] = du + w
                pi[v] = u
                heapq.heappush(Q, (d[v], v))
    return d, pi


# --------------------------------------------------- Bellman-Ford  O(V E)
def arcos_de(adj, peso):
    """Cada aresta nao direcionada {u, v} vira os arcos (u, v) e (v, u)."""
    return [(u, v, w) for u in range(len(adj)) for v, w in zip(adj[u], peso[u])]


def bellman_ford(n, arcos, s, parar_cedo=False):
    """Bellman-Ford(G, w, s) do slide. Devolve (VERDADE/FALSO, d, pi).
    parar_cedo=True interrompe quando uma passada inteira nao altera d[]
    (resultado identico; so evita passadas inuteis)."""
    d, pi = inicia_origem_unica(n, s)
    passadas = 0
    for _ in range(n - 1):
        passadas += 1
        mudou = False
        for u, v, w in arcos:
            if d[v] > d[u] + w:  # Relaxa(u, v, w)
                d[v] = d[u] + w
                pi[v] = u
                mudou = True
        if parar_cedo and not mudou:
            break
    for u, v, w in arcos:
        if d[v] > d[u] + w:
            return False, d, pi, passadas
    return True, d, pi, passadas


# ------------------------------------------------- Floyd-Warshall  O(V^3)
def floyd_warshall(adj, peso):
    """Matriz D^(k) do slide 14: D[i][j] = min(D[i][j], D[i][k] + D[k][j])."""
    n = len(adj)
    D = [[INF] * n for _ in range(n)]
    for i in range(n):
        D[i][i] = 0
        for j, w in zip(adj[i], peso[i]):
            D[i][j] = min(D[i][j], w)
    for k in range(n):
        Dk = D[k]
        for i in range(n):
            dik = D[i][k]
            if dik == INF:  # nenhum j melhora passando por k
                continue
            Di = D[i]
            for j in range(n):
                if dik + Dk[j] < Di[j]:
                    Di[j] = dik + Dk[j]
    return D


# ------------------------- Tarjan: articulacoes e pontes  O(V + E)
def tarjan_articulacoes_pontes(adj):
    """Tarjan (1972) para grafos nao direcionados, sobre a DFS do slide:
    low[v] = menor d[] alcancavel a partir da subarvore de v usando no maximo
    uma aresta de retorno.
      * (v, u) e ponte            se low[u] > d[v]
      * v (nao raiz) e articulacao se low[u] >= d[v] para algum filho u
      * a raiz e articulacao       se tem 2 ou mais filhos na arvore DFS"""
    n = len(adj)
    d = [0] * n  # 0 = BRANCO (ainda nao descoberto)
    low = [0] * n
    pi = [None] * n
    articulacao = [False] * n
    pontes = []
    tempo = 0
    for raiz in range(n):
        if d[raiz]:
            continue
        tempo += 1
        d[raiz] = low[raiz] = tempo
        filhos_raiz = 0
        pilha = [(raiz, 0)]
        while pilha:
            v, i = pilha[-1]
            if i < len(adj[v]):
                pilha[-1] = (v, i + 1)
                u = adj[v][i]
                if d[u] == 0:  # aresta da arvore
                    pi[u] = v
                    tempo += 1
                    d[u] = low[u] = tempo
                    if v == raiz:
                        filhos_raiz += 1
                    pilha.append((u, 0))
                elif u != pi[v]:  # aresta de retorno
                    low[v] = min(low[v], d[u])
            else:
                pilha.pop()
                p = pi[v]
                if p is not None:
                    low[p] = min(low[p], low[v])
                    if low[v] > d[p]:
                        pontes.append((p, v))
                    if p != raiz and low[v] >= d[p]:
                        articulacao[p] = True
        if filhos_raiz >= 2:
            articulacao[raiz] = True
    return [v for v in range(n) if articulacao[v]], pontes


# ----------------------------------------------------- Prim  O(E log V)
def prim(adj, peso):
    """Prim(G, w, r) do slide com Q = heap (mesma tecnica de insercao repetida do
    Dijkstra). Se G for desconexo, reinicia em cada componente -> floresta geradora minima."""
    n = len(adj)
    key = [INF] * n
    pi = [None] * n
    naQ = [True] * n
    total = 0.0
    arestas = []
    for r in range(n):
        if not naQ[r]:
            continue
        key[r] = 0
        Q = [(0, r)]
        while Q:
            k, u = heapq.heappop(Q)  # ExtrairMinimo(Q)
            if not naQ[u]:
                continue
            naQ[u] = False
            if pi[u] is not None:
                arestas.append((pi[u], u, k))
                total += k
            for v, w in zip(adj[u], peso[u]):
                if naQ[v] and w < key[v]:
                    pi[v] = u
                    key[v] = w
                    heapq.heappush(Q, (w, v))
    return arestas, total


# --------------------------------------------------- Kruskal  O(E log V)
def kruskal(n, arestas):
    """Kruskal: percorre as arestas em ordem crescente de peso e aceita a aresta
    se ela liga duas arvores diferentes da floresta (union-find com compressao de
    caminho e uniao por posto)."""
    pai = list(range(n))
    posto = [0] * n

    def encontrar(x):
        raiz = x
        while pai[raiz] != raiz:
            raiz = pai[raiz]
        while pai[x] != raiz:  # compressao de caminho
            pai[x], x = raiz, pai[x]
        return raiz

    escolhidas = []
    total = 0.0
    for u, v, w in sorted(arestas, key=lambda a: a[2]):
        ru, rv = encontrar(u), encontrar(v)
        if ru != rv:
            if posto[ru] < posto[rv]:
                ru, rv = rv, ru
            pai[rv] = ru
            if posto[ru] == posto[rv]:
                posto[ru] += 1
            escolhidas.append((u, v, w))
            total += w
    return escolhidas, total
