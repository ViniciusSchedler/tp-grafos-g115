# TP de Teoria dos Grafos (MATA53/UFBA): grafo G115, web-BeerAdvocate

Trabalho prático "Analisando Grafos do SNAP" (prof. Bruno Pereira dos Santos).
Aluno: Vinicius Schedler, matrícula 223115843.

**Determinação do grafo:**

f(M) = (soma dos dígitos de M) × (últimos 2 dígitos + 1) mod 129
= 29 × 44 mod 129 = 1276 mod 129 = **115**.

G115 é o *web-BeerAdvocate* (<https://snap.stanford.edu/data/web-BeerAdvocate.html>).

Documentos do repositório:

- [`artigo/223115843.pdf`](artigo/223115843.pdf): relatório.
- [`GUIA_DE_ESTUDO.md`](GUIA_DE_ESTUDO.md): explicação de todo o trabalho.
- [`AUDITORIA_FINAL.md`](AUDITORIA_FINAL.md): problemas encontrados, correções e pendências.
- [`REQUISITOS.md`](REQUISITOS.md): conferência do enunciado.

## Modelagem

O conjunto de dados traz avaliações, e não uma lista de arestas. Por isso, o grafo é
**bipartido e não direcionado**:

- um vértice para cada usuário (`review/profileName`);
- um vértice para cada cerveja (`beer/beerId`);
- uma aresta {usuário, cerveja} para cada par que tem avaliação.

Avaliações repetidas do mesmo par viram uma única aresta, com a nota média. Os algoritmos
ponderados usam o peso `w = 6 - nota_media`, que fica em [1, 6].

## Estrutura

```
data/raw/            dado bruto (NÃO versionado; ver "Dados") + SHA256 e data do download
data/processed/      arestas.csv.gz (grafo tratado), cervejas.csv.gz (id -> beerId), tratamento.json
src/
  preparar_dados.py      tratamento: bruto -> lista de arestas
  grafo.py               leitura, listas de adjacência, componentes, subgrafos
  algoritmos.py          BFS, DFS, Euler, Dijkstra, Bellman-Ford, Floyd-Warshall,
                         Tarjan (CFC e articulações/pontes), Prim, Kruskal
  metricas.py            graus, densidade, bipartição, triângulos/clusterização,
                         diâmetro/raio exatos, caminho médio, Latapy, lei de potência
                         (MLE discreto exato + bootstrap de Clauset et al.)
  estatistica.py         média, desvio padrão, IC 95% (Z se n>=30, t-Student se n<30)
  estilo.py              estilo comum das figuras (tamanho de impressão em 2 colunas)
  parte1_estrutural.py   Parte I
  distancias_exatas.py   BFS de todos os vértices da maior componente (L, diâmetro, raio exatos)
  parte2_desempenho.py   Parte II (resultados + tempos)
  parte3_analise.py      Parte III (small-world, lei de potência, robustez, modelos)
  conferir_consistencia.py  confere relações aritméticas entre os resultados
  gerar_artigo.py        gera as tabelas/macros LaTeX do artigo a partir de results/
tests/test_algoritmos.py  validação: casos conhecidos e comparação com NetworkX (13 testes)
results/             JSON, CSV e figuras gerados
results/anteriores_v1/  resultados da 1ª versão (antes da auditoria), para comparação
artigo/              artigo (template WebMedia), PDF final: 223115843.pdf
```

## Como executar

Requisitos: Python 3.12+ (testado com 3.15.2). Instale as dependências:

```
python -m pip install -r requirements.txt
```

### Dados

A página do SNAP diz: "As per request from BeerAdvocate the data is no longer available". Ela
não declara licença nem condições de redistribuição. Mesmo assim, o arquivo ainda era servido
em 22/11/2026 e foi baixado nessa data:

```
curl -o data/raw/Beeradvocate.txt.gz https://snap.stanford.edu/data/Beeradvocate.txt.gz
```

O SHA-256 esperado está em `data/raw/SHA256.txt`.

O que o repositório guarda:

- **Não estão no repositório:** o arquivo bruto, os textos das avaliações e os nomes de usuário.
- **Estão no repositório:**
  - a lista de arestas tratada (`data/processed/arestas.csv.gz`), com identificadores numéricos
    e a nota média de cada par;
  - a correspondência entre o identificador do vértice e o `beerId` (`cervejas.csv.gz`).

Assim, é possível executar tudo a partir do passo 2 sem baixar o arquivo bruto.

Os dados tratados acompanham o código, como pede o enunciado do trabalho. Eles foram derivados do
conjunto do SNAP (McAuley et al., 2012) e servem apenas para reproduzir esta análise acadêmica.

### Ordem de execução

Execute os comandos a partir da raiz do repositório:

```
python src/preparar_dados.py             # 1. tratamento (~1 min; precisa do arquivo bruto)
python tests/test_algoritmos.py          # 2. validação dos algoritmos (~5 s)
python src/parte1_estrutural.py          # 3. Parte I (~3 min)
python src/distancias_exatas.py          # 4. distâncias exatas (~1-3 h com 8 processos)
python src/parte3_analise.py potencia    # 5. lei de potência + bootstrap (~25 min)
python src/parte3_analise.py robustez    # 6. robustez (~8 min)
python src/parte3_analise.py smallworld  # 7. small-world e modelos (~15 min; requer o passo 4)
python src/parte3_analise.py diagnostico_trocas  # 8. diagnóstico do modelo nulo (~10 s)
python src/parte2_desempenho.py          # 9. tempos (~15 min; rodar com a máquina ociosa)
python src/conferir_consistencia.py      # 10. conferências aritméticas
python src/gerar_artigo.py               # 11. tabelas/macros do artigo
cd artigo && pdflatex 223115843 && bibtex 223115843 && pdflatex 223115843 && pdflatex 223115843
```

As etapas 5, 6 e 7 podem rodar em paralelo, pois gravam `results/parte3.json` com trava. As
figuras podem ser refeitas sem recalcular:

- `python src/parte1_estrutural.py figuras`
- `python src/parte2_desempenho.py figura`
- `python src/parte3_analise.py figura_robustez`
- `python src/parte3_analise.py figura_modelos`

Todas as etapas aleatórias usam sementes fixas (2025 e derivadas).

## Ambiente dos experimentos de tempo

- Intel Core i5-12450H (8 núcleos/12 threads), 15,7 GB de RAM, Windows 11 Home.
- Python 3.15.2.
- Bibliotecas: NetworkX 3.7, SciPy 1.18.1, NumPy 2.5.5, matplotlib 3.11.2, powerlaw 2.0.0 (versões
  conferidas com `pip list`).

## Observações

- O NetworkX é usado **apenas** para validar as implementações próprias (testes) e para desenhar
  a visualização reduzida.
- O pacote `powerlaw` é usado só para conferir o expoente e fazer os testes de razão de
  verossimilhança.
- `artigo/webmedia.cls` é o arquivo do template oficial WebMedia (Overleaf), sem alterações. O
  preâmbulo do artigo segue o `Paper.tex` do template; as únicas linhas acrescentadas corrigem
  símbolos matemáticos que sumiam com `lmodern` (comentadas no `.tex`).
- Para compilar: `cd artigo`, depois `pdflatex 223115843`, `bibtex 223115843` e `pdflatex` mais duas vezes.
  A classe usa o estilo `ACM-Reference-Format.bst`, que vem com o pacote `acmart` da distribuição TeX.
