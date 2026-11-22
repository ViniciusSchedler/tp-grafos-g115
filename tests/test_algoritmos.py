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


if __name__ == "__main__":
    testes = [(nome, fn) for nome, fn in sorted(globals().items()) if nome.startswith("test_")]
    for nome, fn in testes:
        fn()
        print(f"ok  {nome}")
    print(f"{len(testes)} testes passaram")
