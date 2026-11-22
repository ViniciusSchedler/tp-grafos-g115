"""
Parte III - small-world, lei de potencia, robustez e comparacao com modelos classicos.
Saidas: results/parte3.json, results/tables/robustez_*.csv, figuras em results/figures.

Uso: python src/parte3_analise.py [smallworld|potencia|robustez|todos|figura_robustez|figura_modelos|figura_potencia|diagnostico_trocas]
"""
import csv
import json
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo import COLUNA, COR, PAGINA, plt, salvar_figura  # noqa: E402
from estatistica import resumo  # noqa: E402
from grafo import (RAIZ, carregar_grafo, componentes_conexas, maior_componente,  # noqa: E402
                   num_arestas, subgrafo_induzido)
from metricas import (ajuste_lei_potencia, ajuste_discreto_exato,  # noqa: E402
                      bondade_ajuste_bootstrap, caminho_medio_amostrado,
                      clusterizacao_bipartida_latapy, melhor_k_min,
                      triangulos_e_clusterizacao)

SEMENTE = 2025
FIG = os.path.join(RAIZ, "results", "figures")
TAB = os.path.join(RAIZ, "results", "tables")
ARQ = os.path.join(RAIZ, "results", "parte3.json")


def salvar(chave, valor):
    """Grava results/parte3.json[chave]. Trava simples por arquivo, pois as etapas podem
    rodar em processos paralelos."""
    trava = ARQ + ".lock"
    while True:
        try:
            fd = os.open(trava, os.O_CREAT | os.O_EXCL)
            break
        except FileExistsError:
            time.sleep(0.2)
    try:
        _salvar(chave, valor)
    finally:
        os.close(fd)
        os.remove(trava)


def _salvar(chave, valor):
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
    """Modelo de configuracao bipartido:
    embaralha as 'pontas' do lado das cervejas e pareia com as dos usuarios.
    Pares repetidos sao descartados (contados), o que REDUZ os graus dos vertices de grau
    alto: a sequencia de graus NAO e preservada. Substituido por bipartido_trocas."""
    rng = random.Random(semente)
    pontas_u = [u for u in range(U) for _ in adj[u]]
    pontas_b = [b for b in range(U, len(adj)) for _ in adj[b]]
    rng.shuffle(pontas_b)
    pares = set(zip(pontas_u, pontas_b))
    return de_pares(len(adj), pares), len(pontas_u) - len(pares)


def bipartido_trocas(adj, U, trocas_por_aresta, semente):
    """Grafo bipartido aleatorio com EXATAMENTE os mesmos graus de cada usuario e de cada
    cerveja, por trocas de arestas (Maslov & Sneppen, 2002; Gionis et al., 2007):
    sorteia duas arestas {u1,b1} e {u2,b2} e as troca por {u1,b2} e {u2,b1}, se isso nao
    criar aresta repetida. Cada troca preserva o grau dos quatro vertices e a biparticao.
    Parte do grafo real e tenta trocas_por_aresta * |E| trocas.
    Devolve (adj, trocas_aceitas, fracao_de_arestas_originais_que_restaram)."""
    rng = random.Random(semente)
    N = len(adj)
    arestas = [(u, b) for u in range(U) for b in adj[u]]
    m = len(arestas)
    presentes = {u * N + b for u, b in arestas}
    originais = set(presentes)
    aceitas = 0
    for _ in range(trocas_por_aresta * m):
        i, j = int(rng.random() * m), int(rng.random() * m)
        u1, b1 = arestas[i]
        u2, b2 = arestas[j]
        if u1 == u2 or b1 == b2:
            continue
        x, y = u1 * N + b2, u2 * N + b1
        if x in presentes or y in presentes:
            continue
        presentes.discard(u1 * N + b1)
        presentes.discard(u2 * N + b2)
        presentes.add(x)
        presentes.add(y)
        arestas[i], arestas[j] = (u1, b2), (u2, b1)
        aceitas += 1
    restantes = len(presentes & originais) / m
    return de_pares(N, arestas), aceitas, restantes


