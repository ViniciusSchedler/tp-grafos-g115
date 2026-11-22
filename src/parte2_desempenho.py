"""
Parte II - execucao dos algoritmos no grafo e medicao de tempo real.

Experimento A (grafo real): todos os algoritmos viaveis na maior componente conexa (MCC).
Experimento B (escalabilidade): subgrafos conexos de tamanho crescente (amostra BFS),
  uma amostra diferente por repeticao, para comparar o crescimento observado com a
  complexidade teorica.
Repeticoes: R = 30 (IC pela Normal) ou R = 10 (IC pela t-Student) nos algoritmos caros.

Uso: python src/parte2_desempenho.py            (experimento completo)
     python src/parte2_desempenho.py extra      (so Tarjan-CFC e Bellman-Ford com parada
                                                 antecipada; junta ao CSV existente)
     python src/parte2_desempenho.py figura     (refaz resumo, inclinacoes e figura)
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algoritmos import (arcos_de, bellman_ford, bfs, dfs, dijkstra,  # noqa: E402
                        floyd_warshall, kruskal, prim, tarjan_articulacoes_pontes,
                        tarjan_cfc, verificar_euleriano)
from estatistica import resumo  # noqa: E402
from estilo import PAGINA, plt, salvar_figura  # noqa: E402
from grafo import (RAIZ, amostra_conexa, carregar_grafo, lista_arestas,  # noqa: E402
                   maior_componente, num_arestas)

SEMENTE = 2025
TAB = os.path.join(RAIZ, "results", "tables")
FIG = os.path.join(RAIZ, "results", "figures")
CSV_BRUTO = os.path.join(TAB, "desempenho_bruto.csv")
ARQ_RES = os.path.join(RAIZ, "results", "parte2_resultados.json")


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
    if nome == "Tarjan-CFC":
        return cronometrar(lambda: tarjan_cfc(adj))
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
    "Tarjan": lambda V, E: V + E, "Tarjan-CFC": lambda V, E: V + E,
    "Dijkstra": lambda V, E: (V + E) * math.log2(V), "Prim": lambda V, E: E * math.log2(V),
    "Kruskal": lambda V, E: E * math.log2(V), "Bellman-Ford": lambda V, E: V * 2 * E,
    "Floyd-Warshall": lambda V, E: V ** 3,
}
COMPLEXIDADE = {
    "BFS": "O(V+E)", "DFS": "O(V+E)", "Euler": "O(V+E)", "Tarjan": "O(V+E)", "Tarjan-CFC": "O(V+E)",
    "Dijkstra": "O((V+E) log V)", "Prim": "O(E log V)", "Kruskal": "O(E log V)",
    "Bellman-Ford": "O(VE)", "Floyd-Warshall": "O(V^3)",
}
LINEARES = ["BFS", "DFS", "Euler", "Tarjan", "Tarjan-CFC", "Dijkstra", "Prim", "Kruskal"]
ORDEM = LINEARES + ["Bellman-Ford", "Floyd-Warshall"]


def experimento_B(adj_mcc, peso_mcc, planos, linhas, t0):
    for algoritmos, tamanhos, R in planos:
        for k in tamanhos:
            for rep in range(R):
                # mesma amostra para todos os algoritmos (a semente depende so de k e rep)
                a, p, _ = amostra_conexa(adj_mcc, peso_mcc, k, SEMENTE + 1000 * k + rep)
                V, E = len(a), num_arestas(a)
                rng = random.Random(SEMENTE + rep)
                for nome in algoritmos:
                    dt, _ = executar(nome, a, p, rng)
                    linhas.append(("B", nome, k, rep, V, E, dt))
            print(f"B {algoritmos[0]}.. k={k} {time.perf_counter() - t0:.0f}s", flush=True)


def resultados_mcc(adj, adj_mcc, peso_mcc):
    """Resultado de cada algoritmo na MCC (uma execucao, para o relatorio)."""
    V_mcc = len(adj_mcc)
    res = {"V_mcc": V_mcc, "E_mcc": num_arestas(adj_mcc)}
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
    res["bellman_ford_passadas_ate_estabilizar"] = passadas  # inclui a ultima passada, sem alteracao
    art, pontes = tarjan_articulacoes_pontes(adj_mcc)
    res["tarjan_articulacoes"] = len(art)
    res["tarjan_pontes"] = len(pontes)
    res["tarjan_pontes_com_folha"] = sum(1 for u, v in pontes if len(adj_mcc[u]) == 1 or len(adj_mcc[v]) == 1)
    res["tarjan_cfc_grafo_completo"] = tarjan_cfc(adj)[1]
    ap, wp = prim(adj_mcc, peso_mcc)
    ak, wk = kruskal(V_mcc, lista_arestas(adj_mcc, peso_mcc))
    res["agm_peso_prim"] = wp
    res["agm_peso_kruskal"] = wk
    res["agm_arestas"] = [len(ap), len(ak)]
    return res


def bellman_ford_passadas(adj_mcc, peso_mcc, R=10):
    """Bellman-Ford com parada antecipada na MCC (R origens sorteadas), guardando o numero
    de passadas. Tempo por passada = tempo / (passadas + 1), pois a verificacao final de
    ciclo negativo percorre os arcos mais uma vez. Serve para estimar a versao sem parada
    antecipada: (|V|-1) passadas + verificacao = |V| percursos da lista de arcos."""
    V = len(adj_mcc)
    arcos = arcos_de(adj_mcc, peso_mcc)
    rng = random.Random(SEMENTE)
    linhas, por_passada, passadas = [], [], []
    for rep in range(R):
        s = rng.randrange(V)
        dt, saida = cronometrar(lambda: bellman_ford(V, arcos, s, parar_cedo=True))
        linhas.append(("A", "Bellman-Ford (parada antecipada)", V, rep, V, num_arestas(adj_mcc), dt))
        passadas.append(saida[3])
        por_passada.append(dt / (saida[3] + 1))
    return linhas, {"passadas_por_origem": passadas, "tempo_por_passada_s": resumo(por_passada),
                    "estimativa_sem_parada_s": resumo([x * V for x in por_passada])}


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "completo"
    os.makedirs(TAB, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    if modo == "figura":
        resumir(ler_bruto(), None)
        return
    adj, peso, U = carregar_grafo()
    adj_mcc, peso_mcc, _ = maior_componente(adj, peso)
    V_mcc, E_mcc = len(adj_mcc), num_arestas(adj_mcc)
    t0 = time.perf_counter()
    res = resultados_mcc(adj, adj_mcc, peso_mcc)

    if modo == "extra":
        # acrescenta Tarjan-CFC (A e B, com as mesmas amostras) e refaz o Bellman-Ford com
        # parada antecipada guardando as passadas; demais linhas do CSV sao mantidas
        linhas = [x for x in ler_bruto() if x[1] not in ("Tarjan-CFC", "Bellman-Ford (parada antecipada)")]
        rng = random.Random(SEMENTE)
        for rep in range(30):
            dt, _ = executar("Tarjan-CFC", adj_mcc, peso_mcc, rng)
            linhas.append(("A", "Tarjan-CFC", V_mcc, rep, V_mcc, E_mcc, dt))
        experimento_B(adj_mcc, peso_mcc, [(["Tarjan-CFC"], [6250, 12500, 25000, 50000], 30)], linhas, t0)
        novas, res["bellman_ford_mcc"] = bellman_ford_passadas(adj_mcc, peso_mcc)
        linhas += novas
        with open(os.path.join(TAB, "desempenho_expoentes.json"), encoding="utf-8") as f:
            amb = json.load(f)["ambiente"]
        amb["tempo_extra_s"] = time.perf_counter() - t0
    else:
        linhas = []  # (experimento, algoritmo, tamanho_alvo, rep, V, E, tempo)
        for nome in LINEARES:
            rng = random.Random(SEMENTE)
            for rep in range(30):
                dt, _ = executar(nome, adj_mcc, peso_mcc, rng)
                linhas.append(("A", nome, V_mcc, rep, V_mcc, E_mcc, dt))
            print(f"A {nome} {time.perf_counter() - t0:.0f}s", flush=True)
        novas, res["bellman_ford_mcc"] = bellman_ford_passadas(adj_mcc, peso_mcc)
        linhas += novas
        experimento_B(adj_mcc, peso_mcc, [(LINEARES, [6250, 12500, 25000, 50000], 30),
                                          (["Bellman-Ford"], [125, 250, 500, 1000], 10),
                                          (["Floyd-Warshall"], [50, 100, 200, 400], 10)], linhas, t0)
        amb = {"python": sys.version, "plataforma": platform.platform(), "processador": platform.processor(),
               "tempo_total_s": time.perf_counter() - t0}
    with open(ARQ_RES, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    with open(CSV_BRUTO, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["experimento", "algoritmo", "tamanho_alvo", "rep", "V", "E", "tempo_s"])
        w.writerows(linhas)
    resumir(linhas, amb)


def ler_bruto():
    with open(CSV_BRUTO, encoding="utf-8") as f:
        return [(r["experimento"], r["algoritmo"], int(r["tamanho_alvo"]), int(r["rep"]), int(r["V"]),
                 int(r["E"]), float(r["tempo_s"])) for r in csv.DictReader(f)]


def inclinacao(xs, ys):
    """Minimos quadrados: inclinacao da reta y = a + b x."""
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def resumir(linhas, amb):
    """Media, dp e IC 95% por (algoritmo, tamanho); inclinacoes log-log; figura."""
    grupos = {}
    for exp, nome, k, rep, V, E, dt in linhas:
        grupos.setdefault((exp, nome, k), []).append((V, E, dt))
    chave = lambda g: (g[0], ORDEM.index(g[1].split(" (")[0]), g[1], g[2])  # noqa: E731
    resumo_linhas = []
    for (exp, nome, k) in sorted(grupos, key=chave):
        xs = grupos[(exp, nome, k)]
        Vm = sum(x[0] for x in xs) / len(xs)
        Em = sum(x[1] for x in xs) / len(xs)
        r = resumo([x[2] for x in xs])
        base = nome.split(" (")[0]
        r.update({"experimento": exp, "algoritmo": nome, "tamanho_alvo": k, "V_medio": Vm, "E_medio": Em,
                  "E_min": min(x[1] for x in xs), "E_max": max(x[1] for x in xs),
                  "complexidade": COMPLEXIDADE[base],
                  "tempo_sobre_custo_ns": 1e9 * r["media"] / CUSTO[base](Vm, Em)})
        resumo_linhas.append(r)
    campos = ["experimento", "algoritmo", "complexidade", "tamanho_alvo", "V_medio", "E_medio", "E_min", "E_max",
              "n", "media", "desvio_padrao", "ic_inf", "ic_sup", "distribuicao", "valor_critico",
              "tempo_sobre_custo_ns"]
    with open(os.path.join(TAB, "desempenho_resumo.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        for r in resumo_linhas:
            w.writerow({c: r[c] for c in campos})

    # inclinacao de log(tempo) x log(custo teorico), esperada ~ 1:
    #  - sobre as medias de cada tamanho (inclui a MCC nos quase lineares);
    #  - sobre cada repeticao do experimento B (com |V| e |E| reais de cada amostra).
    expoentes = {}
    for nome in ORDEM:
        pts = [(r["V_medio"], r["E_medio"], r["media"]) for r in resumo_linhas if r["algoritmo"] == nome]
        if not pts:  # algoritmo ainda nao medido
            continue
        ys =[math.log(t) for _, _, t in pts]
        reps = [(V, E, t) for e, a, _, _, V, E, t in linhas if a == nome and e == "B"]
        expoentes[nome] = {
            "inclinacao_vs_custo_teorico": inclinacao([math.log(CUSTO[nome](V, E)) for V, E, _ in pts], ys),
            "inclinacao_vs_V": inclinacao([math.log(V) for V, _, _ in pts], ys),
            "inclinacao_por_repeticao": inclinacao([math.log(CUSTO[nome](V, E)) for V, E, _ in reps],
                                                   [math.log(t) for _, _, t in reps]),
            "pontos": len(pts), "repeticoes": len(reps)}
    arq = os.path.join(TAB, "desempenho_expoentes.json")
    if amb is None:
        with open(arq, encoding="utf-8") as f:
            amb = json.load(f)["ambiente"]
    with open(arq, "w", encoding="utf-8") as f:
        json.dump({"expoentes": expoentes, "ambiente": amb}, f, indent=2, ensure_ascii=False)
    figura(resumo_linhas)
    print(json.dumps(expoentes, indent=2))


def figura(resumo_linhas):
    """Tempo medio x |V| (log-log) com IC 95%, no tamanho de impressao (duas colunas)."""
    fig, eixos = plt.subplots(1, 2, figsize=(PAGINA, 2.6))
    marcadores = "osD^v<>p"
    rot = {"Tarjan": "Tarjan (art./pontes)", "Tarjan-CFC": "Tarjan (CFC)", "Euler": "Eulerianidade"}
    for ax, nomes in [(eixos[0], LINEARES), (eixos[1], ["Bellman-Ford", "Floyd-Warshall"])]:
        for i, nome in enumerate(nomes):
            rs = sorted([r for r in resumo_linhas if r["algoritmo"] == nome], key=lambda r: r["V_medio"])
            # limite inferior do IC pode ser negativo (Bellman-Ford): corta na escala log
            ax.errorbar([r["V_medio"] for r in rs], [r["media"] for r in rs],
                        yerr=[[r["media"] - max(r["ic_inf"], 1e-4) for r in rs],
                              [r["ic_sup"] - r["media"] for r in rs]],
                        marker=marcadores[i], ms=3, lw=1, capsize=2, label=rot.get(nome, nome))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("$|V|$ do subgrafo")
        ax.grid(which="major")
    eixos[0].set_ylabel("tempo médio (s)")
    eixos[0].set_title("Quase lineares ($R=30$; ponto à direita: MCC)")
    eixos[1].set_title("Bellman-Ford e Floyd-Warshall ($R=10$)")
    # legenda do painel esquerdo abaixo da figura (dentro dos eixos ela cobria as curvas)
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, bbox_to_anchor=(0.27, -0.13))
    eixos[1].legend(loc="upper left")
    fig.tight_layout()
    salvar_figura(fig, os.path.join(FIG, "desempenho"))


if __name__ == "__main__":
    main()
