"""
Gera, a partir de results/, os arquivos incluidos pelo artigo (artigo/gerado/*.tex) e a
figura da distribuicao de distancias. Nenhum numero do artigo e digitado a mao.
"""
import csv
import datetime
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import RAIZ  # noqa: E402

RES = os.path.join(RAIZ, "results")
OUT = os.path.join(RAIZ, "artigo", "gerado")
LINK_REPOSITORIO = "https://github.com/USUARIO/tp-grafos-g115"  # PENDENTE: link real

DECLARACAO_IA = (
    "PENDENTE -- revisar conforme as regras da disciplina. Sugestão: "
    "O código, os experimentos e a redação foram desenvolvidos com auxílio do assistente "
    "Claude (Anthropic); o estudante revisou o código, conferiu os resultados e é responsável "
    "pelo conteúdo.")


def ler(nome):
    with open(os.path.join(RES, nome), encoding="utf-8") as f:
        return json.load(f)


def br(x, casas=0):
    """Numero no formato brasileiro: 1.234.567,89"""
    s = f"{x:,.{casas}f}"
    # {,} evita o espaco apos a virgula quando o numero aparece em modo matematico
    return s.replace(",", "X").replace(".", "{,}").replace("X", ".")


def sci(x, casas=2):
    m, e = f"{x:.{casas}e}".split("e")
    return f"{m.replace('.', '{,}')}\\times 10^{{{int(e)}}}"  # conteudo matematico, sem $


def pct(x, casas=1):
    return br(100 * x, casas) + "\\%"