def sobreposicao_esperada(adj, U):
    """Diagnostico de mistura das trocas: fracao de arestas do grafo real que um grafo
    bipartido aleatorio com os mesmos graus conteria por acaso, aproximada por
    (1/m) * sum_{(u,b) em E} min(1, k_u k_b / m). Se a fracao de arestas originais que
    restam apos as trocas e proxima deste valor, a cadeia de trocas 'esqueceu' o grafo inicial."""
    m = sum(len(adj[u]) for u in range(U))
    return sum(min(1.0, len(adj[u]) * len(adj[b]) / m) for u in range(U) for b in adj[u]) / m


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
    anel = [(v, (v + j) % n) for v in range(n) for j in range(1, k // 2 + 1)]
    atuais = {frozenset(a) for a in anel}  # conjunto de arestas do grafo em construcao
    for u, v in anel:
        if rng.random() < p:
            w = rng.randrange(n)
            while w == u or frozenset((u, w)) in atuais:
                w = rng.randrange(n)
            atuais.discard(frozenset((u, v)))
            atuais.add(frozenset((u, w)))
    return de_pares(n, [tuple(a) for a in atuais])


def maior_comp_adj(adj):
    a, _, _ = maior_componente(adj, [[0] * len(x) for x in adj])
    return a


# --------------------------------------------------------------- small-world
def modelos_classicos(n, m):
    """ER, BA e WS com o mesmo n e grau medio proximo do grafo real (sementes fixas)."""
    k_medio = 2 * m / n
    m0 = round(k_medio / 2)
    kws = 2 * round(k_medio / 2)
    return {"Erdos-Renyi G(n,m)": erdos_renyi(n, m, SEMENTE),
            f"Barabasi-Albert (m0={m0})": barabasi_albert(n, m0, SEMENTE),
            f"Watts-Strogatz (k={kws}, p=0.1)": watts_strogatz(n, kws, 0.1, SEMENTE)}


R_TROCAS = 10    # instancias do modelo nulo bipartido
Q_TROCAS = 10    # tentativas de troca por aresta em cada instancia


def small_world(adj, U):
    n, m = len(adj), num_arestas(adj)
    k_medio = 2 * m / n
    r = {"n": n, "m": m, "k_medio": k_medio,
         "L_ER_formula_ln_n_sobre_ln_k": math.log(n) / math.log(k_medio),
         "C_ER_formula_k_sobre_n": k_medio / (n - 1)}
    K = 200  # origens de BFS para estimar L nos modelos classicos
    t = time.perf_counter()
    modelos = modelos_classicos(n, m)
    r["modelos"] = {}
    for nome, a in modelos.items():
        mcc = maior_comp_adj(a)
        medias, _ = caminho_medio_amostrado(mcc, K, SEMENTE)
        tri, c_med, trans = triangulos_e_clusterizacao(a)
        r["modelos"][nome] = {"arestas": num_arestas(a), "grau_max": max(len(x) for x in a),
                              "mcc_vertices": len(mcc), "L_estimado": resumo(medias),
                              "triangulos": tri, "C_medio": c_med, "transitividade": trans}
        print(nome, r["modelos"][nome]["L_estimado"]["media"], c_med, f"{time.perf_counter() - t:.0f}s",
              flush=True)
    figura_modelos(adj, modelos)
    del modelos

    # modelo nulo bipartido: mesmos graus (trocas de arestas); L e cc de Latapy
    with open(os.path.join(RAIZ, "results", "distancias_mcc.json"), encoding="utf-8") as f:
        L_G = json.load(f)["comprimento_medio_exato"]
    amostra = random.Random(SEMENTE).sample(range(n), 2000)
    cc_g = clusterizacao_bipartida_latapy(adj, amostra)
    instancias = []
    for i in range(R_TROCAS):
        b, aceitas, restantes = bipartido_trocas(adj, U, Q_TROCAS, SEMENTE + i)
        assert all(len(b[v]) == len(adj[v]) for v in range(n))  # graus preservados
        mcc = maior_comp_adj(b)
        medias, _ = caminho_medio_amostrado(mcc, 100, SEMENTE + i)
        cc = clusterizacao_bipartida_latapy(b, amostra)
        instancias.append({"semente": SEMENTE + i, "trocas_tentadas": Q_TROCAS * m, "trocas_aceitas": aceitas,
                           "frac_arestas_originais_restantes": restantes, "mcc_vertices": len(mcc),
                           "L_estimado_100_origens": sum(medias) / len(medias),
                           "cc_latapy_media": sum(cc) / len(cc), "cc_latapy_n": len(cc)})
        print("trocas", i, instancias[-1], f"{time.perf_counter() - t:.0f}s", flush=True)
    r["L_G_exato_mcc"] = L_G
    r["latapy_amostra_vertices"] = 2000
    r["latapy_G"] = resumo(cc_g)
    r["nulo_trocas"] = {"R": R_TROCAS, "Q": Q_TROCAS, "instancias": instancias,
                        "L": resumo([x["L_estimado_100_origens"] for x in instancias]),
                        "cc_latapy": resumo([x["cc_latapy_media"] for x in instancias])}
    cc_r = r["nulo_trocas"]["cc_latapy"]["media"]
    L_r = r["nulo_trocas"]["L"]["media"]
    r["razao_cc"] = r["latapy_G"]["media"] / cc_r
    r["razao_L"] = L_G / L_r
    r["sigma_bipartido"] = r["razao_cc"] / r["razao_L"]
    salvar("small_world", r)


def figura_modelos(adj, modelos):
    import bisect
    fig, ax = plt.subplots(figsize=(COLUNA, 2.3))
    estilos = {"BeerAdvocate": ("black", "-"), "Erdos": (COR["azul_claro"], "--"),
               "Barabasi": (COR["destaque"], "-."), "Watts": (COR["verde"], ":")}
    for nome, a in [("BeerAdvocate", adj)] + list(modelos.items()):
        graus = sorted(len(x) for x in a)
        N = len(graus)
        ks = sorted(set(graus))
        cor, ls = next(v for k, v in estilos.items() if nome.startswith(k))
        rot = (nome.replace("Erdos-Renyi", "Erdős–Rényi").replace("Barabasi-Albert", "Barabási–Albert")
               .replace("Watts-Strogatz", "Watts–Strogatz").replace("m0", "m₀"))
        ax.loglog(ks, [(N - bisect.bisect_left(graus, k)) / N for k in ks], ls, color=cor,
                  lw=1.4 if nome == "BeerAdvocate" else 1.1, label=rot)
    ax.set(xlabel="grau $k$", ylabel="$P(K \\geq k)$")
    ax.grid(which="major")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.25), ncol=2, fontsize=6.5, handlelength=2.5)
    salvar_figura(fig, os.path.join(FIG, "modelos_ccdf"))


