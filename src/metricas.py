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
    P(K >= k) = ((k - 1/2) / (k_min - 1/2))^(1 - gamma) (mesma aproximacao).
    A aproximacao so e boa para k_min >~ 6 (Clauset et al., 2009); o ajuste usado nos
    resultados e ajuste_discreto_exato."""
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


# ------------------------------------------- lei de potencia: MLE discreto exato
# A normalizacao da lei de potencia discreta P(k) = k^-gamma / zeta(gamma, k_min), k >= k_min,
# usa a funcao zeta de Hurwitz zeta(gamma, k_min) = sum_{k >= k_min} k^-gamma (scipy).
def _preparar(graus):
    import numpy as np
    x = np.sort(np.asarray(graus, dtype=float))
    suf = np.concatenate([np.cumsum(np.log(x)[::-1])[::-1], [0.0]])  # suf[i] = sum ln x[i:]
    vals, cont = np.unique(x, return_counts=True)
    return x, suf, vals, cont


def _ajuste_kmin(prep, k_min):
    """MLE exato para um k_min fixo: maximiza
        ln L(gamma) = -n ln zeta(gamma, k_min) - gamma * sum ln k_i
    e calcula a distancia KS entre a CCDF empirica e a CCDF exata
        P(K >= k) = zeta(gamma, k) / zeta(gamma, k_min)."""
    import numpy as np
    from scipy.optimize import minimize_scalar
    from scipy.special import zeta
    x, suf, vals, cont = prep
    i = int(np.searchsorted(x, k_min))
    n = len(x) - i
    S = suf[i]
    res = minimize_scalar(lambda g: n * math.log(zeta(g, k_min)) + g * S, bounds=(1.0001, 8.0),
                          method="bounded", options={"xatol": 1e-8})
    g = float(res.x)
    j = int(np.searchsorted(vals, k_min))
    kv, c = vals[j:], cont[j:]
    emp = 1.0 - (np.cumsum(c) - c) / n                  # P(K >= k) empirica nos valores observados
    emp_dep = np.append(emp[1:], 0.0)                   # empirica logo depois de cada valor
    z0 = zeta(g, k_min)
    mod = zeta(g, kv) / z0                              # P(K >= k) do modelo
    mod_dep = zeta(g, kv + 1) / z0                      # P(K >= k+1) do modelo
    ks = float(max(np.max(np.abs(emp - mod)), np.max(np.abs(emp_dep - mod_dep))))
    h = 1e-4                                            # erro padrao: 1 / sqrt(n * d2/dg2 ln zeta)
    l2 = (math.log(zeta(g + h, k_min)) - 2 * math.log(z0) + math.log(zeta(g - h, k_min))) / h ** 2
    return {"gamma": g, "erro_padrao": 1 / math.sqrt(n * l2), "k_min": float(k_min), "n_cauda": n, "ks": ks}


def ajuste_discreto_exato(graus, k_max_candidato=1000, min_cauda=50):
    """Metodo de Clauset et al. (2009): MLE exato para cada k_min candidato (valores
    observados <= k_max_candidato com pelo menos 'min_cauda' vertices na cauda) e escolha
    do k_min de menor distancia KS."""
    prep = _preparar(graus)
    x, vals = prep[0], prep[2]
    cands = [k for k in vals if k <= k_max_candidato and len(x) - x.searchsorted(k) >= min_cauda]
    return min((_ajuste_kmin(prep, k) for k in cands), key=lambda r: r["ks"])


def _amostra_lei_potencia(rng, m, gamma, k_min, k_tab=10 ** 6):
    """m valores da lei de potencia discreta por inversao da CCDF exata, tabelada ate
    k_tab; acima disso (probabilidade ~1e-3) usa a aproximacao continua de Clauset et al.
    (2009, eq. D.6), precisa para k grande."""
    import numpy as np
    from scipy.special import zeta
    ks = np.arange(k_min, k_tab + 1, dtype=float)
    ccdf = zeta(gamma, ks) / zeta(gamma, k_min)          # decrescente, ccdf[0] = 1
    u = rng.random(m)
    cont = len(ccdf) - np.searchsorted(ccdf[::-1], u, side="left")  # quantos k tem P(K>=k) >= u
    out = k_min + cont - 1.0
    fora = cont == len(ccdf)
    if fora.any():
        cont_ = np.floor((k_min - 0.5) * u[fora] ** (-1 / (gamma - 1)) + 0.5)
        out[fora] = np.maximum(cont_, k_tab + 1)
    return out


def bondade_ajuste_bootstrap(graus, B, semente, k_max_candidato=1000):
    """Teste de bondade de ajuste ABSOLUTO de Clauset et al. (2009, sec. 4.1): gera B
    conjuntos sinteticos do mesmo tamanho (valores < k_min reamostrados dos dados; cauda
    sorteada da lei de potencia ajustada), refaz todo o ajuste (inclusive a escolha de
    k_min) e devolve p = fracao de conjuntos com KS >= KS observado.
    p <= 0,1 => a lei de potencia e descartada como modelo dos dados."""
    import numpy as np
    obs = ajuste_discreto_exato(graus, k_max_candidato)
    x = np.asarray(graus, dtype=float)
    abaixo = x[x < obs["k_min"]]
    n, ntail = len(x), obs["n_cauda"]
    rng = np.random.default_rng(semente)
    ks_sint = []
    for _ in range(B):
        m = int(rng.binomial(n, ntail / n))
        sint = np.concatenate([rng.choice(abaixo, n - m) if len(abaixo) else np.empty(0),
                               _amostra_lei_potencia(rng, m, obs["gamma"], obs["k_min"])])
        ks_sint.append(ajuste_discreto_exato(sint, k_max_candidato)["ks"])
    p = sum(1 for k in ks_sint if k >= obs["ks"]) / B
    return {"observado": obs, "B": B, "p_valor": p, "ks_sinteticos_max": max(ks_sint),
            "ks_sinteticos_media": sum(ks_sint) / B}
