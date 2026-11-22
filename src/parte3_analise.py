"""
Parte III - small-world, lei de potencia, robustez e comparacao com modelos classicos.
Saidas: results/parte3.json, results/tables/robustez_*.csv, figuras em results/figures.

Uso: python src/parte3_analise.py [smallworld|potencia|robustez|todos]
"""
import csv
import json
import math
import os
import random
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estatistica import resumo  # noqa: E402
from grafo import (RAIZ, carregar_grafo, componentes_conexas, maior_componente,  # noqa: E402
                   num_arestas, subgrafo_induzido)
from metricas import (ajuste_lei_potencia, caminho_medio_amostrado,  # noqa: E402
                      clusterizacao_bipartida_latapy, melhor_k_min,
                      triangulos_e_clusterizacao)

SEMENTE = 2025
FIG = os.path.join(RAIZ, "results", "figures")
TAB = os.path.join(RAIZ, "results", "tables")
ARQ = os.path.join(RAIZ, "results", "parte3.json")


def salvar(chave, valor):
    dados = {}
    if os.path.exists(ARQ):
        with open(ARQ, encoding="utf-8") as f:
            dados = json.load(f)
    dados[chave] = valor
    with open(ARQ, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


def de_pares(n, pares):
    adj = [[] for _ in range(n)]
    for u, v in pares:
        adj[u].append(v)
        adj[v].append(u)
    return adj


# ------------------------------------------------------------- modelos aleatorios
def erdos_renyi(n, m, semente):
    """G(n, m): m pares distintos sorteados uniformemente."""
    rng = random.Random(semente)
    pares = set()
    while len(pares) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            pares.add((min(u, v), max(u, v)))
    return de_pares(n, pares)


def bipartido_configuracao(adj, U, semente):
    """Grafo bipartido aleatorio com as MESMAS sequencias de graus de usuarios e
    cervejas: embaralha as 'pontas' do lado das cervejas e pareia com as dos usuarios.
    Arestas repetidas sao descartadas (contadas)."""
    rng = random.Random(semente)
    pontas_u = [u for u in range(U) for _ in adj[u]]
    pontas_b = [b for b in range(U, len(adj)) for _ in adj[b]]
    rng.shuffle(pontas_b)
    pares = set(zip(pontas_u, pontas_b))
    return de_pares(len(adj), pares), len(pontas_u) - len(pares)


def barabasi_albert(n, m0, semente):
    """Ligacao preferencial: cada novo vertice liga-se a m0 vertices escolhidos com
    probabilidade proporcional ao grau (sorteio na lista de pontas de arestas)."""
    rng = random.Random(semente)
    pares = []
    pontas = list(range(m0))  # nucleo inicial: m0 vertices
    for v in range(m0, n):
        alvos = set()
        while len(alvos) < m0:
            alvos.add(rng.choice(pontas))
        for u in alvos:
            pares.append((u, v))
            pontas += [u, v]
    return de_pares(n, pares)


def watts_strogatz(n, k, p, semente):
    """Anel com cada vertice ligado aos k/2 vizinhos de cada lado; cada aresta tem a
    ponta final religada com probabilidade p (sem lacos nem repeticoes)."""
    rng = random.Random(semente)
    arestas = set()
    for v in range(n):
        for j in range(1, k // 2 + 1):
            arestas.add((v, (v + j) % n))
    final = set()
    for u, v in sorted(arestas):
        if rng.random() < p:
            w = rng.randrange(n)
            while w == u or (u, w) in final or (w, u) in final:
                w = rng.randrange(n)
            final.add((u, w))
        else:
            final.add((u, v))
    return de_pares(n, final)


def maior_comp_adj(adj):
    a, _, _ = maior_componente(adj, [[0] * len(x) for x in adj])
    return a


# --------------------------------------------------------------- small-world
def small_world(adj, U):
    n, m = len(adj), num_arestas(adj)
    k_medio = 2 * m / n
    r = {"n": n, "m": m, "k_medio": k_medio,
         "L_ER_formula_ln_n_sobre_ln_k": math.log(n) / math.log(k_medio),
         "C_ER_formula_k_sobre_n": k_medio / (n - 1)}
    K = 200  # origens de BFS para estimar L nos grafos sinteticos
    modelos = {}
    t = time.perf_counter()
    er = erdos_renyi(n, m, SEMENTE)
    modelos["Erdos-Renyi G(n,m)"] = er
    m0 = round(k_medio / 2)
    modelos[f"Barabasi-Albert (m0={m0})"] = barabasi_albert(n, m0, SEMENTE)
    kws = 2 * round(k_medio / 2)
    modelos[f"Watts-Strogatz (k={kws}, p=0.1)"] = watts_strogatz(n, kws, 0.1, SEMENTE)
    bip, descartadas = bipartido_configuracao(adj, U, SEMENTE)
    modelos["Bipartido aleatorio (mesmos graus)"] = bip
    r["bipartido_aleatorio_arestas_repetidas_descartadas"] = descartadas
    r["modelos"] = {}
    for nome, a in modelos.items():
        mcc = maior_comp_adj(a)
        medias, _ = caminho_medio_amostrado(mcc, K, SEMENTE)
        tri, c_med, trans = triangulos_e_clusterizacao(a)
        graus = sorted(len(x) for x in a)
        r["modelos"][nome] = {"arestas": num_arestas(a), "grau_max": graus[-1],
                              "mcc_vertices": len(mcc), "L_estimado": resumo(medias),
                              "triangulos": tri, "C_medio": c_med, "transitividade": trans}
        print(nome, r["modelos"][nome]["L_estimado"]["media"], c_med, f"{time.perf_counter() - t:.0f}s",
              flush=True)

    # clusterizacao bipartida (Latapy et al., 2008) em amostra de vertices: G x bipartido aleatorio
    rng = random.Random(SEMENTE)
    amostra = rng.sample(range(n), 2000)
    cc_g = clusterizacao_bipartida_latapy(adj, amostra)
    cc_r = clusterizacao_bipartida_latapy(bip, amostra)
    r["latapy_G"] = resumo(cc_g)
    r["latapy_bipartido_aleatorio"] = resumo(cc_r)
    r["latapy_amostra_vertices"] = 2000
    # L e C do grafo real vem da Parte I e de distancias_exatas.py (lidos so agora)
    while not os.path.exists(os.path.join(RAIZ, "results", "distancias_mcc.json")):
        print("aguardando distancias_mcc.json ...", flush=True)
        time.sleep(300)
    with open(os.path.join(RAIZ, "results", "distancias_mcc.json"), encoding="utf-8") as f:
        dist = json.load(f)
    with open(os.path.join(RAIZ, "results", "parte1.json"), encoding="utf-8") as f:
        p1 = json.load(f)
    r["L_G_exato_mcc"] = dist["comprimento_medio_exato"]
    r["C_G"] = p1["clusterizacao_media"]
    L_bip = r["modelos"]["Bipartido aleatorio (mesmos graus)"]["L_estimado"]["media"]
    r["sigma_bipartido"] = (r["latapy_G"]["media"] / r["latapy_bipartido_aleatorio"]["media"]) / \
        (r["L_G_exato_mcc"] / L_bip)
    salvar("small_world", r)

    # figura: CCDF de graus do grafo e dos modelos
    fig, ax = plt.subplots(figsize=(4.6, 3.4))
    for nome, a in [("BeerAdvocate", adj)] + list(modelos.items()):
        graus = sorted(len(x) for x in a)
        N = len(graus)
        ks = sorted(set(graus))
        import bisect
        ax.loglog(ks, [(N - bisect.bisect_left(graus, k)) / N for k in ks], lw=1.2 if nome == "BeerAdvocate" else .9,
                  color="black" if nome == "BeerAdvocate" else None, label=nome)
    ax.set(xlabel="grau k", ylabel="P(K ≥ k)")
    ax.grid(alpha=.3, which="both", lw=.3)
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "modelos_ccdf.pdf"))
    fig.savefig(os.path.join(FIG, "modelos_ccdf.png"), dpi=150)
    plt.close(fig)