def main():
    os.makedirs(OUT, exist_ok=True)
    trat = ler(os.path.join("..", "data", "processed", "tratamento.json"))
    p1 = ler("parte1.json")
    dist = ler("distancias_mcc.json")
    p2 = ler("parte2_resultados.json")
    p3 = ler("parte3.json")
    exp = json.load(open(os.path.join(RES, "tables", "desempenho_expoentes.json"), encoding="utf-8"))
    resumo_t = list(csv.DictReader(open(os.path.join(RES, "tables", "desempenho_resumo.csv"), encoding="utf-8")))
    sw, pl, rob = p3["small_world"], p3["lei_potencia"], p3["robustez"]

    # ------------------------------------------------ figura: distancias exatas
    hist = {int(k): v for k, v in dist["histograma_distancias_pares_ordenados"].items()}
    total = sum(hist.values())
    fig, ax = plt.subplots(figsize=(4.2, 2.6))
    ks = sorted(hist)
    ax.bar(ks, [hist[k] / total for k in ks], color="tab:gray")
    for k in ks:
        ax.text(k, hist[k] / total, f"{100 * hist[k] / total:.1f}%".replace(".", ","), ha="center",
                va="bottom", fontsize=6)
    ax.set(xlabel="distância d(u, v)", ylabel="fração dos pares", xticks=ks)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "figures", "distribuicao_distancias.pdf"))
    fig.savefig(os.path.join(RES, "figures", "distribuicao_distancias.png"), dpi=150)
    plt.close(fig)

    # ------------------------------------------------ macros numericas
    graus_um = float(p1["distribuicao_graus"]["todos"]["1"])
    det = p1["componentes_detalhe"]
    pequenas = [c for c in det if c["tamanho"] < p1["mcc_vertices"]]
    raw = os.path.join(RAIZ, "data", "raw")
    data_dl = open(os.path.join(raw, "DOWNLOAD_DATE.txt")).read().strip()[:10]
    data_dl = datetime.date.fromisoformat(data_dl).strftime("%d/%m/%Y")
    tam_bruto = os.path.getsize(os.path.join(raw, "Beeradvocate.txt.gz")) if os.path.exists(
        os.path.join(raw, "Beeradvocate.txt.gz")) else 445475306
    amb = exp["ambiente"]
    m = {
        "NVertices": br(p1["vertices"]), "NArestas": br(p1["arestas"]),
        "NUsuarios": br(p1["usuarios"]), "NCervejas": br(p1["cervejas"]),
        "NAvLidas": br(trat["avaliacoes_lidas"]), "NAvSemUsuario": br(trat["avaliacoes_sem_profileName_descartadas"]),
        "NParesRepetidos": br(trat["pares_usuario_cerveja_repetidos"]),
        "NAvFundidas": br(trat["avaliacoes_removidas_na_fusao_de_paralelas"]),
        "DataDownload": data_dl, "NBytesBruto": br(tam_bruto),
        "DataMin": datetime.datetime.fromtimestamp(trat["review_time_min_unix"], datetime.UTC).strftime("%d/%m/%Y"),
        "GrauMax": br(p1["graus_todos"]["max"]), "GrauMedio": br(p1["graus_todos"]["medio"], 2),
        "GrauMedioU": br(p1["graus_usuarios"]["medio"], 2), "GrauMaxU": br(p1["graus_usuarios"]["max"]),
        "GrauMedioB": br(p1["graus_cervejas"]["medio"], 2), "GrauMaxB": br(p1["graus_cervejas"]["max"]),
        "FracGrauUm": pct(graus_um),
        "Densidade": sci(p1["densidade"]), "DensidadeBip": sci(p1["densidade_bipartida_E_sobre_UxB"]),
        "NComponentes": br(p1["num_componentes"]), "NCompPequenas": br(len(pequenas)),
        "MCCVertices": br(p1["mcc_vertices"]), "MCCPercent": pct(p1["mcc_vertices"] / p1["vertices"], 2),
        "Diametro": str(dist["diametro"]), "Raio": str(dist["raio"]),
        "LExato": br(dist["comprimento_medio_exato"], 3),
        "FracDistAteQuatro": pct(sum(v for k, v in hist.items() if k <= 4) / total),
        "TempoDistHoras": br(dist["tempo_total_s"] / 3600, 1), "BFSLimitantes": str(p1["bfs_usadas_limitantes"]),
        "Triangulos": br(p1["triangulos"]), "Clusterizacao": br(p1["clusterizacao_media"], 1),
        "VizVertices": br(p1["visualizacao"]["vertices"]), "VizArestas": br(p1["visualizacao"]["arestas"]),
        "DFSArvores": br(p2["dfs_arvores_no_grafo_completo"]),
        "EulerImpares": br(p2["euler_grafo_completo"]["vertices_grau_impar"]),
        "EulerImparesMCC": br(p2["euler_mcc"]["vertices_grau_impar"]),
        "AGMPeso": br(p2["agm_peso_prim"], 2), "BFPassadas": str(p2["bellman_ford_passadas_ate_estabilizar"]),
        "TarjanArt": br(p2["tarjan_articulacoes"]), "TarjanPontes": br(p2["tarjan_pontes"]),
        "LERformula": br(sw["L_ER_formula_ln_n_sobre_ln_k"], 2), "CERformula": sci(sw["C_ER_formula_k_sobre_n"]),
        "LERsim": br(sw["modelos"]["Erdos-Renyi G(n,m)"]["L_estimado"]["media"], 2),
        "LatapyG": br(sw["latapy_G"]["media"], 4), "LatapyR": br(sw["latapy_bipartido_aleatorio"]["media"], 4),
        "LatapyRazao": br(sw["latapy_G"]["media"] / sw["latapy_bipartido_aleatorio"]["media"], 1),
        "LBipR": br(sw["modelos"]["Bipartido aleatorio (mesmos graus)"]["L_estimado"]["media"], 2),
        "SigmaBip": br(sw["sigma_bipartido"], 2),
        "GrauMaxBA": br(next(r["grau_max"] for k, r in sw["modelos"].items() if k.startswith("Barabasi"))),
        "BipDescartadas": br(sw["bipartido_aleatorio_arestas_repetidas_descartadas"]),
        "BipDescartadasPct": pct(sw["bipartido_aleatorio_arestas_repetidas_descartadas"] / sw["m"]),
        "GammaTodos": br(pl["todos"]["proprio_kmin_por_KS"]["gamma"], 2),
        "KminTodos": str(pl["todos"]["proprio_kmin_por_KS"]["k_min"]),
        "GammaU": br(pl["usuarios"]["proprio_kmin_por_KS"]["gamma"], 2),
        "GammaB": br(pl["cervejas"]["proprio_kmin_por_KS"]["gamma"], 2),
        "GammaTodosPkg": br(pl["todos"]["powerlaw_pkg_alpha_mesmo_kmin"], 2),
        "RobR": br(rob["r"]),
        "RobSAleat": br(rob["aleatoria"]["A_S_fracao_restantes"]["media"], 4),
        "RobBAleat": br(rob["aleatoria"]["B_num_componentes"]["media"], 1),
        "RobCBase": br(rob["sem_remocao"]["C_dist_media_maior_comp"], 3),
        "RobCAleat": br(rob["aleatoria"]["C_dist_media_maior_comp"]["media"], 3),
        "RobSAlvo": br(rob["direcionado_grau"]["A_S_fracao_restantes"], 4),
        "RobBAlvo": br(rob["direcionado_grau"]["B_num_componentes"]),
        "RobDAlvo": pct(rob["direcionado_grau"]["D_fracao_isolados"], 1),
        "RobCAlvo": br(rob["direcionado_grau"]["C_dist_media_maior_comp"], 3),
        "Hardware": "Intel Core i5-12450H (8 núcleos, 12 threads), 15,7 GB de RAM",
        "SO": "Windows 11 Home 64 bits",
        "PythonVersao": amb["python"].split()[0],
        "LinkRepositorio": LINK_REPOSITORIO,
        "DeclaracaoIA": DECLARACAO_IA,
    }
    # estimativas para a MCC a partir da razao tempo/custo da maior amostra medida
    def razao(nome):
        rs = [r for r in resumo_t if r["algoritmo"] == nome]
        return float(max(rs, key=lambda r: float(r["V_medio"]))["tempo_sobre_custo_ns"]) * 1e-9
    V, E = p2["V_mcc"], p2["E_mcc"]
    m["EstBFHoras"] = br(razao("Bellman-Ford") * V * 2 * E / 3600, 1)
    m["EstFWAnos"] = br(razao("Floyd-Warshall") * V ** 3 / (3600 * 24 * 365), 1)
    m["EstFWMemGB"] = br(V * V * 8 / 1e9, 0)
    m["TarjanPontesFolha"] = br(p2["tarjan_pontes_com_folha"])
    m["DijkstraMax"] = br(p2["dijkstra_dist_max"], 1)
    m["DijkstraMedia"] = br(p2["dijkstra_dist_media"], 2)
    ex = exp["expoentes"]
    quase = ["BFS", "DFS", "Euler", "Tarjan", "Dijkstra", "Prim"]
    m["ExpMin"] = br(min(ex[a]["inclinacao_vs_custo_teorico"] for a in quase), 2)
    m["ExpMax"] = br(max(ex[a]["inclinacao_vs_custo_teorico"] for a in quase), 2)
    m["ExpKruskal"] = br(ex["Kruskal"]["inclinacao_vs_custo_teorico"], 2)
    m["ExpBF"] = br(ex["Bellman-Ford"]["inclinacao_vs_custo_teorico"], 2)
    m["ExpBFV"] = br(ex["Bellman-Ford"]["inclinacao_vs_V"], 2)
    m["ExpFW"] = br(ex["Floyd-Warshall"]["inclinacao_vs_custo_teorico"], 2)
    tA = {r["algoritmo"]: float(r["media"]) for r in resumo_t if r["experimento"] == "A"}
    m["TempoBFS"] = br(tA["BFS"], 3)
    m["TempoDijkstra"] = br(tA["Dijkstra"], 3)
    m["RazaoDijkstraBFS"] = br(tA["Dijkstra"] / tA["BFS"], 1)
    m["TempoTotalDesempenho"] = br(amb["tempo_total_s"] / 60, 0)
    comp = rob["direcionado_composicao"]
    n_rest = rob["n"] - rob["r"]
    m["Descoberta"] = (
        f"A conectividade da rede depende de um núcleo pequeno de vértices. Os "
        f"{br(rob['r'])} vértices de maior grau (grau $\\ge$ {comp['grau_minimo_removido']}; "
        f"{br(comp['removidos_usuarios'])} usuários e {br(comp['removidos_cervejas'])} cervejas) concentram "
        f"{pct(comp['arestas_incidentes_removidas_frac'])} da soma dos graus. Ao removê-los, "
        f"{br(comp['isolados_total'])} vértices ({pct(comp['isolados_total'] / n_rest)} dos restantes) ficam "
        f"isolados, dos quais {br(comp['isolados_cervejas'])} são cervejas: todos os avaliadores dessas "
        f"cervejas pertencem ao grupo dos usuários mais ativos. Em outras palavras, a maior parte do "
        f"catálogo só está ligada ao restante da rede por um grupo de cerca de "
        f"{br(comp['removidos_usuarios'])} usuários muito ativos.")
    with open(os.path.join(OUT, "numeros.tex"), "w", encoding="utf-8") as f:
        f.write("% gerado por src/gerar_artigo.py -- nao editar\n")
        for k, v in m.items():
            f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

    # ------------------------------------------------ Tabela Parte I
    linhas = [
        ("Número de vértices", br(p1["vertices"]), "sim", "contagem"),
        ("Número de arestas", br(p1["arestas"]), "sim", "contagem"),
        ("Grau mínimo / máximo / médio", f"{p1['graus_todos']['min']} / {br(p1['graus_todos']['max'])} / "
         f"{br(p1['graus_todos']['medio'], 2)}", "sim", "exato"),
        ("Distribuição de graus", "Fig.~\\ref{fig:graus}", "sim", "exato"),
        ("Densidade", "$" + sci(p1["densidade"]) + "$", "sim", "exato"),
        ("Número de componentes conexas", br(p1["num_componentes"]), "sim", "BFS"),
        ("Tamanho de cada componente", f"1$\\times${br(p1['mcc_vertices'])}; {len(pequenas)}$\\times$2",
         "sim", "BFS"),
        ("Diâmetro (MCC)", str(dist["diametro"]), "sim", "exato"),
        ("Raio (MCC)", str(dist["raio"]), "sim", "exato"),
        ("Comprimento médio dos caminhos (MCC)", br(dist["comprimento_medio_exato"], 3), "sim",
         "exato ($|V|$ BFS)"),
        ("Coeficiente de clusterização médio", br(p1["clusterizacao_media"], 1), "sim", "exato"),
        ("Número de triângulos", br(p1["triangulos"]), "sim", "exato"),
        ("Visualização", "Fig.~\\ref{fig:viz}", "sim", "amostra"),
    ]
    with open(os.path.join(OUT, "tab_parte1.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Parte I: medidas pedidas, se foram computadas e como.}\n"
                "\\label{tab:parte1}\n\\small\n\\begin{tabular}{p{3.3cm}lcl}\n\\toprule\n"
                "Medida & Valor & Comp.? & Obtenção \\\\\n\\midrule\n")
        for a, b, c, d in linhas:
            f.write(f"{a} & {b} & {c} & {d} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela resultados Parte II
    linhas = [
        ("BFS", f"origem sorteada: excentricidade {p2['bfs_excentricidade_origem']}"),
        ("DFS", f"{br(p2['dfs_arvores_no_grafo_completo'])} árvores no grafo completo"),
        ("Eulerianidade", f"não; {br(p2['euler_grafo_completo']['vertices_grau_impar'])} vértices de grau ímpar"),
        ("Dijkstra", f"mesma origem: dist. máx. {br(p2['dijkstra_dist_max'], 2)}, média {br(p2['dijkstra_dist_media'], 2)}"),
        ("Bellman-Ford", f"sem ciclo negativo; igual a Dijkstra; {p2['bellman_ford_passadas_ate_estabilizar']} passadas"),
        ("Floyd-Warshall", "só em amostras ($\\le 400$ vértices)"),
        ("Tarjan", f"{br(p2['tarjan_articulacoes'])} articulações; {br(p2['tarjan_pontes'])} pontes"),
        ("Prim", f"AGM: {br(p2['agm_arestas'][0])} arestas, peso {br(p2['agm_peso_prim'], 2)}"),
        ("Kruskal", f"AGM: {br(p2['agm_arestas'][1])} arestas, peso {br(p2['agm_peso_kruskal'], 2)}"),
    ]
    with open(os.path.join(OUT, "tab_parte2_resultados.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Parte II: resultado de cada algoritmo na MCC "
                f"($|V|={br(p2['V_mcc'])}$, $|E|={br(p2['E_mcc'])}$).}}\n\\label{{tab:p2res}}\n\\small\n"
                "\\begin{tabular}{lp{5.4cm}}\n\\toprule\nAlgoritmo & Resultado \\\\\n\\midrule\n")
        for a, b in linhas:
            f.write(f"{a} & {b} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela tempos (experimento A)
    with open(os.path.join(OUT, "tab_parte2_tempos.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Tempo real na MCC: média, desvio padrão e IC de 95\\% "
                "(Z para $R=30$; t-Student para $R=10$).}\n\\label{tab:p2tempo}\n\\small\n"
                "\\begin{tabular}{lrrrc}\n\\toprule\nAlgoritmo & $R$ & Média (s) & DP (s) & IC 95\\% (s) \\\\\n"
                "\\midrule\n")
        for r in resumo_t:
            if r["experimento"] != "A":
                continue
            nome = r["algoritmo"].replace("Bellman-Ford (parada antecipada)", "Bellman-Ford$^{*}$")
            f.write(f"{nome} & {r['n']} & {br(float(r['media']), 3)} & {br(float(r['desvio_padrao']), 3)} & "
                    f"[{br(float(r['ic_inf']), 3)}; {br(float(r['ic_sup']), 3)}] ({r['distribuicao']}) \\\\\n")
        f.write("\\bottomrule\n\\multicolumn{5}{l}{\\footnotesize $^{*}$ com parada antecipada.}\n"
                "\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela expoentes
    with open(os.path.join(OUT, "tab_parte2_expoentes.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Inclinação de $\\log(\\text{tempo})$ contra $\\log f(V,E)$ "
                "(custo teórico; esperado $\\approx 1$) e contra $\\log V$, no experimento B.}\n"
                "\\label{tab:p2exp}\n\\small\n\\begin{tabular}{llrr}\n\\toprule\n"
                "Algoritmo & $f(V,E)$ & vs.\\ $f$ & vs.\\ $V$ \\\\\n\\midrule\n")
        custo_tex = {"BFS": "V+E", "DFS": "V+E", "Euler": "V+E", "Tarjan": "V+E",
                     "Dijkstra": "(V+E)\\log V", "Prim": "E\\log V", "Kruskal": "E\\log V",
                     "Bellman-Ford": "VE", "Floyd-Warshall": "V^3"}
        for nome, e in exp["expoentes"].items():
            f.write(f"{nome} & ${custo_tex[nome]}$ & "
                    f"{br(e['inclinacao_vs_custo_teorico'], 2)} & {br(e['inclinacao_vs_V'], 2)} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela small-world
    max_ic = max(r["L_estimado"]["ic_sup"] - r["L_estimado"]["media"] for r in sw["modelos"].values())
    with open(os.path.join(OUT, "tab_smallworld.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Small-world: grafo real (MCC, $L$ exato) e modelos com o mesmo "
                "$n$ ($L$ estimado com 200 origens; meia-largura do IC 95\\% $\\le " + br(max_ic, 2) + "$).}\n"
                "\\label{tab:sw}\n\\small\n\\begin{tabular}{lrrr}\n\\toprule\n"
                "Grafo & $L$ & $C$ & grau máx. \\\\\n\\midrule\n")
        f.write(f"BeerAdvocate & {br(dist['comprimento_medio_exato'], 3)} & {br(p1['clusterizacao_media'], 1)} & "
                f"{br(p1['graus_todos']['max'])} \\\\\n")
        f.write(f"ER (aproximação) & {br(sw['L_ER_formula_ln_n_sobre_ln_k'], 3)} & "
                f"${sci(sw['C_ER_formula_k_sobre_n'])}$ & -- \\\\\n")
        nomes = {"Erdos-Renyi G(n,m)": "Erd\\H{o}s--Rényi", "Bipartido aleatorio (mesmos graus)":
                 "Bipartido aleat."}
        for nome, r in sw["modelos"].items():
            rot = nomes.get(nome, nome.replace("Barabasi-Albert", "Barabási--Albert")
                            .replace("Watts-Strogatz", "Watts--Strogatz").replace("m0", "$m_0$"))
            f.write(f"{rot} & {br(r['L_estimado']['media'], 3)} & {br(r['C_medio'], 4)} & "
                    f"{br(r['grau_max'])} \\\\\n")
        f.write("\\midrule\n")
        f.write(f"\\multicolumn{{4}}{{l}}{{$cc_\\bullet$ (Latapy): grafo {br(sw['latapy_G']['media'], 4)} "
                f"$\\pm$ {br(sw['latapy_G']['ic_sup'] - sw['latapy_G']['media'], 4)}; "
                f"bip. aleat. {br(sw['latapy_bipartido_aleatorio']['media'], 4)} $\\pm$ "
                f"{br(sw['latapy_bipartido_aleatorio']['ic_sup'] - sw['latapy_bipartido_aleatorio']['media'], 4)}}} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela lei de potencia
    with open(os.path.join(OUT, "tab_potencia.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Ajuste de lei de potência ($\\hat\\gamma \\pm$ erro padrão) e "
                "razão de verossimilhança normalizada $R$ (lei de potência vs.\\ alternativa; $R<0$ favorece a "
                "alternativa).}\n\\label{tab:pl}\n\\small\n\\begin{tabular}{lrrr}\n\\toprule\n"
                " & Todos & Usuários & Cervejas \\\\\n\\midrule\n")
        g = [pl[k] for k in ("todos", "usuarios", "cervejas")]
        f.write("$\\hat\\gamma$ & " + " & ".join(
            f"{br(x['proprio_kmin_por_KS']['gamma'], 3)} $\\pm$ {br(x['proprio_kmin_por_KS']['erro_padrao'], 3)}"
            for x in g) + " \\\\\n")
        f.write("$k_{\\min}$ (KS) & " + " & ".join(str(x["proprio_kmin_por_KS"]["k_min"]) for x in g) + " \\\\\n")
        f.write("vértices na cauda & " + " & ".join(br(x["proprio_kmin_por_KS"]["n_cauda"]) for x in g) + " \\\\\n")
        f.write("distância KS & " + " & ".join(br(x["proprio_kmin_por_KS"]["ks"], 3) for x in g) + " \\\\\n")
        f.write("$\\alpha$ (\\texttt{powerlaw}) & " + " & ".join(br(x["powerlaw_pkg_alpha_mesmo_kmin"], 3)
                                                                for x in g) + " \\\\\n")
        rot = {"exponential": "$R$ vs.\\ exponencial", "lognormal": "$R$ vs.\\ lognormal",
               "truncated_power_law": "$R$ vs.\\ l.p.\\ truncada"}
        for alt, nome in rot.items():
            f.write(f"{nome} & " + " & ".join(
                f"{br(x['comparacao_razao_verossimilhanca'][alt]['R'], 1)}" for x in g) + " \\\\\n")
        pmax = max(x["comparacao_razao_verossimilhanca"][a]["p"] for x in g for a in rot)
        f.write("\\bottomrule\n" f"\\multicolumn{{4}}{{l}}{{\\footnotesize Em todos os testes, $p \\le {sci(pmax, 1)}$.}}\n"
                "\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela robustez
    nomes = [("A_maior_componente", "A: maior componente", 0), ("A_S_fracao_restantes", "A: $S$", 4),
             ("B_num_componentes", "B: componentes", 1), ("C_dist_media_maior_comp", "C: distância média", 3),
             ("C_dist_max_observada", "C: maior dist. observada", 1), ("D_fracao_isolados", "D: fração isolados", 4)]
    with open(os.path.join(OUT, "tab_robustez.tex"), "w", encoding="utf-8") as f:
        f.write("\\begin{table}[t]\n\\caption{Robustez na MCC ($n=" + br(rob["n"]) + "$, $r=" + br(rob["r"]) +
                "$): remoção aleatória ($T=30$, média $\\pm$ DP) e remoção dos $r$ "
                "vértices de maior grau. As métricas C são estimadas com BFS a partir de 100 origens.}\n\\label{tab:rob}\n\\small\n\\begin{tabular}{lrrr}\n\\toprule\n"
                "Métrica & Sem remoção & Aleatória & Por grau \\\\\n\\midrule\n")
        for chave, rot, c in nomes:
            a = rob["aleatoria"][chave]
            f.write(f"{rot} & {br(rob['sem_remocao'][chave], c)} & {br(a['media'], c)} $\\pm$ "
                    f"{br(a['desvio_padrao'], c)} & {br(rob['direcionado_grau'][chave], c)} \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
    print("ok")


if __name__ == "__main__":
    main()
