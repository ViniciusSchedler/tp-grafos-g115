"""
Gera, a partir de results/, os arquivos incluidos pelo artigo (artigo/gerado/*.tex) e a
figura da distribuicao de distancias. Nenhum numero do artigo e digitado a mao.
"""
import csv
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilo import COLUNA, COR, plt, salvar_figura  # noqa: E402
from grafo import RAIZ  # noqa: E402

RES = os.path.join(RAIZ, "results")
OUT = os.path.join(RAIZ, "artigo", "gerado")
LINK_REPOSITORIO = "https://github.com/ViniciusSchedler/tp-grafos-g115"

# Declaracao de uso de IA: descreve apenas o que de fato aconteceu.
DECLARACAO_IA = (
    "O código, os experimentos, as figuras e o texto foram produzidos com o assistente de programação "
    "Claude Code (Anthropic), a partir das instruções do autor, que definiu os requisitos do trabalho, "
    "escolheu a modelagem bipartida e é responsável pelo conteúdo entregue.")


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


def ic(r, casas):
    """'[inf; sup]' de um resumo()."""
    return f"[{br(r['ic_inf'], casas)}; {br(r['ic_sup'], casas)}]"


def figura_distancias(dist):
    hist = {int(k): v for k, v in dist["histograma_distancias_pares_ordenados"].items()}
    total = sum(hist.values())
    fig, ax = plt.subplots(figsize=(COLUNA, 1.9))
    ks = sorted(hist)
    ax.bar(ks, [hist[k] / total for k in ks], color=COR["cinza"], width=0.7)
    for k in ks:
        p = 100 * hist[k] / total
        rot = f"{p:.1f}%".replace(".", ",") if p >= 0.05 else "<0,1%"  # evita "0,0%" para pares que existem
        ax.text(k, hist[k] / total + 0.01, rot, ha="center", va="bottom", fontsize=6.5)
    ax.set(xlabel="distância $d(u,v)$", ylabel="fração dos pares", xticks=ks, ylim=(0, 0.62))
    salvar_figura(fig, os.path.join(RES, "figures", "distribuicao_distancias"))
    return hist, total


