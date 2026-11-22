"""
Validacao dos algoritmos:
  (1) grafos pequenos com resposta conhecida (exemplos dos slides / CLRS);
  (2) comparacao com o NetworkX em grafos aleatorios com semente fixa.
Executar:  python tests/test_algoritmos.py
"""
import math
import os
import random
import sys

import networkx as nx

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from algoritmos import (INF, arcos_de, bellman_ford, bfs, dfs, dijkstra,  # noqa: E402
                        floyd_warshall, kruskal, prim, tarjan_articulacoes_pontes,
                        verificar_euleriano)
from grafo import lista_arestas  # noqa: E402


def de_arestas(n, arestas, dirigido=False):
    adj = [[] for _ in range(n)]
    peso = [[] for _ in range(n)]
    for u, v, w in arestas:
        adj[u].append(v)
        peso[u].append(w)
        if not dirigido:
            adj[v].append(u)
            peso[v].append(w)
    return adj, peso


def para_nx(adj, peso):
    G = nx.Graph()
    G.add_nodes_from(range(len(adj)))
    for u, v, w in lista_arestas(adj, peso):
        G.add_edge(u, v, weight=w)
    return G


def grafo_aleatorio(n, m, semente):
    rng = random.Random(semente)
    arestas = set()
    while len(arestas) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            arestas.add((min(u, v), max(u, v)))
    return de_arestas(n, [(u, v, rng.randint(1, 10)) for u, v in arestas])


# ------------------------------------------------------------ casos conhecidos
def test_agm_clrs():
    # grafo do slide g10 (CLRS fig. 23.1): a..i = 0..8 ; AGM tem peso 37
    a, b, c, d, e, f, g, h, i = range(9)
    E = [(a, b, 4), (a, h, 8), (b, c, 8), (b, h, 11), (c, d, 7), (c, f, 4), (c, i, 2),
         (d, e, 9), (d, f, 14), (e, f, 10), (f, g, 2), (g, h, 1), (g, i, 6), (h, i, 7)]
    adj, peso = de_arestas(9, E)
    arestas_p, total_p = prim(adj, peso)
    arestas_k, total_k = kruskal(9, E)
    assert total_p == 37 and total_k == 37
    assert len(arestas_p) == len(arestas_k) == 8


def test_floyd_warshall_slide():
    # exemplo do slide g14 (vertices 1..4 -> 0..3), grafo dirigido
    E = [(0, 1, 3), (0, 3, 7), (1, 0, 8), (1, 2, 2), (2, 0, 5), (2, 3, 1), (3, 0, 2)]
    adj, peso = de_arestas(4, E, dirigido=True)
    D = floyd_warshall(adj, peso)
    assert D == [[0, 3, 5, 6], [5, 0, 2, 3], [3, 6, 0, 1], [2, 5, 7, 0]]
    # Dijkstra e Bellman-Ford devem concordar com cada linha
    for s in range(4):
        assert dijkstra(adj, peso, s)[0] == D[s]
        ok, dist, _, _ = bellman_ford(4, arcos_de(adj, peso), s)
        assert ok and dist == D[s]


def test_bellman_ford_ciclo_negativo():
    E = [(0, 1, 1), (1, 2, -2), (2, 0, -1)]
    adj, peso = de_arestas(3, E, dirigido=True)
    ok, _, _, _ = bellman_ford(3, arcos_de(adj, peso), 0)
    assert ok is False


def test_euler_konigsberg_e_ciclo():
    # Konigsberg (multigrafo): graus 5,3,3,3 -> nem circuito nem caminho
    A, B, C, D = range(4)
    E = [(A, B, 1), (A, B, 1), (A, C, 1), (A, C, 1), (A, D, 1), (B, D, 1), (C, D, 1)]
    r = verificar_euleriano(de_arestas(4, E)[0])
    assert r["vertices_grau_impar"] == 4 and not r["circuito_euleriano"] and not r["caminho_euleriano"]
    ciclo = de_arestas(5, [(i, (i + 1) % 5, 1) for i in range(5)])[0]
    assert verificar_euleriano(ciclo)["circuito_euleriano"]
    caminho = de_arestas(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)])[0]
    assert verificar_euleriano(caminho)["caminho_euleriano"]


def test_tarjan_pequeno():
    # dois triangulos ligados pela ponte 2-3: articulacoes {2, 3}, unica ponte (2, 3)
    E = [(0, 1, 1), (1, 2, 1), (2, 0, 1), (2, 3, 1), (3, 4, 1), (4, 5, 1), (5, 3, 1)]
    art, pontes = tarjan_articulacoes_pontes(de_arestas(6, E)[0])
    assert set(art) == {2, 3}
    assert {frozenset(p) for p in pontes} == {frozenset((2, 3))}