# ------------------------------------------------------------- lei de potencia
B_BOOTSTRAP = 500


def grupos_de_graus(adj, U):
    return {"todos": [len(x) for x in adj], "usuarios": [len(adj[v]) for v in range(U)],
            "cervejas": [len(adj[v]) for v in range(U, len(adj))]}


def lei_potencia(adj, U):
    import powerlaw  # validacao do MLE e testes de razao de verossimilhanca (Alstott et al., 2014)
    r = {}
    for nome, graus in grupos_de_graus(adj, U).items():
        t = time.perf_counter()
        gof = bondade_ajuste_bootstrap(graus, B_BOOTSTRAP, SEMENTE)
        obs = gof["observado"]
        candidatos = sorted(set(g for g in graus if g <= 1000))
        aprox = melhor_k_min(graus, candidatos)
        ref = powerlaw.Fit(graus, discrete=True, xmin=obs["k_min"], verbose=False)
        comp = {}
        for alt in ("lognormal", "exponential", "truncated_power_law"):
            R, p = ref.distribution_compare("power_law", alt, normalized_ratio=True)
            comp[alt] = {"R": R, "p": p}
        r[nome] = {"exato": gof, "aproximado_eq37": aprox, "kmin_1_aproximado": ajuste_lei_potencia(graus, 1),
                   "powerlaw_pkg_alpha_mesmo_kmin": ref.power_law.alpha, "powerlaw_pkg_sigma": ref.power_law.sigma,
                   "powerlaw_pkg_D": ref.power_law.D,
                   "truncada_alpha": ref.truncated_power_law.alpha, "truncada_lambda": ref.truncated_power_law.Lambda,
                   "comparacao_razao_verossimilhanca": comp}
        print(nome, obs, "p =", gof["p_valor"], comp, f"{time.perf_counter() - t:.0f}s", flush=True)
    salvar("lei_potencia", r)
    figura_lei_potencia(adj, U)