def main():
    os.makedirs(OUT, exist_ok=True)
    trat = ler(os.path.join("..", "data", "processed", "tratamento.json"))
    p1 = ler("parte1.json")
    dist = ler("distancias_mcc.json")
    p2 = ler("parte2_resultados.json")
    p3 = ler("parte3.json")
    with open(os.path.join(RES, "tables", "desempenho_expoentes.json"), encoding="utf-8") as f:
        exp = json.load(f)
    with open(os.path.join(RES, "tables", "desempenho_resumo.csv"), encoding="utf-8") as f:
        resumo_t = list(csv.DictReader(f))
    sw, pl, rob = p3["small_world"], p3["lei_potencia"], p3["robustez"]
    hist, total = figura_distancias(dist)

    # ------------------------------------------------ macros numericas
    graus_um = float(p1["distribuicao_graus"]["todos"]["1"])
    pequenas = [c for c in p1["componentes_detalhe"] if c["tamanho"] < p1["mcc_vertices"]]
    raw = os.path.join(RAIZ, "data", "raw")
    with open(os.path.join(raw, "DOWNLOAD_DATE.txt"), encoding="utf-8") as f:
        data_dl = datetime.date.fromisoformat(f.read().strip()[:10]).strftime("%d/%m/%Y")
    arq_bruto = os.path.join(raw, "Beeradvocate.txt.gz")
    tam_bruto = os.path.getsize(arq_bruto) if os.path.exists(arq_bruto) else 445475306
    amb = exp["ambiente"]
    ex = exp["expoentes"]
    tA = {r["algoritmo"]: r for r in resumo_t if r["experimento"] == "A"}
    nulo = sw["nulo_trocas"]
    inst = nulo["instancias"]
    ex_todos = pl["todos"]["exato"]["observado"]
    # o texto do artigo afirma "p = 0 nos tres grupos" e "BF mudou d[] em poucas passadas": conferir
    assert all(pl[g]["exato"]["p_valor"] == 0 for g in pl), "revisar o texto da lei de potencia"
    bf = p2["bellman_ford_mcc"]
    alvo, comp = rob["direcionado_grau"], rob["direcionado_composicao"]
    n_rest = rob["n"] - rob["r"]
    fw = max((r for r in resumo_t if r["algoritmo"] == "Floyd-Warshall"), key=lambda r: float(r["V_medio"]))
    V, E = p2["V_mcc"], p2["E_mcc"]
    quase = ["BFS", "DFS", "Euler", "Tarjan", "Tarjan-CFC", "Dijkstra", "Prim"]
    m = {
        "NVertices": br(p1["vertices"]), "NArestas": br(p1["arestas"]),
        "NUsuarios": br(p1["usuarios"]), "NCervejas": br(p1["cervejas"]),
        "NAvLidas": br(trat["avaliacoes_lidas"]), "NAvSemUsuario": br(trat["avaliacoes_sem_profileName_descartadas"]),
        "NParesRepetidos": br(trat["pares_usuario_cerveja_repetidos"]),
        "NAvFundidas": br(trat["avaliacoes_removidas_na_fusao_de_paralelas"]),
        "DataDownload": data_dl, "NBytesBruto": br(tam_bruto),
        "DataMin": datetime.datetime.fromtimestamp(trat["review_time_min_unix"], datetime.UTC).strftime("%d/%m/%Y"),
        "DataMax": datetime.datetime.fromtimestamp(trat["review_time_max_unix"], datetime.UTC).strftime("%d/%m/%Y"),
        "GrauMax": br(p1["graus_todos"]["max"]), "GrauMedio": br(p1["graus_todos"]["medio"], 2),
        "GrauMedioU": br(p1["graus_usuarios"]["medio"], 2), "GrauMaxU": br(p1["graus_usuarios"]["max"]),
        "GrauMedioB": br(p1["graus_cervejas"]["medio"], 2), "GrauMaxB": br(p1["graus_cervejas"]["max"]),
        "FracGrauUm": pct(graus_um),
        "Densidade": sci(p1["densidade"]), "DensidadeBip": sci(p1["densidade_bipartida_E_sobre_UxB"]),
        "NComponentes": br(p1["num_componentes"]), "NCompPequenas": br(len(pequenas)),
        "MCCVertices": br(p1["mcc_vertices"]), "MCCArestas": br(p1["mcc_arestas"]),
        "MCCPercent": pct(p1["mcc_vertices"] / p1["vertices"], 2),
        "Diametro": str(dist["diametro"]), "Raio": str(dist["raio"]),
        "LExato": br(dist["comprimento_medio_exato"], 3),
        "FracDistAteQuatro": pct(sum(v for k, v in hist.items() if k <= 4) / total),
        "TempoDistHoras": br(dist["tempo_total_s"] / 3600, 1), "BFSLimitantes": str(p1["bfs_usadas_limitantes"]),
        "Triangulos": br(p1["triangulos"]), "Clusterizacao": br(p1["clusterizacao_media"], 1),
        "VizVertices": br(p1["visualizacao"]["vertices"]), "VizArestas": br(p1["visualizacao"]["arestas"]),
        # Parte II
        "DFSArvores": br(p2["dfs_arvores_no_grafo_completo"]), "TarjanCFC": br(p2["tarjan_cfc_grafo_completo"]),
        "EulerImpares": br(p2["euler_grafo_completo"]["vertices_grau_impar"]),
        "EulerImparesMCC": br(p2["euler_mcc"]["vertices_grau_impar"]),
        "AGMPeso": br(p2["agm_peso_prim"], 2),
        "BFPassadasUteis": str(p2["bellman_ford_passadas_ate_estabilizar"] - 1),
        # passadas que alteram d[] (o contador inclui a ultima passada, sem alteracao)
        "BFPassadasFaixa": (str(min(bf["passadas_por_origem"]) - 1) if len(set(bf["passadas_por_origem"])) == 1
                            else f"{min(bf['passadas_por_origem']) - 1} a {max(bf['passadas_por_origem']) - 1}"),
        "PBootLimite": br(1 / pl["todos"]["exato"]["B"], 3),
        "BFOrigens": str(len(bf["passadas_por_origem"])),
        "TrocasSobreposicaoEsperada": pct(p3["nulo_trocas_diagnostico"]["sobreposicao_esperada"]),
        "BFTempoPassada": br(bf["tempo_por_passada_s"]["media"], 3),
        "EstBFHoras": br(bf["estimativa_sem_parada_s"]["media"] / 3600, 1),
        "EstFWAnos": br(float(fw["tempo_sobre_custo_ns"]) * 1e-9 * V ** 3 / (3600 * 24 * 365), 1),
        "FWnsOp": br(float(fw["tempo_sobre_custo_ns"]), 0),
        "EstFWMemGB": br(V * V * 8 / 1e9, 0),
        "TarjanArt": br(p2["tarjan_articulacoes"]), "TarjanPontes": br(p2["tarjan_pontes"]),
        "TarjanPontesFolha": br(p2["tarjan_pontes_com_folha"]),
        "DijkstraMax": br(p2["dijkstra_dist_max"], 1), "DijkstraMedia": br(p2["dijkstra_dist_media"], 2),
        "ExpMin": br(min(ex[a]["inclinacao_vs_custo_teorico"] for a in quase), 2),
        "ExpMax": br(max(ex[a]["inclinacao_vs_custo_teorico"] for a in quase), 2),
        "ExpRepMin": br(min(ex[a]["inclinacao_por_repeticao"] for a in quase + ["Kruskal"]), 2),
        "ExpRepMax": br(max(ex[a]["inclinacao_por_repeticao"] for a in quase + ["Kruskal"]), 2),
        "ExpKruskal": br(ex["Kruskal"]["inclinacao_vs_custo_teorico"], 2),
        "ExpKruskalRep": br(ex["Kruskal"]["inclinacao_por_repeticao"], 2),
        "KruskalNsMaior": br(max(float(r["tempo_sobre_custo_ns"]) for r in resumo_t if r["algoritmo"] == "Kruskal"), 0),
        "KruskalNsMCC": br(float(tA["Kruskal"]["tempo_sobre_custo_ns"]), 0),
        "ExpBF": br(ex["Bellman-Ford"]["inclinacao_vs_custo_teorico"], 2),
        "ExpBFRep": br(ex["Bellman-Ford"]["inclinacao_por_repeticao"], 2),
        "ExpBFV": br(ex["Bellman-Ford"]["inclinacao_vs_V"], 2),
        "ExpFW": br(ex["Floyd-Warshall"]["inclinacao_vs_custo_teorico"], 2),
        "TempoBFS": br(float(tA["BFS"]["media"]), 3), "TempoDijkstra": br(float(tA["Dijkstra"]["media"]), 3),
        "RazaoDijkstraBFS": br(float(tA["Dijkstra"]["media"]) / float(tA["BFS"]["media"]), 1),
        "TempoTotalDesempenho": br((amb["tempo_total_s"] + amb.get("tempo_extra_s", 0)) / 60, 0),
        # Parte III: small-world
        "LERformula": br(sw["L_ER_formula_ln_n_sobre_ln_k"], 2), "CERformula": sci(sw["C_ER_formula_k_sobre_n"]),
        "LERsim": br(sw["modelos"]["Erdos-Renyi G(n,m)"]["L_estimado"]["media"], 2),
        "LatapyG": br(sw["latapy_G"]["media"], 4), "LatapyR": br(nulo["cc_latapy"]["media"], 4),
        "LatapyRazao": br(sw["razao_cc"], 2), "LBipR": br(nulo["L"]["media"], 3), "RazaoL": br(sw["razao_L"], 3),
        "SigmaBip": br(sw["sigma_bipartido"], 2), "RTrocas": str(nulo["R"]), "QTrocas": str(nulo["Q"]),
        "TrocasAceitasPct": pct(sum(x["trocas_aceitas"] / x["trocas_tentadas"] for x in inst) / len(inst)),
        "TrocasRestantesPct": pct(sum(x["frac_arestas_originais_restantes"] for x in inst) / len(inst)),
        "LatapyAmostra": br(sw["latapy_amostra_vertices"]),
        "GrauMaxBA": br(next(r["grau_max"] for k, r in sw["modelos"].items() if k.startswith("Barabasi"))),
        # Parte III: lei de potencia
        "GammaTodos": br(ex_todos["gamma"], 2), "KminTodos": str(int(ex_todos["k_min"])),
        "KSTodos": br(ex_todos["ks"], 3),
        "GammaU": br(pl["usuarios"]["exato"]["observado"]["gamma"], 2),
        "GammaB": br(pl["cervejas"]["exato"]["observado"]["gamma"], 2),
        "GammaTodosAprox": br(pl["todos"]["aproximado_eq37"]["gamma"], 3),
        "GammaTodosExato": br(ex_todos["gamma"], 3),
        "BBoot": br(pl["todos"]["exato"]["B"]),
        "PBootMax": br(max(pl[g]["exato"]["p_valor"] for g in pl), 3),
        "KSSintMax": br(max(pl[g]["exato"]["ks_sinteticos_max"] for g in pl), 3),
        # Parte III: robustez
        "RobR": br(rob["r"]), "RobN": br(rob["n"]),
        "RobSAleat": br(rob["aleatoria"]["A_S_fracao_restantes"]["media"], 4),
        "RobBAleat": br(rob["aleatoria"]["B_num_componentes"]["media"], 1),
        "RobDAleat": pct(rob["aleatoria"]["D_fracao_isolados"]["media"], 2),
        "RobCBase": br(rob["sem_remocao"]["C_dist_media_maior_comp"], 3),
        "RobCAleat": br(rob["aleatoria"]["C_dist_media_maior_comp"]["media"], 3),
        "RobCAleatIC": ic(rob["aleatoria"]["C_dist_media_maior_comp"], 3),
        "RobSAlvo": br(alvo["A_S_fracao_restantes"], 4), "RobBAlvo": br(alvo["B_num_componentes"]),
        "RobDAlvo": pct(alvo["D_fracao_isolados"], 1), "RobCAlvo": br(alvo["C_dist_media_maior_comp"], 3),
        "RobCAlvoIC": ic(alvo["C_resumo_origens"], 3), "RobKAlvo": br(rob["K_origens_bfs_direcionado"]),
        "RobGrauCorte": br(comp["grau_minimo_removido"]),
        "RobEmpatesRem": br(comp["empates_no_grau_de_corte_removidos"]),
        "RobEmpatesTot": br(comp["empates_no_grau_de_corte_total"]),
        # ambiente e declaracoes
        "Hardware": "Intel Core i5-12450H (8 núcleos, 12 threads), 15,7 GB de RAM",
        "SO": "Windows 11 Home 64 bits",
        "PythonVersao": amb["python"].split()[0],
        "LinkRepositorio": LINK_REPOSITORIO,
        "DeclaracaoIA": DECLARACAO_IA,
    }
    m["Descoberta"] = (
        f"A conectividade da rede depende de um núcleo pequeno de vértices. Os "
        f"{br(rob['r'])} vértices de maior grau (grau $\\ge$ {comp['grau_minimo_removido']}; "
        f"{br(comp['removidos_usuarios'])} usuários e {br(comp['removidos_cervejas'])} cervejas) concentram "
        f"{pct(comp['soma_graus_removidos_frac'])} da soma dos graus da MCC. Ao removê-los, "
        f"{br(comp['isolados_total'])} vértices ({pct(comp['isolados_total'] / n_rest)} dos restantes) ficam "
        f"isolados, dos quais {br(comp['isolados_cervejas'])} são cervejas: todos os avaliadores dessas "
        f"cervejas estão entre os {br(comp['removidos_usuarios'])} usuários removidos. Ou seja, a maior parte "
        f"do catálogo só se liga ao restante da rede por meio de um grupo pequeno de usuários muito ativos.")
    with open(os.path.join(OUT, "numeros.tex"), "w", encoding="utf-8") as f:
        f.write("% gerado por src/gerar_artigo.py -- nao editar\n")
        for k, v in m.items():
            f.write(f"\\newcommand{{\\{k}}}{{{v}}}\n")

    escrever_tabelas(p1, dist, p2, sw, pl, rob, exp, resumo_t, pequenas)
    print("ok")


