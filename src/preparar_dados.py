"""
Tratamento do dataset web-BeerAdvocate (SNAP) -> grafo bipartido usuario-cerveja.

Entrada : data/raw/Beeradvocate.txt.gz (formato "chave: valor", uma avaliacao por bloco)
Saida   : data/processed/arestas.csv.gz   (usuario, cerveja, nota_media, n_avaliacoes)
          data/processed/tratamento.json  (contagens de cada etapa do tratamento)

Decisoes (justificadas no relatorio):
  * vertice-usuario = review/profileName ; vertice-cerveja = beer/beerId
  * avaliacoes sem profileName sao descartadas (nao ha como identificar o usuario)
  * pares (usuario, cerveja) repetidos viram UMA aresta (multigrafo -> grafo simples);
    guardamos a media de review/overall e o numero de avaliacoes do par
  * todas as datas sao usadas (uniao temporal -> grafo estatico)
  * nomes de usuario NAO sao publicados: usuarios recebem ids 0..U-1 (ordem alfabetica)
    e cervejas ids U..U+B-1 (ordem crescente de beerId)
"""
import gzip
import json
import os
from collections import defaultdict

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQ_BRUTO = os.path.join(RAIZ, "data", "raw", "Beeradvocate.txt.gz")
DIR_SAIDA = os.path.join(RAIZ, "data", "processed")


def ler_avaliacoes(caminho):
    """Gera um dicionario por avaliacao (apenas os campos usados)."""
    campos = ("beer/beerId", "review/profileName", "review/overall", "review/time")
    atual = {}
    # latin-1 nunca falha na decodificacao; os campos usados sao ASCII na pratica
    with gzip.open(caminho, "rt", encoding="latin-1") as f:
        for linha in f:
            linha = linha.rstrip("\n")
            if linha == "":
                if atual:
                    yield atual
                    atual = {}
                continue
            chave, _, valor = linha.partition(": ")
            if chave in campos:
                atual[chave] = valor.strip()
    if atual:
        yield atual


def main():
    os.makedirs(DIR_SAIDA, exist_ok=True)
    total = 0
    sem_usuario = 0
    sem_nota = 0
    soma_nota = defaultdict(float)   # (usuario, beerId) -> soma das notas overall
    qtd = defaultdict(int)           # (usuario, beerId) -> numero de avaliacoes
    hist_overall = defaultdict(int)
    t_min, t_max = None, None

    for av in ler_avaliacoes(ARQ_BRUTO):
        total += 1
        usuario = av.get("review/profileName", "")
        if usuario == "":
            sem_usuario += 1
            continue
        try:
            nota = float(av["review/overall"])
        except (KeyError, ValueError):
            sem_nota += 1
            continue
        hist_overall[nota] += 1
        t = int(av.get("review/time", "0") or 0)
        t_min = t if t_min is None else min(t_min, t)
        t_max = t if t_max is None else max(t_max, t)
        par = (usuario, int(av["beer/beerId"]))
        soma_nota[par] += nota
        qtd[par] += 1

    usuarios = sorted({u for u, _ in qtd})
    cervejas = sorted({b for _, b in qtd})
    id_usuario = {u: i for i, u in enumerate(usuarios)}
    id_cerveja = {b: len(usuarios) + i for i, b in enumerate(cervejas)}

    pares_repetidos = sum(1 for c in qtd.values() if c > 1)
    arq_arestas = os.path.join(DIR_SAIDA, "arestas.csv.gz")
    with gzip.open(arq_arestas, "wt", encoding="utf-8", newline="") as f:
        f.write("usuario,cerveja,nota_media,n_avaliacoes\n")
        for (u, b) in sorted(qtd, key=lambda p: (id_usuario[p[0]], id_cerveja[p[1]])):
            c = qtd[(u, b)]
            f.write(f"{id_usuario[u]},{id_cerveja[b]},{soma_nota[(u, b)] / c:.4f},{c}\n")

    # mapa beerId original -> id do vertice (beerId e publico; nomes de usuario nao)
    with gzip.open(os.path.join(DIR_SAIDA, "cervejas.csv.gz"), "wt", encoding="utf-8") as f:
        f.write("vertice,beerId\n")
        for b in cervejas:
            f.write(f"{id_cerveja[b]},{b}\n")

    resumo = {
        "avaliacoes_lidas": total,
        "avaliacoes_sem_profileName_descartadas": sem_usuario,
        "avaliacoes_sem_nota_descartadas": sem_nota,
        "avaliacoes_usadas": total - sem_usuario - sem_nota,
        "usuarios": len(usuarios),
        "cervejas": len(cervejas),
        "arestas_grafo_simples": len(qtd),
        "pares_usuario_cerveja_repetidos": pares_repetidos,
        "avaliacoes_removidas_na_fusao_de_paralelas": (total - sem_usuario - sem_nota) - len(qtd),
        "review_time_min_unix": t_min,
        "review_time_max_unix": t_max,
        "histograma_review_overall": {str(k): v for k, v in sorted(hist_overall.items())},
    }
    with open(os.path.join(DIR_SAIDA, "tratamento.json"), "w", encoding="utf-8") as f:
        json.dump(resumo, f, indent=2, ensure_ascii=False)
    print(json.dumps(resumo, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
