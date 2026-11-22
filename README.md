# TP de Teoria dos Grafos (MATA53/UFBA): grafo G115, web-BeerAdvocate

Trabalho prático "Analisando Grafos do SNAP" (prof. Bruno Pereira dos Santos).
Aluno: Vinicius Schedler, matrícula 223115843.

**Determinação do grafo:** f(M) = (soma dos dígitos de M) × (últimos 2 dígitos + 1) mod 129
= 29 × 44 mod 129 = 1276 mod 129 = **115**. G115 é o *web-BeerAdvocate*
(<https://snap.stanford.edu/data/web-BeerAdvocate.html>).

## Modelagem

O conjunto de dados traz avaliações, não uma lista de arestas. Por isso, o grafo é
**bipartido e não direcionado**: um vértice para cada usuário (`review/profileName`), um
para cada cerveja (`beer/beerId`) e uma aresta {usuário, cerveja} para cada par que tem
avaliação. Avaliações repetidas do mesmo par viram uma única aresta, com a nota média.
Peso da aresta (usado nos algoritmos ponderados): `w = 6 - nota_media`, que fica em [1, 6].

## Estrutura

```
data/raw/            dado bruto (NÃO versionado; ver "Dados") + SHA256 e data do download
data/processed/      arestas.csv.gz (grafo tratado), cervejas.csv.gz, tratamento.json
src/
  preparar_dados.py    tratamento: bruto -> lista de arestas
  grafo.py             leitura, listas de adjacência, componentes, subgrafos
  algoritmos.py        BFS, DFS, Euler, Dijkstra, Bellman-Ford, Floyd-Warshall,
                       Tarjan (articulações/pontes), Prim, Kruskal
  metricas.py          graus, densidade, bipartição, triângulos/clusterização,
                       diâmetro/raio exatos, caminho médio, Latapy, lei de potência
  estatistica.py       média, desvio padrão, IC 95% (Z se n>=30, t-Student se n<30)
  parte1_estrutural.py Parte I
  distancias_exatas.py BFS de todos os vértices da maior componente (L, diâmetro, raio exatos)
  parte2_desempenho.py Parte II (resultados + tempos)
  parte3_analise.py    Parte III (small-world, lei de potência, robustez, modelos)
  gerar_artigo.py      gera as tabelas/macros LaTeX do artigo a partir de results/
tests/test_algoritmos.py  validação: casos conhecidos e comparação com NetworkX
results/             JSON, CSV e figuras gerados
artigo/              artigo (template WebMedia), PDF final: 223115843.pdf
```

## Como executar

Requisitos: Python 3.12+ (testado com 3.15.2). Instale as dependências:

```
python -m pip install -r requirements.txt
```

### Dados

O SNAP informa que o conjunto não está mais disponível a pedido do BeerAdvocate. Mesmo
assim, o arquivo ainda era servido em 22/11/2026 e foi baixado nessa data:

```
curl -o data/raw/Beeradvocate.txt.gz https://snap.stanford.edu/data/Beeradvocate.txt.gz
```

O SHA-256 esperado está em `data/raw/SHA256.txt`. O arquivo bruto **não** está no
repositório. A lista de arestas tratada (`data/processed/arestas.csv.gz`) está, com
identificadores numéricos e sem os nomes de usuário. Assim, é possível executar tudo a
partir do passo 2 sem baixar o arquivo bruto.

### Ordem de execução

Execute os comandos a partir da raiz do repositório:

```
python src/preparar_dados.py          # 1. tratamento (~1 min; precisa do arquivo bruto)
python tests/test_algoritmos.py       # 2. validação dos algoritmos (~1 min)
python src/parte1_estrutural.py       # 3. Parte I (~3 min)
python src/distancias_exatas.py       # 4. distâncias exatas (~2-3 h com 8 processos)
python src/parte3_analise.py potencia # 5. lei de potência (~2 min)
python src/parte3_analise.py robustez # 6. robustez (~15 min)
python src/parte3_analise.py smallworld  # 7. small-world e modelos (requer o passo 4)
python src/parte2_desempenho.py       # 8. tempos (rodar com a máquina ociosa)
python src/gerar_artigo.py            # 9. tabelas/macros do artigo
cd artigo && pdflatex 223115843 && bibtex 223115843 && pdflatex 223115843 && pdflatex 223115843
```

Todas as etapas aleatórias usam sementes fixas (2025 e derivadas).

## Ambiente dos experimentos de tempo

Intel Core i5-12450H (8 núcleos/12 threads), 15,7 GB RAM, Windows 11 Home, Python 3.15.2,
NetworkX 3.7, SciPy 1.18.1, matplotlib 3.11.2, powerlaw 2.0.0.

## Observações

- O NetworkX é usado **apenas** para validar as implementações próprias (testes). O pacote
  `powerlaw` é usado só para conferir o expoente e fazer os testes de razão de verossimilhança.
- `artigo/webmedia.cls` é **provisório** (carrega o `acmart`). Para a versão final,
  substitua-o pelo `webmedia.cls` do template oficial no Overleaf.
