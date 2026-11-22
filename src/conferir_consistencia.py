"""
Confere relacoes aritmeticas entre os resultados (avaliacoes, vertices, arestas, graus,
componentes e distancias). Nao recalcula nada caro: so cruza os arquivos de results/ e
data/processed/. Uso: python src/conferir_consistencia.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grafo import RAIZ, carregar_grafo  # noqa: E402


def ler(*partes):
    with open(os.path.join(RAIZ, *partes), encoding="utf-8") as f:
        return json.load(f)


def main():
    trat = ler("data", "processed", "tratamento.json")
    p1 = ler("results", "parte1.json")
    p2 = ler("results", "parte2_resultados.json")
    dist = ler("results", "distancias_mcc.json")
    p3 = ler("results", "parte3.json")
    adj, _, U = carregar_grafo()
    n, m = len(adj), sum(len(x) for x in adj) // 2
    graus = [len(x) for x in adj]
    checagens = [
        ("avaliacoes usadas = lidas - sem usuario",
         trat["avaliacoes_usadas"] == trat["avaliacoes_lidas"] - trat["avaliacoes_sem_profileName_descartadas"]),
        ("arestas = avaliacoes usadas - avaliacoes fundidas",
         trat["arestas_grafo_simples"] == trat["avaliacoes_usadas"] - trat["avaliacoes_removidas_na_fusao_de_paralelas"]),
        ("arestas do arquivo = arestas do tratamento = Parte I", m == trat["arestas_grafo_simples"] == p1["arestas"]),
        ("vertices = usuarios + cervejas", n == p1["vertices"] == U + p1["cervejas"] and U == p1["usuarios"]),
        ("soma dos graus = 2|E| (lema do aperto de maos)", sum(graus) == 2 * m),
        ("grafo bipartido: toda aresta liga usuario a cerveja",
         all((u < U) != (v < U) for u in range(n) for v in adj[u])),
        ("soma dos graus dos usuarios = soma dos graus das cervejas = |E|",
         sum(graus[:U]) == sum(graus[U:]) == m),
        ("grau medio = 2|E|/|V|", abs(p1["graus_todos"]["medio"] - 2 * m / n) < 1e-9),
        ("densidade = 2|E|/(|V|(|V|-1))", abs(p1["densidade"] - 2 * m / (n * (n - 1))) < 1e-15),
        ("componentes: soma dos tamanhos = |V|",
         sum(int(k) * v for k, v in p1["tamanhos_componentes_freq"].items()) == n),
        ("MCC + pares isolados = arestas totais", p1["mcc_arestas"] + (p1["num_componentes"] - 1) == m),
        ("DFS: arvores = componentes = CFC (Tarjan)",
         p2["dfs_arvores_no_grafo_completo"] == p1["num_componentes"] == p2["tarjan_cfc_grafo_completo"]),
        ("vertices de grau impar: grafo = MCC + 2 por par isolado",
         p2["euler_grafo_completo"]["vertices_grau_impar"]
         == p2["euler_mcc"]["vertices_grau_impar"] + 2 * (p1["num_componentes"] - 1)),
        ("numero de vertices de grau impar e par (lema do aperto de maos)",
         p2["euler_grafo_completo"]["vertices_grau_impar"] % 2 == 0),
        ("AGM: |V_mcc| - 1 arestas e Prim = Kruskal",
         p2["agm_arestas"] == [p1["mcc_vertices"] - 1] * 2 and abs(p2["agm_peso_prim"] - p2["agm_peso_kruskal"]) < 1e-6),
        ("histograma de distancias soma n(n-1)",
         sum(dist["histograma_distancias_pares_ordenados"].values()) == dist["n_mcc"] * (dist["n_mcc"] - 1)),
        ("pares a distancia 1 = 2|E_mcc|", dist["histograma_distancias_pares_ordenados"]["1"] == 2 * p1["mcc_arestas"]),
        ("L exato = media do histograma",
         abs(sum(int(k) * v for k, v in dist["histograma_distancias_pares_ordenados"].items())
             / (dist["n_mcc"] * (dist["n_mcc"] - 1)) - dist["comprimento_medio_exato"]) < 1e-12),
        ("raio <= diametro <= 2 raio (vale em todo grafo conexo)",
         dist["raio"] <= dist["diametro"] <= 2 * dist["raio"]),
        ("diametro: limitantes (Parte I) = todas as BFS", p1["mcc_diametro"] == dist["diametro"]
         and p1["mcc_raio"] == dist["raio"]),
        ("robustez: r = ceil(0,05 n)", p3["robustez"]["r"] == -(-5 * p3["robustez"]["n"] // 100)),
        ("robustez: composicao do ataque soma r",
         p3["robustez"]["direcionado_composicao"]["removidos_usuarios"]
         + p3["robustez"]["direcionado_composicao"]["removidos_cervejas"] == p3["robustez"]["r"]),
        ("trocas: |E| tentativas * Q", all(x["trocas_tentadas"] == p3["small_world"]["nulo_trocas"]["Q"] * m
                                          for x in p3["small_world"]["nulo_trocas"]["instancias"])),
    ]
    falhas = 0
    for nome, ok in checagens:
        print(("ok    " if ok else "FALHA ") + nome)
        falhas += not ok
    print(f"{len(checagens) - falhas}/{len(checagens)} conferencias ok")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
