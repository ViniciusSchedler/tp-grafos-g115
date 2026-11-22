"""
Parte II - execucao dos algoritmos no grafo e medicao de tempo real.

Experimento A (grafo real): todos os algoritmos viaveis na maior componente conexa (MCC).
Experimento B (escalabilidade): subgrafos conexos de tamanho crescente (amostra BFS),
  uma amostra diferente por repeticao, para comparar o crescimento observado com a
  complexidade teorica.
Repeticoes: R = 30 (IC pela Normal) ou R = 10 (IC pela t-Student) nos algoritmos caros.
"""
import csv
import gc
import json
import math
import os
import platform
import random
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algoritmos import (INF, arcos_de, bellman_ford, bfs, dfs, dijkstra,  # noqa: E402
                        floyd_warshall, kruskal, prim, tarjan_articulacoes_pontes,
                        verificar_euleriano)
from estatistica import resumo  # noqa: E402
from grafo import (RAIZ, amostra_conexa, carregar_grafo, lista_arestas,  # noqa: E402
                   maior_componente, num_arestas)

SEMENTE = 2025
TAB = os.path.join(RAIZ, "results", "tables")
FIG = os.path.join(RAIZ, "results", "figures")


def cronometrar(funcao):
    gc.collect()
    gc.disable()  # evita pausas do coletor de lixo dentro da medicao
    t = time.perf_counter()
    saida = funcao()
    dt = time.perf_counter() - t
    gc.enable()
    return dt, saida


def executar(nome, adj, peso, rng):
    """Roda um algoritmo uma vez (preparacao de entrada fora do cronometro)."""
    n = len(adj)
    if nome == "BFS":
        s = rng.randrange(n)
        return cronometrar(lambda: bfs(adj, s))
    if nome == "DFS":
        return cronometrar(lambda: dfs(adj))
    if nome == "Euler":
        return cronometrar(lambda: verificar_euleriano(adj))
    if nome == "Dijkstra":
        s = rng.randrange(n)
        return cronometrar(lambda: dijkstra(adj, peso, s))
    if nome == "Tarjan":
        return cronometrar(lambda: tarjan_articulacoes_pontes(adj))
    if nome == "Prim":
        return cronometrar(lambda: prim(adj, peso))
    if nome == "Kruskal":
        arestas = lista_arestas(adj, peso)
        return cronometrar(lambda: kruskal(n, arestas))
    if nome in ("Bellman-Ford", "Bellman-Ford (parada antecipada)"):
        arcos = arcos_de(adj, peso)
        s = rng.randrange(n)
        cedo = nome != "Bellman-Ford"
        return cronometrar(lambda: bellman_ford(n, arcos, s, parar_cedo=cedo))
    if nome == "Floyd-Warshall":
        return cronometrar(lambda: floyd_warshall(adj, peso))
    raise ValueError(nome)


# custo teorico f(V, E) usado para a razao tempo / f
CUSTO = {
    "BFS": lambda V, E: V + E, "DFS": lambda V, E: V + E, "Euler": lambda V, E: V + E,
    "Tarjan": lambda V, E: V + E,
    "Dijkstra": lambda V, E: (V + E) * math.log2(V), "Prim": lambda V, E: E * math.log2(V),
    "Kruskal": lambda V, E: E * math.log2(V), "Bellman-Ford": lambda V, E: V * 2 * E,
    "Floyd-Warshall": lambda V, E: V ** 3,
}
COMPLEXIDADE = {
    "BFS": "O(V+E)", "DFS": "O(V+E)", "Euler": "O(V+E)", "Tarjan": "O(V+E)",
    "Dijkstra": "O((V+E) log V)", "Prim": "O(E log V)", "Kruskal": "O(E log V)",
    "Bellman-Ford": "O(VE)", "Floyd-Warshall": "O(V^3)",
}
LINEARES = ["BFS", "DFS", "Euler", "Tarjan", "Dijkstra", "Prim", "Kruskal"]


