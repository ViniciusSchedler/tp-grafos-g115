"""
Parte I - Analise estrutural obrigatoria. Gera results/parte1.json, tabelas e figuras.
(O comprimento medio exato vem de distancias_exatas.py, que roda separadamente.)

Uso: python src/parte1_estrutural.py            (calcula tudo)
     python src/parte1_estrutural.py figuras    (so refaz as figuras a partir de parte1.json)
"""
import json
import os
import sys
import time
from collections import Counter

import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo import COLUNA, COR, PAGINA, plt, salvar_figura  # noqa: E402
from grafo import (RAIZ, amostra_conexa, carregar_grafo, componentes_conexas,  # noqa: E402
                   maior_componente, num_arestas)
from metricas import (densidade, diametro_raio_exatos, distribuicao_graus,  # noqa: E402
                      eh_bipartido, resumo_graus, triangulos_e_clusterizacao)

FIG = os.path.join(RAIZ, "results", "figures")
SEMENTE = 2025


def main():
    os.makedirs(FIG, exist_ok=True)
    r = {}
    adj, peso, U = carregar_grafo()
    n, m = len(adj), num_arestas(adj)
    usuarios, cervejas = range(U), range(U, n)
    r["vertices"] = n
    r["usuarios"] = U
    r["cervejas"] = n - U
    r["arestas"] = m
    r["graus_todos"] = resumo_graus(adj)
    r["graus_usuarios"] = resumo_graus(adj, usuarios)
    r["graus_cervejas"] = resumo_graus(adj, cervejas)
    r["densidade"] = densidade(n, m)
    r["densidade_bipartida_E_sobre_UxB"] = m / (U * (n - U))
    r["bipartido_verificado_por_bfs"] = eh_bipartido(adj)

    comp, tamanhos = componentes_conexas(adj)
    r["num_componentes"] = len(tamanhos)
    r["tamanhos_componentes_freq"] = {str(k): v for k, v in sorted(Counter(tamanhos).items())}
    # composicao (usuarios, cervejas) de cada componente pequena
    pequenas = Counter()
    for v in range(n):
        pequenas[(comp[v], v < U)] += 1
    r["componentes_detalhe"] = sorted(
        [{"tamanho": tamanhos[c], "usuarios": pequenas[(c, True)], "cervejas": pequenas[(c, False)]}
         for c in range(len(tamanhos))], key=lambda x: -x["tamanho"])

    t = time.perf_counter()
    tri, c_medio, trans = triangulos_e_clusterizacao(adj)
    r["triangulos"] = tri
    r["clusterizacao_media"] = c_medio
    r["transitividade"] = trans
    r["tempo_triangulos_s"] = time.perf_counter() - t

    adj_mcc, peso_mcc, vert_mcc = maior_componente(adj, peso)
    r["mcc_vertices"] = len(adj_mcc)
    r["mcc_arestas"] = num_arestas(adj_mcc)
    r["mcc_usuarios"] = sum(1 for v in vert_mcc if v < U)
    t = time.perf_counter()
    diam, raio, nbfs = diametro_raio_exatos(adj_mcc)
    r["mcc_diametro"] = diam
    r["mcc_raio"] = raio
    r["bfs_usadas_limitantes"] = nbfs
    r["tempo_diametro_raio_s"] = time.perf_counter() - t

    # distribuicao de graus
    dist = {"todos": distribuicao_graus(adj), "usuarios": distribuicao_graus(adj, usuarios),
            "cervejas": distribuicao_graus(adj, cervejas)}
    r["distribuicao_graus"] = {k: {str(g): p for g, p in d.items()} for k, d in dist.items()}
    figura_graus(dist)
    r["visualizacao"] = figura_visualizacao(adj_mcc, peso_mcc, vert_mcc, U)

    with open(os.path.join(RAIZ, "results", "parte1.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in r.items() if k not in ("distribuicao_graus", "componentes_detalhe")},
                     indent=2, ensure_ascii=False))


ROTULO = {"usuarios": "usuários", "cervejas": "cervejas", "todos": "todos"}


def figura_graus(dist):
    """P(k) e CCDF P(K >= k) em escala log-log (dist[grupo][k] = P(k))."""
    fig, eixos = plt.subplots(1, 2, figsize=(PAGINA, 2.3))
    for nome in ("usuarios", "cervejas", "todos"):
        d = {int(k): p for k, p in dist[nome].items()}
        ks = sorted(d)
        eixos[0].loglog(ks, [d[k] for k in ks], "o" if nome != "todos" else ".", ms=2 if nome != "todos" else 2.5,
                        mfc="none" if nome != "todos" else None, mew=0.6, color=COR[nome], label=ROTULO[nome])
        ccdf, acc = [], 1.0
        for k in ks:
            ccdf.append(acc)
            acc -= d[k]
        eixos[1].loglog(ks, ccdf, "-", color=COR[nome], lw=1.5 if nome == "todos" else 1.1, label=ROTULO[nome])
    eixos[0].set(xlabel="grau $k$", ylabel="$P(k)$", title="Distribuição de graus")
    eixos[1].set(xlabel="grau $k$", ylabel="$P(K \\geq k)$", title="Distribuição acumulada complementar (CCDF)")
    for e in eixos:
        e.legend(loc="lower left")
        e.grid(which="major")
    salvar_figura(fig, os.path.join(FIG, "distribuicao_graus"))


def figura_visualizacao(adj_mcc, peso_mcc, vert_mcc, U):
    """Visualizacao reduzida: 250 vertices em ordem BFS a partir de um vertice sorteado."""
    a_viz, _, ordem = amostra_conexa(adj_mcc, peso_mcc, 250, SEMENTE)
    eh_usuario = [vert_mcc[v] < U for v in ordem]
    G = nx.Graph()
    for u, viz in enumerate(a_viz):
        for v in viz:
            G.add_edge(u, v)
    pos = nx.spring_layout(G, seed=SEMENTE, k=0.15)
    fig, ax = plt.subplots(figsize=(COLUNA, COLUNA * 0.85))
    nx.draw_networkx_edges(G, pos, ax=ax, width=.35, alpha=.45, edge_color="0.4")
    cores = [COR["usuarios"] if eh_usuario[v] else COR["cervejas"] for v in G]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[4 + 1.5 * G.degree(v) for v in G],
                           node_color=cores, linewidths=0)
    ax.scatter([], [], s=12, color=COR["usuarios"], label="usuário")
    ax.scatter([], [], s=12, color=COR["cervejas"], label="cerveja")
    ax.legend(loc="lower right", handletextpad=0.2)
    ax.set_axis_off()
    salvar_figura(fig, os.path.join(FIG, "visualizacao_amostra"))
    return {"vertices": G.number_of_nodes(), "arestas": G.number_of_edges(), "semente": SEMENTE,
            "usuarios": sum(eh_usuario), "cervejas": len(eh_usuario) - sum(eh_usuario)}


def figuras():
    with open(os.path.join(RAIZ, "results", "parte1.json"), encoding="utf-8") as f:
        r = json.load(f)
    figura_graus(r["distribuicao_graus"])
    adj, peso, U = carregar_grafo()
    adj_mcc, peso_mcc, vert_mcc = maior_componente(adj, peso)
    assert figura_visualizacao(adj_mcc, peso_mcc, vert_mcc, U) == r["visualizacao"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "figuras":
        figuras()
    else:
        main()