def figura_lei_potencia(adj, U):
    """CCDF empirica, lei de potencia ajustada (parametros de parte3.json) e lei de potencia
    truncada (pacote powerlaw, mesmo k_min), para todos, usuarios e cervejas."""
    import bisect

    import numpy as np
    import powerlaw
    from scipy.special import zeta
    with open(ARQ, encoding="utf-8") as f:
        res = json.load(f)["lei_potencia"]
    fig, eixos = plt.subplots(1, 3, figsize=(PAGINA, 2.25), sharey=True)
    for ax, (nome, graus) in zip(eixos, grupos_de_graus(adj, U).items()):
        obs = res[nome]["exato"]["observado"]
        gs = sorted(graus)
        N = len(gs)
        ks = sorted(set(gs))
        ax.loglog(ks, [(N - bisect.bisect_left(gs, k)) / N for k in ks], ".", ms=2.5, color=COR["cinza"],
                  label="empírica")
        kmin, g = obs["k_min"], obs["gamma"]
        frac = obs["n_cauda"] / N
        xs = np.array([k for k in ks if k >= kmin], dtype=float)
        ax.loglog(xs, frac * zeta(g, xs) / zeta(g, kmin), "-", color=COR["destaque"], label="lei de potência")
        trunc = powerlaw.Fit(graus, discrete=True, xmin=kmin, verbose=False).truncated_power_law
        ax.loglog(xs, frac * trunc.ccdf(xs), "--", color=COR["usuarios"], label="lei de potência truncada")
        titulo = nome.replace("usuarios", "usuários")
        ax.set_title(f"{titulo} ($\\hat\\gamma$ = {g:.2f}; $k_{{\\min}}$ = {int(kmin)})".replace(".", ","))
        ax.set_xlabel("grau $k$")
        ax.grid(which="major")
    eixos[0].set_ylabel("$P(K \\geq k)$")
    eixos[0].set_ylim(1e-5, 1.5)
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.04), markerscale=2)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    salvar_figura(fig, os.path.join(FIG, "lei_potencia"))


# ------------------------------------------------------------------- robustez
def metricas_apos_remocao(adj, removidos, k_bfs, semente, eh_usuario=None):
    """Remove 'removidos' (e arestas incidentes) e mede as metricas A-D do Apendice C.
    A metrica C e estimada com BFS a partir de k_bfs origens sorteadas na maior componente."""
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
    isolados = [v for v in range(n_rest) if not a2[v]]
    r = {"A_maior_componente": maior, "A_S_fracao_restantes": maior / n_rest,
         "A_S_fracao_original": maior / len(adj), "B_num_componentes": len(tam),
         "C_dist_media_maior_comp": sum(medias) / len(medias),
         "C_dist_max_observada": max(hist), "D_fracao_isolados": len(isolados) / n_rest}
    if eh_usuario is not None:
        r["isolados_usuarios"] = sum(1 for v in isolados if eh_usuario[restantes[v]])
        r["isolados_cervejas"] = len(isolados) - r["isolados_usuarios"]
        r["C_resumo_origens"] = resumo(medias)
    return r