def test_dfs_tempos():
    # parenteses: d[v] < f[v] e intervalos de pai contem os dos filhos
    adj, _ = grafo_aleatorio(60, 90, semente=7)
    d, f, pi, _ = dfs(adj)
    for v in range(60):
        assert d[v] < f[v]
        if pi[v] is not None:
            assert d[pi[v]] < d[v] < f[v] < f[pi[v]]


# ------------------------------------------- comparacao com NetworkX
def test_contra_networkx():
    for semente in range(20):
        n = 40 + semente * 5
        adj, peso = grafo_aleatorio(n, int(n * 1.3), semente)
        G = para_nx(adj, peso)

        dist_bfs, _ = bfs(adj, 0)
        ref = nx.single_source_shortest_path_length(G, 0)
        assert all((dist_bfs[v] == ref[v]) if v in ref else dist_bfs[v] == INF for v in range(n))

        _, _, _, arvores = dfs(adj)
        assert arvores == nx.number_connected_components(G)

        dist_dij, _ = dijkstra(adj, peso, 0)
        ref = nx.single_source_dijkstra_path_length(G, 0)
        assert all(math.isclose(dist_dij[v], ref[v]) if v in ref else dist_dij[v] == INF for v in range(n))

        ok, dist_bf, _, _ = bellman_ford(n, arcos_de(adj, peso), 0)
        assert ok and dist_bf == dist_dij

        D = floyd_warshall(adj, peso)
        ref = dict(nx.all_pairs_dijkstra_path_length(G))
        for i in range(n):
            for j in range(n):
                assert (D[i][j] == ref[i][j]) if j in ref[i] else D[i][j] == INF

        art, pontes = tarjan_articulacoes_pontes(adj)
        assert set(art) == set(nx.articulation_points(G))
        assert {frozenset(p) for p in pontes} == {frozenset(p) for p in nx.bridges(G)}

        ref_peso = nx.minimum_spanning_tree(G).size(weight="weight")
        assert math.isclose(prim(adj, peso)[1], ref_peso)
        assert math.isclose(kruskal(n, lista_arestas(adj, peso))[1], ref_peso)

        r = verificar_euleriano(adj)
        sem_isolados = G.subgraph([v for v in G if G.degree(v) > 0])
        assert r["circuito_euleriano"] == (sem_isolados.number_of_nodes() > 0 and nx.is_eulerian(sem_isolados))


# ------------------------------------------------------------ metricas
def test_metricas_contra_networkx():
    from metricas import (clusterizacao_bipartida_latapy, diametro_raio_exatos,
                          eh_bipartido, triangulos_e_clusterizacao)
    from networkx.algorithms import bipartite
    for semente in range(15):
        n = 60 + semente * 7
        adj, peso = grafo_aleatorio(n, int(n * 1.6), semente)
        G = para_nx(adj, peso)
        maior = max(nx.connected_components(G), key=len)
        H = nx.convert_node_labels_to_integers(G.subgraph(maior))
        adjH = [list(H.neighbors(v)) for v in range(H.number_of_nodes())]
        diam, raio, _ = diametro_raio_exatos(adjH)
        assert diam == nx.diameter(H) and raio == nx.radius(H)
        tri, c_medio, trans = triangulos_e_clusterizacao(adj)
        assert tri == sum(nx.triangles(G).values()) // 3
        assert math.isclose(c_medio, nx.average_clustering(G), abs_tol=1e-12)
        assert math.isclose(trans, nx.transitivity(G), abs_tol=1e-12)
        assert eh_bipartido(adj) == nx.is_bipartite(G)
    # grafo bipartido aleatorio: clusterizacao de Latapy
    B = bipartite.random_graph(30, 40, 0.1, seed=3)
    adjB = [list(B.neighbors(v)) for v in range(B.number_of_nodes())]
    ref = bipartite.latapy_clustering(B, mode="dot")
    vs = [v for v in B if any(True for w in B[v] for x in B[w] if x != v)]
    calc = clusterizacao_bipartida_latapy(adjB, vs)
    assert all(math.isclose(c, ref[v]) for c, v in zip(calc, vs))
    assert eh_bipartido(adjB)


