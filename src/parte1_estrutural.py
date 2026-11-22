"""
Parte I - Analise estrutural obrigatoria. Gera results/parte1.json, tabelas e figuras.
(O comprimento medio exato vem de distancias_exatas.py, que roda separadamente.)
"""
import json
import os
import sys
import time
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
    fig, eixos = plt.subplots(1, 2, figsize=(9, 3.4))
    for nome, cor in (("usuarios", "tab:blue"), ("cervejas", "tab:orange"), ("todos", "black")):
        d = dist[nome]
        rotulo = {"usuarios": "usuários", "cervejas": "cervejas", "todos": "todos"}[nome]
        eixos[0].loglog(list(d), list(d.values()), ".", ms=3, color=cor, label=rotulo, alpha=.7)
        ks = sorted(d)
        ccdf, acc = [], 1.0
        for k in ks:
            ccdf.append(acc)
            acc -= d[k]
        eixos[1].loglog(ks, ccdf, "-", color=cor, label=rotulo)
    eixos[0].set(xlabel="grau k", ylabel="P(k)", title="Distribuição de graus")
    eixos[1].set(xlabel="grau k", ylabel="P(K ≥ k)", title="CCDF")
    for e in eixos:
        e.legend(fontsize=8)
        e.grid(alpha=.3, which="both", lw=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "distribuicao_graus.pdf"))
    fig.savefig(os.path.join(FIG, "distribuicao_graus.png"), dpi=150)
    plt.close(fig)

    # visualizacao reduzida: 250 vertices em ordem BFS a partir de um vertice sorteado
    a_viz, _, ordem = amostra_conexa(adj_mcc, peso_mcc, 250, SEMENTE)
    eh_usuario = [vert_mcc[v] < U for v in ordem]
    G = nx.Graph()
    for u, viz in enumerate(a_viz):
        for v in viz:
            G.add_edge(u, v)
    pos = nx.spring_layout(G, seed=SEMENTE, k=0.15)
    fig, ax = plt.subplots(figsize=(5, 5))
    nx.draw_networkx_edges(G, pos, ax=ax, width=.3, alpha=.4)
    cores = ["tab:blue" if eh_usuario[v] else "tab:orange" for v in G]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=[8 + 2 * G.degree(v) for v in G],
                           node_color=cores, linewidths=0)
    ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "visualizacao_amostra.pdf"))
    fig.savefig(os.path.join(FIG, "visualizacao_amostra.png"), dpi=150)
    plt.close(fig)
    r["visualizacao"] = {"vertices": G.number_of_nodes(), "arestas": G.number_of_edges(),
                         "semente": SEMENTE, "usuarios": sum(eh_usuario),
                         "cervejas": len(eh_usuario) - sum(eh_usuario)}

    with open(os.path.join(RAIZ, "results", "parte1.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in r.items() if k not in ("distribuicao_graus", "componentes_detalhe")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