# ------------------------------------------------------------- lei de potencia
def lei_potencia(adj, U):
    import powerlaw  # apenas para validacao e teste de razao de verossimilhanca
    grupos = {"todos": [len(x) for x in adj], "usuarios": [len(adj[v]) for v in range(U)],
              "cervejas": [len(adj[v]) for v in range(U, len(adj))]}
    r = {}
    fig, eixos = plt.subplots(1, 3, figsize=(10, 3.2))
    for ax, (nome, graus) in zip(eixos, grupos.items()):
        candidatos = sorted(set(g for g in graus if g <= 1000))
        melhor = melhor_k_min(graus, candidatos)
        k1 = ajuste_lei_potencia(graus, 1)
        ref = powerlaw.Fit(graus, discrete=True, xmin=melhor["k_min"], verbose=False)
        comp = {}
        for alt in ("lognormal", "exponential", "truncated_power_law"):
            R, p = ref.distribution_compare("power_law", alt, normalized_ratio=True)
            comp[alt] = {"R": R, "p": p}
        r[nome] = {"proprio_kmin_por_KS": melhor, "proprio_kmin_1": k1,
                   "powerlaw_pkg_alpha_mesmo_kmin": ref.power_law.alpha,
                   "powerlaw_pkg_sigma": ref.power_law.sigma,
                   "comparacao_razao_verossimilhanca": comp}
        # figura: CCDF empirica + reta ajustada a partir de k_min
        gs = sorted(graus)
        N = len(gs)
        ks = sorted(set(gs))
        import bisect
        ccdf = [(N - bisect.bisect_left(gs, k)) / N for k in ks]
        ax.loglog(ks, ccdf, ".", ms=2, color="gray", label="empírica")
        kmin, gamma = melhor["k_min"], melhor["gamma"]
        frac = melhor["n_cauda"] / N
        xs = [k for k in ks if k >= kmin]
        ax.loglog(xs, [frac * ((k - .5) / (kmin - .5)) ** (1 - gamma) for k in xs], "r-",
                  label=f"γ={gamma:.2f}, k_min={kmin}")
        ax.set(title=nome.replace("usuarios", "usuários"), xlabel="grau k", ylabel="P(K ≥ k)")
        ax.grid(alpha=.3, which="both", lw=.3)
        ax.legend(fontsize=7)
        print(nome, melhor, ref.power_law.alpha, comp, flush=True)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "lei_potencia.pdf"))
    fig.savefig(os.path.join(FIG, "lei_potencia.png"), dpi=150)
    plt.close(fig)
    salvar("lei_potencia", r)