def robustez(adj_g, peso_g, U):
    adj, _, vert = maior_componente(adj_g, peso_g)
    eh_usuario = [v < U for v in vert]
    n = len(adj)
    r_rem = math.ceil(0.05 * n)
    T, K = 30, 100
    with open(os.path.join(RAIZ, "results", "distancias_mcc.json"), encoding="utf-8") as f:
        L_exato = json.load(f)["comprimento_medio_exato"]
    base = metricas_apos_remocao(adj, [], K, SEMENTE)
    base["C_dist_media_maior_comp_estimada_100_origens"] = base["C_dist_media_maior_comp"]
    base["C_dist_media_maior_comp"] = L_exato  # sem remocao o valor exato e conhecido
    linhas = []
    t = time.perf_counter()
    for rep in range(T):
        rem = random.Random(SEMENTE + rep).sample(range(n), r_rem)
        # origens das BFS com semente distinta da usada na remocao (sorteios independentes)
        m = metricas_apos_remocao(adj, rem, K, SEMENTE + 10_000 + rep)
        m["rep"] = rep
        linhas.append(m)
        print(f"aleatoria {rep} {time.perf_counter() - t:.0f}s", flush=True)
    # ataque direcionado: ranking fixo por grau calculado antes da remocao (desempate pelo id)
    ranking = sorted(range(n), key=lambda v: (-len(adj[v]), v))
    alvo = metricas_apos_remocao(adj, ranking[:r_rem], 2000, SEMENTE, eh_usuario)
    grau_corte = len(adj[ranking[r_rem - 1]])
    removidos = ranking[:r_rem]
    soma_graus = sum(len(x) for x in adj)
    composicao = {
        "removidos_usuarios": sum(1 for v in removidos if eh_usuario[v]),
        "removidos_cervejas": sum(1 for v in removidos if not eh_usuario[v]),
        "grau_minimo_removido": grau_corte,
        "empates_no_grau_de_corte_total": sum(1 for x in adj if len(x) == grau_corte),
        "empates_no_grau_de_corte_removidos": sum(1 for v in removidos if len(adj[v]) == grau_corte),
        "isolados_usuarios": alvo.pop("isolados_usuarios"), "isolados_cervejas": alvo.pop("isolados_cervejas"),
        "soma_graus_removidos_frac": sum(len(adj[v]) for v in removidos) / soma_graus,
    }
    composicao["isolados_total"] = composicao["isolados_usuarios"] + composicao["isolados_cervejas"]
    chaves = list(linhas[0].keys())
    chaves.remove("rep")
    with open(os.path.join(TAB, "robustez_aleatoria.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["rep"] + chaves)
        w.writeheader()
        w.writerows(linhas)
    res = {"n": n, "r": r_rem, "T": T, "K_origens_bfs_aleatoria": K, "K_origens_bfs_direcionado": 2000,
           "sem_remocao": base, "direcionado_grau": alvo, "direcionado_composicao": composicao,
           "aleatoria": {c: resumo([x[c] for x in linhas]) for c in chaves}}
    salvar("robustez", res)
    figura_robustez()


def figura_robustez():
    """Boxplots da remocao aleatoria (media ± dp) + valor do ataque por grau e sem remocao."""
    with open(ARQ, encoding="utf-8") as f:
        res = json.load(f)["robustez"]
    with open(os.path.join(TAB, "robustez_aleatoria.csv"), encoding="utf-8") as f:
        linhas = [{k: float(v) for k, v in x.items()} for x in csv.DictReader(f)]
    alvo, base = res["direcionado_grau"], res["sem_remocao"]
    titulos = {"A_S_fracao_restantes": "A: $S$ (maior comp./restantes)", "B_num_componentes": "B: nº de componentes",
               "C_dist_media_maior_comp": "C: distância média", "D_fracao_isolados": "D: fração de isolados"}
    fig, eixos = plt.subplots(1, 4, figsize=(PAGINA, 2.0))
    for ax, (c, tit) in zip(eixos, titulos.items()):
        vals = [x[c] for x in linhas]
        ax.boxplot(vals, positions=[1], widths=.45, medianprops={"color": "black"},
                   flierprops={"markersize": 2})
        mu, dp = res["aleatoria"][c]["media"], res["aleatoria"][c]["desvio_padrao"]
        ax.errorbar([1.45], [mu], yerr=[dp], fmt="o", color=COR["usuarios"], ms=3, capsize=3,
                    label="aleatória: média ± DP")
        ax.plot([2.1], [alvo[c]], "*", color=COR["destaque"], ms=9, label="5% de maior grau")
        ax.plot([0.55], [base[c]], "^", color=COR["verde"], ms=5, label="sem remoção")
        if c == "B_num_componentes":
            ax.set_yscale("log")
        ax.set_title(tit)
        ax.set_xlim(0.3, 2.4)
        ax.set_xticks([])
        ax.grid(axis="y", which="major")
    h, l = eixos[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06))
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    salvar_figura(fig, os.path.join(FIG, "robustez"))


def main():
    etapa = sys.argv[1] if len(sys.argv) > 1 else "todos"
    os.makedirs(FIG, exist_ok=True)
    os.makedirs(TAB, exist_ok=True)
    adj, peso, U = carregar_grafo()
    if etapa in ("potencia", "todos"):
        lei_potencia(adj, U)
    if etapa in ("robustez", "todos"):
        robustez(adj, peso, U)
    if etapa == "figura_robustez":
        figura_robustez()
    if etapa in ("diagnostico_trocas", "todos"):
        salvar("nulo_trocas_diagnostico", {"sobreposicao_esperada": sobreposicao_esperada(adj, U)})
    if etapa == "figura_potencia":
        figura_lei_potencia(adj, U)
    if etapa == "figura_modelos":
        figura_modelos(adj, modelos_classicos(len(adj), num_arestas(adj)))
    if etapa in ("smallworld", "todos"):
        small_world(adj, U)


if __name__ == "__main__":
    main()