# ------------------------------------------- Tarjan: componentes fortemente conexas
def test_tarjan_cfc():
    from algoritmos import tarjan_cfc
    # exemplo classico (CLRS fig. 22.9): a..h = 0..7; CFC {a,b,e}, {c,d}, {f,g}, {h}
    a, b, c, d, e, f, g, h = range(8)
    arcos = [(a, b), (b, c), (b, e), (b, f), (c, d), (c, g), (d, c), (d, h), (e, a), (e, f),
             (f, g), (g, f), (g, h), (h, h)]
    adj = [[] for _ in range(8)]
    for u, v in arcos:
        adj[u].append(v)
    comp, k = tarjan_cfc(adj)
    grupos = {frozenset(v for v in range(8) if comp[v] == i) for i in range(k)}
    assert grupos == {frozenset({a, b, e}), frozenset({c, d}), frozenset({f, g}), frozenset({h})}
    # grafos dirigidos aleatorios contra o NetworkX
    for semente in range(20):
        rng = random.Random(semente)
        n = 30 + 4 * semente
        adj = [[] for _ in range(n)]
        G = nx.DiGraph()
        G.add_nodes_from(range(n))
        for _ in range(int(1.5 * n)):
            u, v = rng.randrange(n), rng.randrange(n)
            adj[u].append(v)
            G.add_edge(u, v)
        comp, k = tarjan_cfc(adj)
        ref = {frozenset(c) for c in nx.strongly_connected_components(G)}
        assert k == len(ref)
        assert {frozenset(v for v in range(n) if comp[v] == i) for i in range(k)} == ref
    # grafo nao direcionado (dirigido simetrico): CFC = componentes conexas
    adj, _ = grafo_aleatorio(80, 70, semente=5)
    _, k = tarjan_cfc(adj)
    assert k == nx.number_connected_components(para_nx(adj, [[1] * len(x) for x in adj]))


# ------------------------------------------- diametro/raio em arvores e caminhos
def test_takes_kosters_arvores():
    from metricas import diametro_raio_exatos
    for semente in range(30):
        T = nx.random_labeled_tree(20 + semente, seed=semente)
        adj = [list(T.neighbors(v)) for v in range(T.number_of_nodes())]
        diam, raio, _ = diametro_raio_exatos(adj)
        assert diam == nx.diameter(T) and raio == nx.radius(T)
    P = [[1]] + [[i - 1, i + 1] for i in range(1, 9)] + [[8]]  # caminho com 10 vertices
    assert diametro_raio_exatos(P)[:2] == (9, 5)


# ------------------------------------------- geradores da Parte III
def test_geradores_parte3():
    from collections import Counter

    from parte3_analise import bipartido_trocas, watts_strogatz
    # Watts-Strogatz: exatamente n*k/2 arestas, sem lacos nem repeticoes
    for p in (0.0, 0.1, 0.5):
        adj = watts_strogatz(300, 10, p, semente=1)
        pares = [frozenset((u, v)) for u in range(300) for v in adj[u]]
        assert len(pares) == 2 * 1500 and all(len(x) == 2 for x in pares)
        assert all(c == 2 for c in Counter(pares).values())
    # trocas bipartidas: mesmos graus de cada vertice, grafo simples e bipartido
    from networkx.algorithms import bipartite
    B = bipartite.random_graph(40, 60, 0.15, seed=4)
    adj = [list(B.neighbors(v)) for v in range(100)]
    novo, aceitas, restantes = bipartido_trocas(adj, 40, 20, semente=2)
    assert aceitas > 0 and restantes < 0.5
    assert all(len(novo[v]) == len(adj[v]) for v in range(100))
    assert all(len(set(novo[v])) == len(novo[v]) for v in range(100))
    assert all((u < 40) != (v < 40) for u in range(100) for v in novo[u])


# ------------------------------------------- lei de potencia e IC
def test_lei_potencia_exata_contra_powerlaw():
    import numpy as np
    import powerlaw
    from metricas import _ajuste_kmin, _amostra_lei_potencia, _preparar
    x = _amostra_lei_potencia(np.random.default_rng(0), 5000, 2.3, 4)
    r = _ajuste_kmin(_preparar(x), 4)
    ref = powerlaw.Fit(x, discrete=True, xmin=4, verbose=False).power_law
    assert abs(r["gamma"] - ref.alpha) < 1e-3 and abs(r["ks"] - ref.D) < 1e-3
    assert abs(r["gamma"] - 2.3) < 4 * r["erro_padrao"]


def test_intervalo_de_confianca():
    from scipy import stats

    from estatistica import resumo
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]                 # n < 30 -> t-Student com 4 g.l.
    r = resumo(xs)
    assert r["distribuicao"] == "t" and math.isclose(r["valor_critico"], stats.t.ppf(0.975, 4))
    assert math.isclose(r["ic_sup"] - r["media"], stats.t.ppf(0.975, 4) * math.sqrt(2.5) / math.sqrt(5))
    r = resumo([float(i % 7) for i in range(40)])  # n >= 30 -> Normal
    assert r["distribuicao"] == "Z" and math.isclose(r["valor_critico"], stats.norm.ppf(0.975))


if __name__ == "__main__":
    testes = [(nome, fn) for nome, fn in sorted(globals().items()) if nome.startswith("test_")]
    for nome, fn in testes:
        fn()
        print(f"ok  {nome}")
    print(f"{len(testes)} testes passaram")