def main():
    os.makedirs(TAB, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    adj, peso, U = carregar_grafo()
    adj_mcc, peso_mcc, _ = maior_componente(adj, peso)
    V_mcc, E_mcc = len(adj_mcc), num_arestas(adj_mcc)
    linhas = []  # (experimento, algoritmo, tamanho_alvo, rep, V, E, tempo)
    t0 = time.perf_counter()

    # ---------- resultados dos algoritmos na MCC (uma execucao, para o relatorio)
    res = {"V_mcc": V_mcc, "E_mcc": E_mcc}
    rng = random.Random(SEMENTE)
    s = rng.randrange(V_mcc)
    d_bfs, _ = bfs(adj_mcc, s)
    res["bfs_origem"] = s
    res["bfs_excentricidade_origem"] = max(d_bfs)
    res["bfs_vertices_por_nivel"] = [d_bfs.count(k) for k in range(max(d_bfs) + 1)]
    _, _, _, arvores = dfs(adj)
    res["dfs_arvores_no_grafo_completo"] = arvores
    res["euler_grafo_completo"] = verificar_euleriano(adj)
    res["euler_mcc"] = verificar_euleriano(adj_mcc)
    d_dij, _ = dijkstra(adj_mcc, peso_mcc, s)
    res["dijkstra_origem"] = s
    res["dijkstra_dist_max"] = max(d_dij)
    res["dijkstra_dist_media"] = sum(d_dij) / (V_mcc - 1)
    ok, d_bf, _, passadas = bellman_ford(V_mcc, arcos_de(adj_mcc, peso_mcc), s, parar_cedo=True)
    res["bellman_ford_sem_ciclo_negativo"] = ok
    res["bellman_ford_igual_dijkstra"] = all(abs(a - b) < 1e-9 for a, b in zip(d_bf, d_dij))
    res["bellman_ford_passadas_ate_estabilizar"] = passadas
    art, pontes = tarjan_articulacoes_pontes(adj_mcc)
    res["tarjan_articulacoes"] = len(art)
    res["tarjan_pontes"] = len(pontes)
    res["tarjan_pontes_com_folha"] = sum(1 for u, v in pontes if len(adj_mcc[u]) == 1 or len(adj_mcc[v]) == 1)
    ap, wp = prim(adj_mcc, peso_mcc)
    ak, wk = kruskal(V_mcc, lista_arestas(adj_mcc, peso_mcc))
    res["agm_peso_prim"] = wp
    res["agm_peso_kruskal"] = wk
    res["agm_arestas"] = [len(ap), len(ak)]
    with open(os.path.join(RAIZ, "results", "parte2_resultados.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "bfs_vertices_por_nivel"}, indent=2), flush=True)

    # ---------- Experimento A: MCC inteira
    for nome in LINEARES:
        rng = random.Random(SEMENTE)
        for rep in range(30):
            dt, _ = executar(nome, adj_mcc, peso_mcc, rng)
            linhas.append(("A", nome, V_mcc, rep, V_mcc, E_mcc, dt))
        print(f"A {nome} {time.perf_counter() - t0:.0f}s", flush=True)
    rng = random.Random(SEMENTE)
    for rep in range(10):
        dt, _ = executar("Bellman-Ford (parada antecipada)", adj_mcc, peso_mcc, rng)
        linhas.append(("A", "Bellman-Ford (parada antecipada)", V_mcc, rep, V_mcc, E_mcc, dt))
    print(f"A Bellman-Ford {time.perf_counter() - t0:.0f}s", flush=True)

    # ---------- Experimento B: escalabilidade em amostras conexas
    planos = [(LINEARES, [6250, 12500, 25000, 50000], 30),
              (["Bellman-Ford"], [125, 250, 500, 1000], 10),
              (["Floyd-Warshall"], [50, 100, 200, 400], 10)]
    for algoritmos, tamanhos, R in planos:
        for k in tamanhos:
            for rep in range(R):
                a, p, _ = amostra_conexa(adj_mcc, peso_mcc, k, SEMENTE + 1000 * k + rep)
                V, E = len(a), num_arestas(a)
                rng = random.Random(SEMENTE + rep)
                for nome in algoritmos:
                    dt, _ = executar(nome, a, p, rng)
                    linhas.append(("B", nome, k, rep, V, E, dt))
            print(f"B {algoritmos[0]}.. k={k} {time.perf_counter() - t0:.0f}s", flush=True)

    with open(os.path.join(TAB, "desempenho_bruto.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["experimento", "algoritmo", "tamanho_alvo", "rep", "V", "E", "tempo_s"])
        w.writerows(linhas)

    # ---------- resumo: media, dp, IC 95% por (algoritmo, tamanho)
    grupos = {}
    for exp, nome, k, rep, V, E, dt in linhas:
        grupos.setdefault((exp, nome, k), []).append((V, E, dt))
    resumo_linhas = []
    for (exp, nome, k), xs in grupos.items():
        tempos = [x[2] for x in xs]
        Vm = sum(x[0] for x in xs) / len(xs)
        Em = sum(x[1] for x in xs) / len(xs)
        r = resumo(tempos)
        base = nome.split(" (")[0]
        r.update({"experimento": exp, "algoritmo": nome, "tamanho_alvo": k, "V_medio": Vm, "E_medio": Em,
                  "complexidade": COMPLEXIDADE[base],
                  "tempo_sobre_custo_ns": 1e9 * r["media"] / CUSTO[base](Vm, Em)})
        resumo_linhas.append(r)
    campos = ["experimento", "algoritmo", "complexidade", "tamanho_alvo", "V_medio", "E_medio", "n", "media",
              "desvio_padrao", "ic_inf", "ic_sup", "distribuicao", "valor_critico", "tempo_sobre_custo_ns"]
    with open(os.path.join(TAB, "desempenho_resumo.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in resumo_linhas:
            w.writerow({c: r[c] for c in campos})

    # expoente empirico: inclinacao de log(tempo) x log(custo teorico) (esperado ~ 1)
    expoentes = {}
    for nome in LINEARES + ["Bellman-Ford", "Floyd-Warshall"]:
        pts = [(r["V_medio"], r["E_medio"], r["media"]) for r in resumo_linhas
               if r["algoritmo"] == nome]  # inclui a MCC (experimento A) nos quase lineares
        xs = [math.log(CUSTO[nome](V, E)) for V, E, _ in pts]
        ys = [math.log(t) for _, _, t in pts]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        xv = [math.log(V) for V, _, _ in pts]
        mv = sum(xv) / len(xv)
        bv = sum((x - mv) * (y - my) for x, y in zip(xv, ys)) / sum((x - mv) ** 2 for x in xv)
        expoentes[nome] = {"inclinacao_vs_custo_teorico": b, "inclinacao_vs_V": bv, "pontos": len(pts)}

    ambiente = {"python": sys.version, "plataforma": platform.platform(), "processador": platform.processor(),
                "tempo_total_s": time.perf_counter() - t0}
    with open(os.path.join(TAB, "desempenho_expoentes.json"), "w", encoding="utf-8") as f:
        json.dump({"expoentes": expoentes, "ambiente": ambiente}, f, indent=2, ensure_ascii=False)

    # ---------- figura: tempo medio x V (log-log) com IC 95%
    fig, eixos = plt.subplots(1, 2, figsize=(9, 3.6))
    for nome in LINEARES:
        rs = sorted([r for r in resumo_linhas if r["algoritmo"] == nome], key=lambda r: r["V_medio"])
        eixos[0].errorbar([r["V_medio"] for r in rs], [r["media"] for r in rs],
                          yerr=[[r["media"] - r["ic_inf"] for r in rs], [r["ic_sup"] - r["media"] for r in rs]],
                          marker="o", ms=3, capsize=2, label=nome)
    for nome in ["Bellman-Ford", "Floyd-Warshall"]:
        rs = sorted([r for r in resumo_linhas if r["algoritmo"] == nome], key=lambda r: r["V_medio"])
        eixos[1].errorbar([r["V_medio"] for r in rs], [r["media"] for r in rs],
                          yerr=[[r["media"] - r["ic_inf"] for r in rs], [r["ic_sup"] - r["media"] for r in rs]],
                          marker="o", ms=3, capsize=2, label=nome)
    for e in eixos:
        e.set_xscale("log")
        e.set_yscale("log")
        e.set_xlabel("|V| do subgrafo")
        e.set_ylabel("tempo médio (s)")
        e.grid(alpha=.3, which="both", lw=.3)
        e.legend(fontsize=7)
    eixos[0].set_title("Algoritmos quase lineares (R = 30)")
    eixos[1].set_title("Algoritmos caros (R = 10)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "desempenho.pdf"))
    fig.savefig(os.path.join(FIG, "desempenho.png"), dpi=150)
    print(json.dumps(expoentes, indent=2))
    print(f"total {time.perf_counter() - t0:.0f}s")


if __name__ == "__main__":
    main()