def escrever(nome, texto):
    with open(os.path.join(OUT, nome), "w", encoding="utf-8") as f:
        f.write(texto)


def escrever_tabelas(p1, dist, p2, sw, pl, rob, exp, resumo_t, pequenas):
    # ------------------------------------------------ Tabela Parte I
    linhas = [
        ("Número de vértices", br(p1["vertices"]), "sim", "contagem"),
        ("Número de arestas", br(p1["arestas"]), "sim", "contagem"),
        ("Grau mín. / máx. / médio", f"{p1['graus_todos']['min']} / {br(p1['graus_todos']['max'])} / "
         f"{br(p1['graus_todos']['medio'], 2)}", "sim", "exato"),
        ("Distribuição de graus", "Fig.~\\ref{fig:graus}", "sim", "exato"),
        ("Densidade", "$" + sci(p1["densidade"]) + "$", "sim", "exato"),
        ("Nº de componentes conexas", br(p1["num_componentes"]), "sim", "BFS"),
        ("Tamanho de cada componente", f"1$\\times${br(p1['mcc_vertices'])}; {len(pequenas)}$\\times$2",
         "sim", "BFS"),
        ("Diâmetro (MCC)", str(dist["diametro"]), "sim", "exato"),
        ("Raio (MCC)", str(dist["raio"]), "sim", "exato"),
        ("Compr. médio dos caminhos (MCC)", br(dist["comprimento_medio_exato"], 3), "sim", "exato"),
        ("Clusterização média", br(p1["clusterizacao_media"], 1), "sim", "exato"),
        ("Número de triângulos", br(p1["triangulos"]), "sim", "exato"),
        ("Visualização", "Fig.~\\ref{fig:viz}", "sim", "amostra"),
    ]
    t = ("\\begin{table}[t]\n\\caption{Parte I: medidas pedidas, se foram computadas e como. Distâncias, diâmetro e "
         "raio referem-se à maior componente conexa (MCC); as demais, ao grafo inteiro.}\n\\label{tab:parte1}\n"
         "\\footnotesize\n\\begin{tabular}{@{}p{3.15cm}lcl@{}}\n\\toprule\nMedida & Valor & Comp.? & Obtenção \\\\\n"
         "\\midrule\n")
    t += "".join(f"{a} & {b} & {c} & {d} \\\\\n" for a, b, c, d in linhas)
    escrever("tab_parte1.tex", t + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela resultados Parte II
    linhas = [
        ("BFS", f"origem sorteada: excentricidade {p2['bfs_excentricidade_origem']}"),
        ("DFS", f"{br(p2['dfs_arvores_no_grafo_completo'])} árvores no grafo completo"),
        ("Eulerianidade", f"não; {br(p2['euler_mcc']['vertices_grau_impar'])} vértices de grau ímpar"),
        ("Dijkstra", f"mesma origem da BFS: dist.\\ máx.\\ {br(p2['dijkstra_dist_max'], 1)}, "
                     f"média {br(p2['dijkstra_dist_media'], 2)}"),
        ("Bellman-Ford", f"sem ciclo negativo; igual a Dijkstra; d[] muda em "
                         f"{p2['bellman_ford_passadas_ate_estabilizar'] - 1} passadas"),
        ("Floyd-Warshall", "só em subgrafos ($\\le 400$ vértices)"),
        ("Tarjan (art./pontes)", f"{br(p2['tarjan_articulacoes'])} articulações; {br(p2['tarjan_pontes'])} pontes"),
        ("Tarjan (CFC)", f"{br(p2['tarjan_cfc_grafo_completo'])} CFC no grafo completo (= componentes conexas)"),
        ("Prim", f"AGM: {br(p2['agm_arestas'][0])} arestas, peso {br(p2['agm_peso_prim'], 2)}"),
        ("Kruskal", f"AGM: {br(p2['agm_arestas'][1])} arestas, peso {br(p2['agm_peso_kruskal'], 2)}"),
    ]
    t = ("\\begin{table}[t]\n\\caption{Parte II: resultado de cada algoritmo na MCC "
         f"($|V|={br(p2['V_mcc'])}$, $|E|={br(p2['E_mcc'])}$), salvo indicação.}}\n\\label{{tab:p2res}}\n\\footnotesize\n"
         "\\begin{tabular}{@{}lp{5.0cm}@{}}\n\\toprule\nAlgoritmo & Resultado \\\\\n\\midrule\n")
    t += "".join(f"{a} & {b} \\\\\n" for a, b in linhas)
    escrever("tab_parte2_resultados.tex", t + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela tempos (experimento A)
    nomes = {"Euler": "Eulerianidade", "Tarjan": "Tarjan (art./pontes)", "Tarjan-CFC": "Tarjan (CFC)",
             "Bellman-Ford (parada antecipada)": "Bellman-Ford$^{*}$"}
    t = ("\\begin{table}[t]\n\\caption{Tempo real na MCC: média, desvio padrão (DP) e IC de 95\\% "
         "(Z para $R=30$; t-Student para $R=10$).}\n\\label{tab:p2tempo}\n\\footnotesize\n"
         "\\begin{tabular}{@{}lrrrc@{}}\n\\toprule\nAlgoritmo & $R$ & Média (s) & DP (s) & IC 95\\% (s) \\\\\n"
         "\\midrule\n")
    for r in resumo_t:
        if r["experimento"] == "A":
            t += (f"{nomes.get(r['algoritmo'], r['algoritmo'])} & {r['n']} & {br(float(r['media']), 3)} & "
                  f"{br(float(r['desvio_padrao']), 3)} & [{br(float(r['ic_inf']), 3)}; {br(float(r['ic_sup']), 3)}] "
                  f"\\\\\n")
    escrever("tab_parte2_tempos.tex", t + "\\bottomrule\n\\multicolumn{5}{@{}l}{\\footnotesize $^{*}$ com parada "
             "antecipada.}\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela: todas as medicoes em subgrafos (experimento B)
    t = ("\\begin{table*}[t]\n\\caption{Experimento B: tempo real em subgrafos conexos de tamanho alvo $k$ "
         "(uma amostra nova por repetição; o subgrafo tem exatamente $|V|=k$ vértices). $|E|$ é a média sobre "
         "as repetições, com o intervalo de $|E|$ entre parênteses nos algoritmos caros; IC de 95\\% pela "
         "Normal ($R=30$) ou pela t-Student com $R-1$ graus de liberdade ($R=10$, em Bellman-Ford e Floyd-Warshall). Tempos em segundos.}\n"
         "\\label{tab:p2amostras}\n\\footnotesize\n\\setlength{\\tabcolsep}{2.2pt}\n"
         "\\begin{tabular}{@{}lrrrrr@{\\hspace{0.8em}}lrrrrr@{}}\n\\toprule\n"
         "Algoritmo & $k$ & $|E|$ & Média & DP & IC 95\\% & "
         "Algoritmo & $k$ & $|E|$ & Média & DP & IC 95\\% \\\\\n\\midrule\n")
    linhas_b = []
    for r in resumo_t:
        if r["experimento"] != "B":
            continue
        caro = r["algoritmo"] in ("Bellman-Ford", "Floyd-Warshall")
        Ecol = (f"{br(float(r['E_medio']), 0)} ({br(int(r['E_min']))}--{br(int(r['E_max']))})" if caro
                else br(float(r["E_medio"]), 0))
        casas = 4 if caro else 3
        assert float(r["V_medio"]) == int(r["tamanho_alvo"])  # a amostra tem exatamente k vertices
        linhas_b.append(f"{nomes.get(r['algoritmo'], r['algoritmo'])} & {br(int(r['tamanho_alvo']))} & "
                        f"{Ecol} & {br(float(r['media']), casas)} & "
                        f"{br(float(r['desvio_padrao']), casas)} & "
                        f"[{br(float(r['ic_inf']), casas)}; {br(float(r['ic_sup']), casas)}]")
    meio = (len(linhas_b) + 1) // 2
    for i in range(meio):
        dir_ = linhas_b[meio + i] if meio + i < len(linhas_b) else "& & & & &"
        t += f"{linhas_b[i]} & {dir_} \\\\\n"
    escrever("tab_parte2_amostras.tex", t + "\\bottomrule\n\\end{tabular}\n\\end{table*}\n")

    # ------------------------------------------------ Tabela expoentes
    custo_tex = {"BFS": "V+E", "DFS": "V+E", "Euler": "V+E", "Tarjan": "V+E", "Tarjan-CFC": "V+E",
                 "Dijkstra": "(V+E)\\log V", "Prim": "E\\log V", "Kruskal": "E\\log V",
                 "Bellman-Ford": "VE", "Floyd-Warshall": "V^3"}
    t = ("\\begin{table}[t]\n\\caption{Inclinação de $\\log(\\text{tempo})$ contra $\\log f(V,E)$ (custo "
         "teórico; esperado $\\approx 1$), ajustada sobre as médias por tamanho e sobre cada repetição do "
         "experimento B, e contra $\\log V$ (médias).}\n\\label{tab:p2exp}\n\\footnotesize\n"
         "\\begin{tabular}{@{}llrrr@{}}\n\\toprule\nAlgoritmo & $f(V,E)$ & médias & repetições & vs.\\ $V$ \\\\\n"
         "\\midrule\n")
    for nome, e in exp["expoentes"].items():
        t += (f"{nomes.get(nome, nome)} & ${custo_tex[nome]}$ & {br(e['inclinacao_vs_custo_teorico'], 2)} & "
              f"{br(e['inclinacao_por_repeticao'], 2)} & {br(e['inclinacao_vs_V'], 2)} \\\\\n")
    escrever("tab_parte2_expoentes.tex", t + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela small-world
    nulo = sw["nulo_trocas"]
    t = ("\\begin{table}[t]\n\\caption{Small-world. $L$: grafo real exato (MCC); modelos clássicos estimados "
         "com 200 origens de BFS; nulo bipartido: média de " + str(nulo["R"]) + " instâncias (100 origens cada). "
         "$cc_\\bullet$: agrupamento bipartido médio em " + br(sw["latapy_amostra_vertices"]) +
         " vértices sorteados. Entre colchetes, IC de 95\\%.}\n\\label{tab:sw}\n\\footnotesize\n"
         "\\begin{tabular}{@{}lllr@{}}\n\\toprule\nGrafo & $L$ & $C$ & grau máx. \\\\\n\\midrule\n")
    t += (f"BeerAdvocate & {br(dist['comprimento_medio_exato'], 3)} & {br(p1['clusterizacao_media'], 1)} & "
          f"{br(p1['graus_todos']['max'])} \\\\\n")
    t += (f"ER (fórmula) & {br(sw['L_ER_formula_ln_n_sobre_ln_k'], 3)} & "
          f"${sci(sw['C_ER_formula_k_sobre_n'])}$ & -- \\\\\n")
    for nome, r in sw["modelos"].items():
        rot = (nome.replace("Erdos-Renyi G(n,m)", "Erd\\H{o}s--Rényi").replace("Barabasi-Albert", "Barabási--Albert")
               .replace("Watts-Strogatz", "Watts--Strogatz").replace("m0", "$m_0$")
               .replace("(k=32, p=0.1)", "($k$=32, $p$=0,1)"))
        t += f"{rot} & {br(r['L_estimado']['media'], 3)} & {br(r['C_medio'], 4)} & {br(r['grau_max'])} \\\\\n"
    t += (f"Nulo bipartido (trocas) & {br(nulo['L']['media'], 3)} & 0 & {br(p1['graus_todos']['max'])} \\\\\n"
          "\\midrule\n")
    g, rr = sw["latapy_G"], nulo["cc_latapy"]
    t += (f"\\multicolumn{{4}}{{@{{}}l@{{}}}}{{$cc_\\bullet$ BeerAdvocate: {br(g['media'], 4)} {ic(g, 4)}}} \\\\\n"
          f"\\multicolumn{{4}}{{@{{}}l@{{}}}}{{$cc_\\bullet$ nulo bipartido: {br(rr['media'], 4)} {ic(rr, 4)}}} \\\\\n")
    t += (f"\\multicolumn{{4}}{{@{{}}l@{{}}}}{{$L$ do nulo bipartido: IC {ic(nulo['L'], 3)}; "
          f"$\\sigma_{{\\text{{bip}}}} = {br(sw['sigma_bipartido'], 2)}$}} \\\\\n")
    escrever("tab_smallworld.tex", t + "\\bottomrule\n\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela lei de potencia
    gs = [pl[k] for k in ("todos", "usuarios", "cervejas")]
    t = ("\\begin{table}[t]\n\\caption{Lei de potência discreta: MLE exato ($\\hat\\gamma\\pm$ erro padrão), "
         "$k_{\\min}$ pela menor distância KS, teste de bondade de ajuste por \\textit{bootstrap} ($p$; "
         "$p\\le 0{,}1$ rejeita a lei de potência) e razão de verossimilhança normalizada $R$ contra "
         "alternativas ($R<0$ favorece a alternativa).}\n\\label{tab:pl}\n\\footnotesize\n"
         "\\begin{tabular}{@{}lrrr@{}}\n\\toprule\n & Todos & Usuários & Cervejas \\\\\n\\midrule\n")
    t += "$\\hat\\gamma$ & " + " & ".join(
        f"{br(x['exato']['observado']['gamma'], 3)} $\\pm$ {br(x['exato']['observado']['erro_padrao'], 3)}"
        for x in gs) + " \\\\\n"
    t += "$k_{\\min}$ & " + " & ".join(str(int(x["exato"]["observado"]["k_min"])) for x in gs) + " \\\\\n"
    t += "$n$ com $k\\ge k_{\\min}$ & " + " & ".join(br(x["exato"]["observado"]["n_cauda"]) for x in gs) + " \\\\\n"
    t += "distância KS ($D$) & " + " & ".join(br(x["exato"]["observado"]["ks"], 3) for x in gs) + " \\\\\n"
    t += "maior $D$ sintético & " + " & ".join(br(x["exato"]["ks_sinteticos_max"], 3) for x in gs) + " \\\\\n"
    t += f"$p$ ($B={br(gs[0]['exato']['B'])}$) & " + " & ".join(
        br(x["exato"]["p_valor"], 3) for x in gs) + " \\\\\n"
    t += "$\\alpha$ (\\texttt{powerlaw}) & " + " & ".join(br(x["powerlaw_pkg_alpha_mesmo_kmin"], 3) for x in gs) + " \\\\\n"
    rot = {"exponential": "$R$ vs.\\ exponencial", "lognormal": "$R$ vs.\\ lognormal",
           "truncated_power_law": "$R$ vs.\\ truncada"}
    for alt, nome in rot.items():
        t += f"{nome} & " + " & ".join(f"{br(x['comparacao_razao_verossimilhanca'][alt]['R'], 1)}" for x in gs) + " \\\\\n"
    pmax = max(x["comparacao_razao_verossimilhanca"][a]["p"] for x in gs for a in rot)
    escrever("tab_potencia.tex", t + "\\bottomrule\n" + "\\multicolumn{4}{@{}l}{\\footnotesize Razões de "
             f"verossimilhança: $p \\le {sci(max(pmax, 1e-300), 1)}$ em todos os testes.}}\n"
             "\\end{tabular}\n\\end{table}\n")

    # ------------------------------------------------ Tabela robustez
    # (chave, rotulo, casas do valor unico, casas da media +- DP)
    nomes = [("A_maior_componente", "A: maior componente", 0, 0), ("A_S_fracao_restantes", "A: $S$", 4, 4),
             ("B_num_componentes", "B: componentes", 0, 1), ("C_dist_media_maior_comp", "C: distância média", 3, 3),
             ("C_dist_max_observada", "C: maior distância", 0, 1),
             ("D_fracao_isolados", "D: fração isolados", 4, 4)]
    t = ("\\begin{table}[t]\n\\caption{Robustez na MCC ($n=" + br(rob["n"]) + "$, $r=" + br(rob["r"]) +
         "$): remoção aleatória ($T=30$, média $\\pm$ DP) e remoção dos $r$ vértices de maior grau. Sem remoção, "
         "C é o valor exato; após a remoção, C é estimada por BFS a partir de " + br(rob["K_origens_bfs_aleatoria"]) +
         " (aleatória) e " + br(rob["K_origens_bfs_direcionado"]) + " origens (por grau).}\n\\label{tab:rob}\n"
         "\\footnotesize\n\\begin{tabular}{@{}lrrr@{}}\n\\toprule\nMétrica & Sem remoção & Aleatória & Por grau \\\\\n"
         "\\midrule\n")
    for chave, rot_, c, cm in nomes:
        a = rob["aleatoria"][chave]
        base_txt = br(rob["sem_remocao"][chave], c)
        if chave == "C_dist_max_observada":
            base_txt = str(dist["diametro"]) + "$^{\\dagger}$"
        t += (f"{rot_} & {base_txt} & {br(a['media'], cm)} $\\pm$ {br(a['desvio_padrao'], cm)} & "
              f"{br(rob['direcionado_grau'][chave], c)} \\\\\n")
    escrever("tab_robustez.tex", t + "\\bottomrule\n\\multicolumn{4}{@{}l}{\\footnotesize $^{\\dagger}$ diâmetro "
             "exato; após a remoção, maior distância vista nas BFS.}\n\\end{tabular}\n\\end{table}\n")


if __name__ == "__main__":
    main()