# ------------------------------------------------------------------- robustez
def metricas_apos_remocao(adj, removidos, k_bfs, semente):
    """Remove 'removidos' (e arestas incidentes) e mede as metricas A-D do Apendice C."""
    fora = set(removidos)
    restantes = [v for v in range(len(adj)) if v not in fora]
    a2, _, _ = subgrafo_induzido(adj, [[0] * len(x) for x in adj], restantes)
    comp, tam = componentes_conexas(a2)
    n_rest = len(a2)
    maior = max(tam)
    c_max = tam.index(maior)
    vert = [v for v in range(n_rest) if comp[v] == c_max]
    a3, _, _ = subgrafo_induzido(a2, [[0] * len(x) for x in a2], vert)
    medias, hist = caminho_medio_amostrado(a3, min(k_bfs, len(a3)), semente)
    return {"A_maior_componente": maior, "A_S_fracao_restantes": maior / n_rest,
            "A_S_fracao_original": maior / len(adj), "B_num_componentes": len(tam),
            "C_dist_media_maior_comp": sum(medias) / len(medias),
            "C_dist_max_observada": max(hist), "D_fracao_isolados": sum(1 for x in a2 if not x) / n_rest}


def robustez(adj_g, peso_g):
    adj, _, _ = maior_componente(adj_g, peso_g)
    n = len(adj)
    r_rem = math.ceil(0.05 * n)
    T, K = 30, 100
    base = metricas_apos_remocao(adj, [], K, SEMENTE)
    linhas = []
    t = time.perf_counter()
    for rep in range(T):
        rng = random.Random(SEMENTE + rep)
        rem = rng.sample(range(n), r_rem)
        m = metricas_apos_remocao(adj, rem, K, SEMENTE + rep)
        m["rep"] = rep
        linhas.append(m)
        print(f"aleatoria {rep} {time.perf_counter() - t:.0f}s", flush=True)
    # ataque direcionado: ranking fixo por grau (desempate pelo id)
    ranking = sorted(range(n), key=lambda v: (-len(adj[v]), v))
    alvo = metricas_apos_remocao(adj, ranking[:r_rem], K, SEMENTE)
    chaves = [c for c in base if c != "rep"]
    with open(os.path.join(TAB, "robustez_aleatoria.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rep"] + chaves)
        w.writeheader()
        w.writerows(linhas)
    res = {"n": n, "r": r_rem, "T": T, "K_origens_bfs": K, "sem_remocao": base, "direcionado_grau": alvo,
           "aleatoria": {c: resumo([x[c] for x in linhas]) for c in chaves},
           "removidos_direcionado_usuarios_e_cervejas": "ver contagem",
           }
    salvar("robustez", res)

    figura_robustez()
    print(json.dumps({"base": base, "alvo": alvo}, indent=2))


def figura_robustez():
    """Boxplots da remocao aleatoria (media ± dp) + valor do ataque por grau e sem remocao."""
    with open(ARQ, encoding="utf-8") as f:
        res = json.load(f)["robustez"]
    with open(os.path.join(TAB, "robustez_aleatoria.csv"), encoding="utf-8") as f:
        linhas = [{k: float(v) for k, v in x.items()} for x in csv.DictReader(f)]
    alvo, base = res["direcionado_grau"], res["sem_remocao"]
    titulos = {"A_S_fracao_restantes": "A: S (maior comp./restantes)", "B_num_componentes": "B: nº de componentes",
               "C_dist_media_maior_comp": "C: distância média", "D_fracao_isolados": "D: fração de isolados"}
    fig, eixos = plt.subplots(1, 4, figsize=(10, 3.1))
    for ax, (c, tit) in zip(eixos, titulos.items()):
        vals = [x[c] for x in linhas]
        ax.boxplot(vals, widths=.5)
        mu, dp = res["aleatoria"][c]["media"], res["aleatoria"][c]["desvio_padrao"]
        ax.errorbar([1.4], [mu], yerr=[dp], fmt="o", color="tab:blue", ms=3, capsize=3, label="aleatória: média ± dp")
        ax.plot([1], [alvo[c]], "r*", ms=10, label="ataque por grau")
        ax.plot([1], [base[c]], "g^", ms=6, label="sem remoção")
        ax.set_title(tit, fontsize=8)
        ax.set_xticks([])
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, fontsize=7, frameon=False)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(os.path.join(FIG, "robustez.pdf"))
    fig.savefig(os.path.join(FIG, "robustez.png"), dpi=150)
    plt.close(fig)


def main():
    etapa = sys.argv[1] if len(sys.argv) > 1 else "todos"
    os.makedirs(FIG, exist_ok=True)
    os.makedirs(TAB, exist_ok=True)
    adj, peso, U = carregar_grafo()
    if etapa in ("potencia", "todos"):
        lei_potencia(adj, U)
    if etapa in ("robustez", "todos"):
        robustez(adj, peso)
    if etapa == "figura_robustez":
        figura_robustez()
    if etapa in ("smallworld", "todos"):
        small_world(adj, U)


if __name__ == "__main__":
    main()
