# Guia de estudo do TP: grafo G115 (web-BeerAdvocate)

Este guia explica o trabalho do zero, para quem acompanhou MATA53. Ele segue a ordem do
artigo (`artigo/223115843.pdf`). Os números citados vêm dos arquivos de `results/`. Se você
rodar tudo de novo, as tabelas do artigo são regeneradas automaticamente por
`src/gerar_artigo.py`.

Como estudar:

1. Leia a Seção 1 (conceitos) com os slides ao lado.
2. Faça à mão os exemplos da Seção 7 e confira com o código: `python tests/test_algoritmos.py`.
3. Leia a explicação dos algoritmos (Seção 3) abrindo `src/algoritmos.py`.
4. Treine com as 35 perguntas da Seção 8 **sem olhar a resposta**.

---

## Sumário

1. [Conceitos usados no artigo](#1-conceitos-usados-no-artigo)
2. [Os dados e a modelagem](#2-os-dados-e-a-modelagem)
3. [Algoritmos linha por linha](#3-algoritmos-linha-por-linha)
4. [Técnicas complementares (Parte I e Parte III)](#4-técnicas-complementares-parte-i-e-parte-iii)
5. [Fórmulas explicadas](#5-fórmulas-explicadas)
6. [Decisões metodológicas e justificativas](#6-decisões-metodológicas-e-justificativas)
7. [Exemplos pequenos para executar à mão](#7-exemplos-pequenos-para-executar-à-mão)
8. [Como ler cada tabela e figura](#8-como-ler-cada-tabela-e-figura)
9. [35 perguntas que o professor pode fazer (com respostas)](#9-35-perguntas-que-o-professor-pode-fazer-com-respostas)
10. [Glossário](#10-glossário)

---

## 1. Conceitos usados no artigo

### 1.1 Grafo, vértice, aresta, grau

- **Grafo** G = (V, E): um conjunto de vértices V e um conjunto de arestas E. Cada aresta liga
  dois vértices.
- **Não direcionado**: a aresta {u, v} vale nos dois sentidos.
- **Simples**: sem laços (aresta de um vértice para ele mesmo) e sem arestas repetidas
  (multiarestas).
- **Grau** k_v: número de arestas que tocam v.
- **Lema do aperto de mãos**: Σ k_v = 2|E|, porque cada aresta é contada uma vez em cada ponta.
  - Consequência 1: o grau médio é ⟨k⟩ = 2|E|/|V|. No nosso grafo, 2 · 1.571.480 / 99.438 = 31,61.
  - Consequência 2: o número de vértices de grau ímpar é sempre par (62.054 no grafo).

### 1.2 Grafo bipartido

- O conjunto de vértices é dividido em duas partes, U (usuários) e B (cervejas). Toda aresta
  liga uma parte à outra.
- **Teorema**: um grafo é bipartido se e somente se não tem ciclo de comprimento ímpar.
- Logo, um grafo bipartido não tem triângulo (ciclo de comprimento 3). É por isso que o número de
  triângulos e o coeficiente de clusterização C são exatamente 0 no nosso grafo.
- **Como testar** (função `eh_bipartido`): BFS colorindo os níveis alternadamente (2-coloração).
  - Se uma aresta ligar dois vértices de mesma cor, existe um ciclo ímpar e o grafo não é bipartido.
  - Num grafo bipartido conexo, d(u, v) é par quando u e v estão do mesmo lado e ímpar quando
    estão em lados opostos. Usuário–cerveja: distâncias 1, 3, 5…; usuário–usuário: 2, 4, 6…

### 1.3 Densidade

- ρ = 2|E| / (|V|(|V|−1)): a fração das arestas possíveis que existem.
- Num grafo bipartido, nenhuma aresta usuário–usuário é possível. Por isso o artigo também dá a
  densidade bipartida |E|/(|U||B|).
- Valores: ρ = 3,18 × 10⁻⁴ e densidade bipartida 7,13 × 10⁻⁴. Os dois são muito pequenos: o grafo
  é **esparso** (|E| ≪ |V|²). É esse fato que justifica listas de adjacência em vez de matriz.

### 1.4 Caminho, distância, componentes

- **Caminho**: sequência de vértices ligados por arestas. **Distância** d(u, v): número de arestas
  do caminho mais curto; é ∞ se não há caminho.
- **Componente conexa**: conjunto maximal de vértices que se alcançam entre si.
  - Nosso grafo tem 42 componentes: a maior componente conexa (MCC), com 99.356 vértices, e 41
    pares isolados de um usuário com uma cerveja.
- **Excentricidade** e(v) = max_u d(v, u). **Diâmetro** = max e(v). **Raio** = min e(v).
  - Num grafo desconexo, toda excentricidade é ∞. Por isso diâmetro, raio e distâncias foram
    calculados **na MCC**.
- **Comprimento médio dos caminhos**: L = (1/(n(n−1))) Σ_{u≠v} d(u, v), a média sobre todos os
  pares ordenados.
- Em todo grafo conexo vale raio ≤ diâmetro ≤ 2·raio. Por quê? Seja c um centro (e(c) = raio).
  Para quaisquer u e v, d(u, v) ≤ d(u, c) + d(c, v) ≤ 2·raio. No nosso grafo: 5 ≤ 9 ≤ 10.

### 1.5 Clusterização e triângulos

- **Clusterização local**: C_v = 2T_v / (k_v(k_v − 1)), em que T_v é o número de arestas entre
  vizinhos de v (equivalentemente, de triângulos que passam por v). É a fração dos pares de
  vizinhos de v que também são vizinhos entre si.
- **C médio**: a média de C_v (com C_v = 0 quando k_v < 2).
- **Transitividade**: 3 × triângulos / caminhos de comprimento 2.
- Os três valem 0 em grafo bipartido.

### 1.6 Grafos dirigidos e componentes fortemente conexas (CFC)

- Num grafo dirigido, uma **CFC** é um conjunto maximal em que todo vértice alcança todos os
  outros seguindo o sentido dos arcos (slides g04).
- Um grafo não direcionado pode ser visto como dirigido **simétrico**: cada aresta {u, v} vira
  os arcos (u, v) e (v, u). Nesse caso u alcança v se e somente se v alcança u, logo **CFC =
  componentes conexas**.
- Foi por isso que Tarjan (CFC) deu 42 CFC no nosso grafo, o mesmo número da DFS.

### 1.7 Pontos de articulação e pontes

- **Ponto de articulação**: vértice cuja remoção aumenta o número de componentes.
- **Ponte**: aresta cuja remoção aumenta o número de componentes.
- Toda aresta que liga um vértice de grau 1 ao resto é uma ponte. Na MCC, 34.185 das 34.340
  pontes são desse tipo.

### 1.8 Eulerianidade (slides g05)

- **Circuito euleriano**: passa por todas as arestas exatamente uma vez e volta ao início.
  Existe se e somente se o grafo é conexo (ignorando vértices isolados) e **todos** os graus são
  pares.
- **Caminho euleriano** (não fechado): existe se e somente se o grafo é conexo e tem
  **exatamente dois** vértices de grau ímpar. Esses dois são as pontas do caminho.
- Nosso grafo tem 62.054 vértices de grau ímpar, logo não tem nenhum dos dois.

### 1.9 Árvore geradora mínima (AGM)

- **Árvore geradora**: subgrafo que é uma árvore e contém todos os vértices. Tem |V|−1 arestas.
- **AGM**: árvore geradora de menor soma de pesos. Prim e Kruskal sempre dão o **mesmo peso
  total**, mas podem escolher árvores diferentes quando há empates de peso.
- **Propriedade do corte** (que justifica os dois algoritmos): a aresta mais leve que cruza um
  corte (S, V∖S) pertence a alguma AGM.

### 1.10 Caminhos mínimos com pesos

- **Relaxa(u, v, w)**: se d[v] > d[u] + w(u, v), atualiza d[v] = d[u] + w(u, v) e π[v] = u.
- **Dijkstra** exige pesos ≥ 0. **Bellman-Ford** aceita pesos negativos e detecta ciclo negativo.
  **Floyd-Warshall** calcula todos os pares.

### 1.11 Complexidade assintótica

- O(f) é um limite superior do crescimento do custo, a menos de constante, para entradas grandes.
- Para comparar teoria e prática, usamos a ideia: se tempo ≈ c·f(V, E), então
  log(tempo) = log c + 1·log f. A **inclinação** da reta de log(tempo) contra log f deve ser ≈ 1.

### 1.12 Estatística das medições

- **Média** x̄. **Desvio padrão amostral**: s = √(Σ(x − x̄)² / (n − 1)). Divide por n−1 porque a
  média foi estimada dos próprios dados.
- **Intervalo de confiança (IC) de 95%** para a média, regra do enunciado:
  - n ≥ 30: x̄ ± z_{α/2} · s/√n, com z_{0,025} = 1,96 (distribuição Normal).
  - n < 30 e σ desconhecido: x̄ ± t_{α/2, n−1} · s/√n (t-Student com n−1 graus de liberdade).
    Por exemplo, t_{0,025; 9} = 2,262 para n = 10.
- **Interpretação**: se repetíssemos o experimento muitas vezes, cerca de 95% dos intervalos
  construídos assim conteriam a média verdadeira.
- O IC **não** diz que 95% das medições individuais caem dentro dele. Isso seria um intervalo de
  predição.

### 1.13 Small-world (Apêndice A)

- Uma rede é *small-world* se L é pequeno, da ordem do L de um grafo aleatório equivalente, e se
  C é muito maior que o de um grafo aleatório (Watts e Strogatz, 1998).
- O **grafo aleatório** de referência mais simples é o de Erdős–Rényi:
  - L_ER ≈ ln n / ln⟨k⟩;
  - C_ER ≈ ⟨k⟩/n, a probabilidade de existir cada aresta.

### 1.14 Lei de potência (Apêndice B)

- P(k) ∝ k^(−γ): poucos vértices com grau enorme (*hubs*) e muitos com grau pequeno.
- Em escala log-log, log P(k) = −γ log k + const é uma reta.
- Também a CCDF P(K ≥ k) é uma reta, com inclinação 1 − γ.

### 1.15 Robustez (Apêndice C)

- Remover vértices ao acaso ("falhas") ou os mais centrais ("ataque") e medir quatro métricas:
  - A: tamanho da maior componente;
  - B: número de componentes;
  - C: distâncias;
  - D: fração de vértices isolados.
- Redes com *hubs* resistem a falhas e são frágeis a ataques (Albert, Jeong e Barabási, 2000).

---

## 2. Os dados e a modelagem

### 2.1 O que é o dataset

- O web-BeerAdvocate (SNAP) traz **avaliações**, não uma lista de arestas. Cada registro tem:
  - cerveja (`beer/beerId`), cervejaria, estilo e teor alcoólico;
  - cinco notas, entre elas `review/overall`;
  - instante (`review/time`), usuário (`review/profileName`) e texto.
- A página do SNAP diz: "As per request from BeerAdvocate the data is no longer available".
  - Não há licença declarada.
  - O arquivo ainda era servido e foi baixado em 22/11/2026; o SHA-256 está em `data/raw/SHA256.txt`.

### 2.2 Por que um grafo bipartido

- A relação presente nos dados é "usuário u avaliou cerveja b". O modelo mais fiel é o bipartido
  G = (U ∪ B, E).
- Alternativa: a **projeção** usuário–usuário, ligando dois usuários que avaliaram a mesma cerveja.
  Ela exigiria um limiar arbitrário e criaria um grafo enorme. Um *hub* com 3.206 avaliadores
  sozinho gera C(3206, 2) ≈ 5,1 milhões de arestas.

### 2.3 Tratamento (`src/preparar_dados.py`)

| Etapa | Quantidade | Por quê |
|---|---|---|
| Avaliações lidas | 1.586.614 | (o SNAP informa 1.586.259; diferença de 355 registrada) |
| Sem `profileName` (descartadas) | 348 | sem nome não há vértice-usuário |
| Pares (usuário, cerveja) repetidos | 14.274 | o mesmo usuário avaliou a mesma cerveja mais de uma vez |
| Avaliações fundidas | 14.786 | multigrafo → grafo simples (uma aresta por par, nota média) |
| Arestas finais | 1.571.480 | = 1.586.614 − 348 − 14.786 |

Conta para conferir: 1.586.614 − 348 = 1.586.266 avaliações usadas, e 1.586.266 − 14.786 =
1.571.480 arestas. O script `src/conferir_consistencia.py` confere essa e outras 20 relações.

**Peso das arestas**: w = 6 − nota_média, que fica em [1, 6].

- O peso é positivo, como Dijkstra exige.
- Uma cerveja bem avaliada fica "mais perto".
- É uma convenção: os dados não têm distância natural. Só os algoritmos ponderados (Dijkstra,
  Bellman-Ford, Floyd-Warshall, Prim, Kruskal) usam o peso.

**Identificadores**:

- usuários recebem 0..33.386, em ordem alfabética do nome;
- cervejas recebem 33.387..99.437, em ordem de `beerId`;
- os nomes não são publicados.

---

## 3. Algoritmos linha por linha

Todos estão em `src/algoritmos.py` e recebem `adj` (lista de vizinhos de cada vértice) e `peso`
(lista paralela com os pesos). As cores BRANCO/CINZA/PRETO e os nomes d, f, π, key, Relaxa são os
dos slides.

### 3.1 BFS: `bfs(adj, s)`, O(V+E)

```python
cor = [BRANCO]*n; d = [INF]*n; pi = [None]*n   # inicialização: ninguém descoberto
cor[s] = CINZA; d[s] = 0; Q = deque([s])        # s descoberto, distância 0, entra na fila
while Q:                                        # enquanto houver vértice descoberto não processado
    u = Q.popleft()                             # FIFO: processa em ordem de distância
    for v in adj[u]:                            # examina cada aresta (u, v)
        if cor[v] == BRANCO:                    # v nunca visto
            d[v] = d[u] + 1; pi[v] = u          # v está um nível abaixo de u; pai = u
            cor[v] = CINZA; Q.append(v)         # descoberto, vai para a fila
    cor[u] = PRETO                              # todas as arestas de u examinadas
```

- **Por que d[v] é a distância mínima**: a fila processa os vértices em ordem não decrescente
  de d. Um vértice é descoberto pela primeira vez a partir de um vértice do nível anterior.
- **Custo**: cada vértice entra uma vez na fila, O(V). Cada lista de adjacência é percorrida uma
  vez, e Σ|adj[u]| = 2|E|, logo O(E).
- **Onde é usada**: componentes conexas, 2-coloração, distâncias exatas (uma BFS por vértice da
  MCC), diâmetro e raio, robustez.

### 3.2 DFS: `dfs(adj)`, O(V+E), versão iterativa

A versão do slide é recursiva (`VisitaDFS`). Com ~10⁵ vértices, a recursão estouraria o limite
do Python, então usamos uma pilha de pares (vértice, próximo índice da lista de adjacência).

```python
for s in range(n):                      # DFS(G): tenta iniciar uma árvore em cada vértice
    if cor[s] != BRANCO: continue
    arvores += 1                        # nova árvore da floresta DFS
    cor[s] = CINZA; tempo += 1; d[s] = tempo     # início de VisitaDFS(s)
    pilha = [(s, 0)]
    while pilha:
        v, i = pilha[-1]                # topo = chamada recursiva "ativa"
        if i < len(adj[v]):             # ainda há arestas de v a examinar
            pilha[-1] = (v, i + 1)      # avança o "laço for" de VisitaDFS(v)
            u = adj[v][i]
            if cor[u] == BRANCO:        # equivale a chamar VisitaDFS(u)
                pi[u] = v; cor[u] = CINZA; tempo += 1; d[u] = tempo
                pilha.append((u, 0))
        else:                           # laço de v terminou: fim de VisitaDFS(v)
            pilha.pop(); cor[v] = PRETO; tempo += 1; f[v] = tempo
```

- **Por que a ordem é a mesma da recursiva**: o par (v, i) guarda exatamente onde a chamada
  recursiva de v parou. Empilhar (u, 0) é "chamar" u; desempilhar é "retornar".
- **Teorema dos parênteses**: os intervalos [d[v], f[v]] são aninhados ou disjuntos. Se u é
  descendente de v, então d[v] < d[u] < f[u] < f[v]. Isso é testado em `test_dfs_tempos`.
- **Número de árvores** = número de componentes conexas, num grafo não direcionado (42 aqui).

### 3.3 Eulerianidade: `verificar_euleriano(adj)`, O(V+E)

1. Conta os vértices de grau ímpar: O(V), pois `len(adj[v])` é O(1).
2. Testa a conexidade dos vértices com arestas: uma BFS a partir de um deles, O(V+E).
3. Aplica os teoremas da Seção 1.8.

### 3.4 Dijkstra: `dijkstra(adj, peso, s)`, O((V+E) log V)

```python
d, pi = inicia_origem_unica(n, s)       # d[s]=0, demais ∞
S = [False]*n; Q = [(0, s)]             # S = conjunto de vértices finalizados; Q = heap mínimo
while Q:
    du, u = heapq.heappop(Q)            # ExtrairMinimo(Q)
    if S[u]: continue                   # entrada obsoleta (u já foi finalizado com d menor)
    S[u] = True
    for v, w in zip(adj[u], peso[u]):
        if d[v] > du + w:               # Relaxa(u, v, w)
            d[v] = du + w; pi[v] = u
            heapq.heappush(Q, (d[v], v))  # em vez de DiminuirChave: insere de novo
```

- **Por que "inserir de novo"**: o `heapq` do Python não tem DiminuirChave. Inserimos (d[v], v)
  outra vez; a entrada antiga, com d maior, sai depois e é ignorada pelo teste `if S[u]`.
- **Custo**: há no máximo uma inserção por relaxamento bem-sucedido, logo ≤ |E| + 1 entradas.
  Cada operação custa O(log E) = O(log V), pois E < V², log E < 2 log V. Total: O((V+E) log V).
- **Por que exige peso ≥ 0**: o argumento guloso diz que, quando u sai do heap, d[u] é final.
  Isso depende de nenhum caminho por vértices ainda não finalizados poder ficar mais curto, o que
  falha com arestas negativas.

### 3.5 Bellman-Ford: `bellman_ford(n, arcos, s, parar_cedo)`, O(VE)

```python
d, pi = inicia_origem_unica(n, s)
for _ in range(n - 1):                  # |V|-1 passadas
    mudou = False
    for u, v, w in arcos:               # relaxa TODOS os arcos
        if d[v] > d[u] + w:
            d[v] = d[u] + w; pi[v] = u; mudou = True
    if parar_cedo and not mudou: break  # nada mudou: as próximas passadas também não mudariam
for u, v, w in arcos:                   # verificação de ciclo negativo
    if d[v] > d[u] + w: return False, ...
return True, ...
```

- **Por que |V|−1 passadas bastam**: um caminho mínimo simples tem no máximo |V|−1 arestas. Após
  a passada i, todo vértice cujo caminho mínimo tem ≤ i arestas já tem d correto.
- **Parada antecipada**: se uma passada inteira não muda d[], as seguintes também não mudarão,
  pois relaxam os mesmos arcos com os mesmos valores. O resultado é idêntico ao do slide.
  - Na MCC, d[] mudou em 4 passadas e a 5ª confirmou. Só 4 passadas mudam algo porque os caminhos
    mínimos ponderados têm poucas arestas, e a ordem dos arcos ajuda a propagar várias arestas
    por passada.
- **Grafo não direcionado**: `arcos_de` transforma {u, v} em (u, v) e (v, u). São 2|E| arcos.
  - Atenção: com uma aresta negativa, isso criaria o ciclo u→v→u de peso negativo. No nosso caso
    os pesos estão em [1, 6].
- **Estimativa na MCC sem parada antecipada**: medimos o tempo de uma passada na própria MCC
  (tempo da execução com parada antecipada ÷ (passadas + 1)) e multiplicamos por |V|. O
  resultado está no artigo (7,8 h).

### 3.6 Floyd-Warshall: `floyd_warshall(adj, peso)`, O(V³) tempo, O(V²) memória

```python
D = matriz n×n com ∞; D[i][i] = 0; D[i][j] = w(i,j) para cada aresta
for k in range(n):                      # D^(k): caminhos que usam só os vértices 0..k como intermediários
    for i in range(n):
        if D[i][k] == INF: continue     # se i não alcança k, k não melhora nada para i
        for j in range(n):
            if D[i][k] + D[k][j] < D[i][j]:
                D[i][j] = D[i][k] + D[k][j]
```

- **Recorrência** (slides g14): D^(k)[i][j] = min(D^(k−1)[i][j], D^(k−1)[i][k] + D^(k−1)[k][j]).
  O laço de k precisa ser o **mais externo**.
- **Por que não rodou na MCC**:
  - 99.356³ ≈ 9,8 × 10¹⁴ iterações a ~33 ns cada dariam ≈ 1,0 ano(s).
  - A matriz teria 99.356² ≈ 9,9 × 10⁹ entradas, no mínimo 79 GB com 8 bytes por entrada. Há
    15,7 GB de RAM.

### 3.7 Tarjan para articulações e pontes: `tarjan_articulacoes_pontes(adj)`, O(V+E)

Ideia: na DFS de um grafo não direcionado só há arestas de árvore e arestas de retorno (para um
ancestral). Define-se:

> low[v] = menor d[] alcançável a partir da subárvore de v usando no máximo uma aresta de retorno.

```python
if d[u] == 0:              # aresta de árvore (v -> u)
    pi[u] = v; tempo += 1; d[u] = low[u] = tempo; ...
elif u != pi[v]:           # aresta de retorno (não é a própria aresta para o pai)
    low[v] = min(low[v], d[u])
...
# ao terminar u (filho de p = pi[u]):
low[p] = min(low[p], low[u])
if low[u] > d[p]:  ponte (p, u)       # a subárvore de u não volta a p nem acima
if p != raiz and low[u] >= d[p]: articulação p   # a subárvore de u não passa acima de p
# raiz: articulação se tem 2 ou mais filhos na árvore DFS
```

- **Por que a raiz é especial**: ela não tem ancestral. É articulação somente se a DFS precisou
  começar dois ou mais ramos a partir dela, pois não há aresta entre subárvores diferentes de uma
  DFS em grafo não direcionado.
- **Detalhe**: `u != pi[v]` ignora a aresta para o pai. Isso só é correto em grafo **simples**.
  Num multigrafo, uma aresta paralela ao pai é um retorno legítimo. Por isso tornamos o grafo
  simples no tratamento.

### 3.8 Tarjan para CFC: `tarjan_cfc(adj)`, O(V+E)

Mantém uma pilha P de vértices "abertos" (que ainda não têm CFC definida).

```python
descobre u:  d[u] = low[u] = tempo; P.append(u); na_pilha[u] = True
arco v -> u já descoberto e na_pilha[u]:  low[v] = min(low[v], d[u])
fim de v:
    if low[v] == d[v]:                 # v é a "raiz" (primeiro vértice descoberto) da sua CFC
        desempilha P até v; todos recebem a mesma CFC
    low[pai] = min(low[pai], low[v])
```

- **Por que funciona**: se low[v] == d[v], nenhum vértice da subárvore de v alcança um vértice
  descoberto antes de v que ainda esteja aberto. Então v e o que está acima dele em P formam uma
  CFC completa.
- **Diferença para o método dos slides (CLRS)**: o CLRS faz duas DFS, uma em G e outra no
  transposto Gᵀ em ordem decrescente de f[]. Tarjan usa uma DFS só. Ambos são O(V+E).
- **Aplicação ao nosso grafo**: dirigido simétrico, CFC = componentes conexas = 42.
  - Isso confere a implementação, mas não traz informação nova sobre o grafo, e o artigo diz isso.

### 3.9 Prim: `prim(adj, peso)`, O(E log V)

```python
for r in range(n):                      # reinicia em cada componente -> floresta geradora mínima
    if not naQ[r]: continue
    key[r] = 0; Q = [(0, r)]
    while Q:
        k, u = heapq.heappop(Q)         # vértice mais barato para entrar na árvore
        if not naQ[u]: continue         # entrada obsoleta
        naQ[u] = False
        if pi[u] is not None: arestas.append((pi[u], u, k)); total += k
        for v, w in zip(adj[u], peso[u]):
            if naQ[v] and w < key[v]:   # aresta (u,v) é a melhor ligação de v à árvore até agora
                pi[v] = u; key[v] = w; heapq.heappush(Q, (w, v))
```

- **key[v]**: peso da aresta mais leve que liga v à árvore atual.
- A diferença para Dijkstra é só o critério: key[v] = w (peso da aresta), e não d[u] + w (custo do
  caminho).

### 3.10 Kruskal: `kruskal(n, arestas)`, O(E log V)

```python
for u, v, w in sorted(arestas, key=peso):   # ordem crescente de peso: O(E log E) = O(E log V)
    ru, rv = encontrar(u), encontrar(v)       # raízes das árvores de u e v (union-find)
    if ru != rv:                              # não forma ciclo
        une as árvores (união por posto); aceita (u, v, w)
```

- `encontrar` usa **compressão de caminho**: depois de achar a raiz, aponta todos os vértices do
  caminho diretamente para ela.
- Com **união por posto**, cada operação custa O(α(n)) amortizado, em que α é a inversa de
  Ackermann (≤ 4 na prática). O custo dominante é a ordenação.

---

## 4. Técnicas complementares (Parte I e Parte III)

### 4.1 Diâmetro e raio exatos sem n BFS (Takes e Kosters, 2011): `diametro_raio_exatos`

Uma BFS a partir de v dá e(v) e todas as distâncias d(v, w). Pela desigualdade triangular, para
todo w:

- **limitante inferior**: e(w) ≥ max(d(v,w), e(v) − d(v,w));
- **limitante superior**: e(w) ≤ e(v) + d(v,w).

O algoritmo:

1. Alterna BFS a partir do candidato de maior limitante superior (bom para o diâmetro) e do de
   menor limitante inferior (bom para o raio).
2. Descarta os vértices cuja excentricidade já não pode mudar o diâmetro nem o raio.

Na MCC bastaram **38 BFS**, em vez de 99.356. O resultado (9 e 5) coincide com a BFS de todos os
vértices (`distancias_exatas.py`). É exato, não aproximado.

### 4.2 Comprimento médio exato

- Uma BFS por vértice da MCC dá o histograma exato das distâncias e L = 3,7245.
- Custo O(V(V+E)) ≈ 99.356 × 1,67 × 10⁶ operações: 1,1 h com 8 processos.

### 4.3 Estimador de L por amostragem (modelos e robustez)

- Sorteamos k origens sem reposição. Para cada origem s, calculamos a média de d(s, v) sobre os
  n−1 destinos. A média dessas médias é um **estimador sem viés** de L, porque cada origem tem
  exatamente n−1 destinos.
- O IC vem da variação entre origens.

### 4.4 Agrupamento bipartido de Latapy: `clusterizacao_bipartida_latapy`

- cc•(u) = média, sobre os vértices v a distância 2 de u, de |N(u) ∩ N(v)| / |N(u) ∪ N(v)|.
- É a **sobreposição de Jaccard** entre as vizinhanças: quanto dois usuários avaliaram as mesmas
  cervejas, ou quanto duas cervejas têm os mesmos avaliadores.
- Usa a identidade |N(u) ∪ N(v)| = k_u + k_v − |N(u) ∩ N(v)|.
- A contagem de |N(u) ∩ N(v)| para todos os v a distância 2 sai de um `Counter`: percorre os
  vizinhos w de u e soma 1 para cada vizinho de w.

### 4.5 Modelo nulo bipartido por trocas de arestas (Maslov e Sneppen, 2002; Gionis et al., 2007)

- **Objetivo**: um grafo aleatório bipartido em que **cada** usuário e **cada** cerveja tem
  exatamente o mesmo grau do grafo real. Comparar com ele mostra o que é "estrutura" e o que é
  só "efeito da sequência de graus".
- **Algoritmo** (`bipartido_trocas`), repetido Q·|E| vezes:
  1. Sorteia duas arestas {u₁, b₁} e {u₂, b₂}.
  2. Se u₁ ≠ u₂, b₁ ≠ b₂ e {u₁, b₂} e {u₂, b₁} ainda não existem, troca para {u₁, b₂}, {u₂, b₁}.
- Cada troca preserva o grau dos 4 vértices e a bipartição. Nunca cria aresta repetida.
- **Diagnóstico de mistura**:
  - após as trocas, restam 15,4% das arestas originais;
  - um grafo aleatório com os mesmos graus teria por acaso ≈ (1/m) Σ min(1, k_u k_b/m) =
    15,6%;
  - como os valores são próximos, as trocas foram suficientes.
- **Por que não o modelo de configuração simples**:
  - a primeira versão pareava "pontas" ao acaso e descartava os pares repetidos;
  - com *hubs*, isso descartou 139.336 arestas (8,9%) e reduziu os graus altos, de modo que o modelo
    não tinha mais os mesmos graus;
  - as trocas corrigem isso.

### 4.6 Lei de potência com o método de Clauset, Shalizi e Newman (2009)

1. **Modelo discreto**: P(k) = k^(−γ) / ζ(γ, k_min) para k ≥ k_min, com
   ζ(γ, k_min) = Σ_{j ≥ k_min} j^(−γ) (zeta de Hurwitz, `scipy.special.zeta`).
2. **MLE exato**: maximiza ln L(γ) = −n ln ζ(γ, k_min) − γ Σ ln k_i (otimização numérica em uma
   variável).
   - A primeira versão usava a fórmula aproximada γ̂ = 1 + n[Σ ln(k_i/(k_min − ½))]⁻¹, que só é
     boa para k_min ≳ 6. Com k_min = 2 ela dava 1,554; o MLE exato dá 1,565, igual ao
     pacote `powerlaw`.
3. **Escolha de k_min**: o que minimiza a distância KS
   D = max_k |CCDF_empírica(k) − CCDF_modelo(k)|.
4. **Bondade de ajuste (absoluta)**:
   - gera B = 500 conjuntos sintéticos; abaixo de k_min, sorteia dos dados; acima, sorteia do
     modelo ajustado;
   - refaz o passo 3 (inclusive a escolha de k_min) em cada um;
   - p = fração dos conjuntos com D ≥ D_dados. Se p ≤ 0,1, rejeita a lei de potência.
   - Resultado: p = 0 (nenhum dos 500 sintéticos teve D tão grande; p < 0,002) nos três grupos. **Rejeitada.**
5. **Comparação relativa** (razão de verossimilhança normalizada R, pacote `powerlaw`):
   - R > 0 favorece a lei de potência; R < 0 favorece a alternativa.
   - Resultado: lei de potência ≫ exponencial, mas lognormal e lei de potência truncada são melhores.
6. **Diferença entre 4 e 5**:
   - O passo 4 pergunta: "os dados poderiam ter vindo deste modelo?"
   - O passo 5 pergunta: "qual de dois modelos explica melhor os dados?"
   - Um modelo pode ganhar a comparação e ainda assim ser rejeitado no teste absoluto. É o que
     acontece aqui: a truncada ganha da lei de potência pura, mas nenhuma das duas foi testada como
     "o" modelo verdadeiro.

### 4.7 Robustez

- r = ⌈0,05 · 99.356⌉ = 4.968 vértices removidos, na MCC.
- **Aleatória**: T = 30 sorteios independentes (sementes 2025 a 2054). As origens das BFS da
  métrica C usam outras sementes (12025 a 12054).
- **Ataque por grau**:
  - ranking fixo calculado antes de remover, como o enunciado pede;
  - desempate pelo identificador;
  - no grau de corte (136) há 33 vértices, dos quais 20 entram.
- Métricas:
  - S = maior componente / vértices restantes;
  - D = isolados / vértices restantes;
  - C = distância média na maior componente: valor exato sem remoção; 100 origens por repetição
    aleatória; 2.000 origens no ataque.

---

## 5. Fórmulas explicadas

| Fórmula | O que significa | Valor no trabalho |
|---|---|---|
| f(M) = (Σ dígitos) × (últimos 2 + 1) mod 129 | regra do enunciado | 29 × 44 mod 129 = 115 |
| Σ_v k_v = 2\|E\| | cada aresta tem 2 pontas | 3.142.960 |
| ⟨k⟩ = 2\|E\|/\|V\| | grau médio | 31,61 |
| ρ = 2\|E\|/(\|V\|(\|V\|−1)) | fração de arestas possíveis | 3,18 × 10⁻⁴ |
| \|E\|/(\|U\|\|B\|) | densidade bipartida | 7,13 × 10⁻⁴ |
| C_v = 2T_v/(k_v(k_v−1)) | fração de pares de vizinhos ligados | 0 (bipartido) |
| L = Σ d(u,v)/(n(n−1)) | distância média entre pares | 3,7245 (MCC) |
| L_ER ≈ ln n/ln⟨k⟩ | L esperado num ER | ln 99.438/ln 31,61 = 3,33 |
| C_ER ≈ ⟨k⟩/n | prob. de uma aresta no ER | 3,18 × 10⁻⁴ |
| cc•(u) = média \|N(u)∩N(v)\|/\|N(u)∪N(v)\| | sobreposição de vizinhanças | 0,0599 (grafo) × 0,0306 (nulo) |
| σ_bip = (cc•/cc•_nulo)/(L/L_nulo) | índice small-world bipartido | 1,93 |
| P(k) = k^(−γ)/ζ(γ,k_min) | lei de potência discreta | γ̂ = 1,565 |
| D = max \|S(k) − P(k)\| | distância KS entre CCDFs | 0,025 |
| x̄ ± z_{α/2} s/√n | IC 95%, n ≥ 30 | z = 1,96 |
| x̄ ± t_{α/2,n−1} s/√n | IC 95%, n < 30 | t = 2,262 (n = 10) |
| r = ⌈0,05 n⌉ | vértices removidos na robustez | 4.968 |
| w = 6 − nota | peso da aresta | w ∈ [1, 6] |
| e(w) ≥ max(d, e(v) − d), e(w) ≤ e(v) + d | limitantes de Takes–Kosters | 38 BFS |
| log t = log c + b log f | inclinação b ≈ 1 se t ∝ f | Tab. 6 do artigo |

**Por que a CCDF em vez do histograma**:

- O histograma P(k) fica ruidoso na cauda: há muitos graus com 0 ou 1 vértice, o que gera as
  "linhas" horizontais na Fig. 1.
- A CCDF P(K ≥ k) acumula os vértices, é monótona e não precisa de escolher faixas.
- Se P(k) ∝ k^(−γ), então P(K ≥ k) ∝ k^(1−γ).

---

## 6. Decisões metodológicas e justificativas

1. **Grafo bipartido não direcionado**: é a estrutura dos dados. Uma projeção dependeria de
   limiar arbitrário.
2. **Multigrafo → simples**: o enunciado permite. A nota média preserva a informação do peso. Isso
   também evita o problema de Tarjan com arestas paralelas.
3. **Sem filtro temporal**: o enunciado sugere a união das arestas no tempo. Filtrar reduziria o
   grafo sem necessidade, porque os algoritmos lineares rodam no grafo inteiro.
4. **Listas de adjacência**: o grafo é esparso. Uma matriz teria ~10¹⁰ posições.
5. **DFS e Tarjan iterativos**: a recursão do Python (limite ~1.000, e a pilha do C) não suporta
   uma DFS de profundidade ~10⁵. A versão iterativa visita na mesma ordem.
6. **Heap com reinserção**: o `heapq` não tem DiminuirChave. A reinserção mantém a complexidade.
7. **Distâncias na MCC**: no grafo desconexo, e(v) = ∞. A MCC tem 99,92% dos vértices. As
   componentes pequenas são 41 pares, com distância 1 entre os dois vértices.
8. **L exato em vez de estimado**: com 8 processos levou 1,1 h. O estimador por amostragem só foi
   usado onde o exato seria caro demais (modelos, robustez), sempre com IC.
9. **Diâmetro e raio por dois métodos**: Takes–Kosters (38 BFS) e todas as BFS. A concordância é
   uma validação.
10. **Floyd-Warshall e Bellman-Ford só em subgrafos**:
    - Floyd-Warshall precisaria de ≥ 79 GB e ~1 ano.
    - Bellman-Ford sem parada antecipada, ~7,8 h por execução, vezes R repetições.
    - Na MCC, Bellman-Ford rodou com parada antecipada, que dá o mesmo resultado.
11. **Subgrafos por BFS**: garantem subgrafos conexos. Viés conhecido: ficam mais densos que a MCC,
    por isso comparamos com f(V, E), e não só com V.
12. **R = 30 e R = 10**: com R = 30 o IC usa a Normal; nos algoritmos caros, R = 10 com t-Student,
    como manda o enunciado para n < 30.
13. **Inclinação por repetição**: complementa a inclinação sobre as médias. Usa o |V| e |E| reais
    de cada amostra, importante em Bellman-Ford, cujo |E| varia muito entre amostras.
14. **Ataque por grau, não por intermediação**: o enunciado recomenda as duas. A intermediação
    exata custa O(VE) ≈ 1,6 × 10¹¹ operações em Python puro, o que é inviável. O grau é exato e
    barato.
15. **Ranking fixo**: é o que o enunciado descreve ("calcule a centralidade, ordene, remova os
    top r"). Um ataque adaptativo, que recalcula o grau a cada remoção, seria outra variante.
16. **Nulo bipartido por trocas**: preserva exatamente os graus, ao contrário do modelo de
    configuração com descarte.
17. **Clauset et al.**: a inspeção visual da reta em log-log é o que o Apêndice B pede. O teste de
    bondade de ajuste evita concluir "é lei de potência" só porque o gráfico parece reto.
18. **Sementes fixas** (2025 e derivadas): qualquer pessoa obtém os mesmos números.
19. **Números do artigo gerados por script**: evita erro de digitação. Se um resultado muda, o
    texto muda junto.

---

## 7. Exemplos pequenos para executar à mão

Todos os resultados abaixo foram conferidos com o código do projeto.

### Exemplo 1: BFS, DFS, Euler, articulações, diâmetro

Vértices A=0, B=1, C=2, D=3, E=4, F=5; arestas A–B, A–C, B–D, C–D, D–E, E–F. Listas de adjacência
(na ordem de inserção):

```
A: B, C     B: A, D     C: A, D     D: B, C, E     E: D, F     F: E
```

(Um quadrado A-B-D-C com uma "cauda" D-E-F.)

**BFS a partir de A**:

- Fila [A] → processa A, descobre B e C (d = 1).
- Processa B, descobre D (d = 2). Processa C: D já é cinza.
- Processa D, descobre E (d = 3). Processa E, descobre F (d = 4).
- Resultado: d = [0, 1, 1, 2, 3, 4]; π = [–, A, A, B, D, E].

**DFS** (começa em A, segue a ordem das listas):

| v | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| d | 1 | 2 | 4 | 3 | 6 | 7 |
| f | 12 | 11 | 5 | 10 | 9 | 8 |

Caminho da DFS: A(1) → B(2) → D(3) → C(4), e C não tem vizinho branco, logo f[C] = 5. Depois D →
E(6) → F(7); f[F] = 8, f[E] = 9, f[D] = 10, f[B] = 11, f[A] = 12. Há uma árvore. Confira os
parênteses: [3,10] contém [4,5] e [6,9].

**Euler**: graus A2, B2, C2, D3, E2, F1. Exatamente 2 ímpares (D e F), logo há **caminho
euleriano** de D a F e não há circuito. Exemplo: D-B-A-C-D-E-F.

**Tarjan (articulações e pontes)**:

- low de C: C tem aresta de retorno para A (d = 1), logo low[C] = 1. Isso propaga low[D] = low[B] = 1.
- E e F não têm retorno: low[F] = 7 > d[E] = 6, então (E, F) é ponte; low[E] = 6 > d[D] = 3, então
  (D, E) é ponte.
- Articulações: D (filho E com low[E] = 6 ≥ d[D] = 3) e E (filho F com low 7 ≥ 6).
- Resultado: **articulações {D, E}**, **pontes {D–E, E–F}**.

**Diâmetro e raio**: e(A) = 4 (até F), e(D) = 2. Diâmetro = 4 (A–F), raio = 2 (centro D).

### Exemplo 2: Dijkstra, Bellman-Ford, Floyd-Warshall, Prim, Kruskal

Vértices 0..4; arestas com peso: 0–1 (4), 0–2 (1), 2–1 (2), 1–3 (1), 2–3 (5), 3–4 (3).

**Dijkstra a partir de 0**:

| passo | extrai | relaxamentos | d = [0, 1, 2, 3, 4] |
|---|---|---|---|
| 1 | 0 (0) | d1 = 4, d2 = 1 | [0, 4, 1, ∞, ∞] |
| 2 | 2 (1) | d1 = 1+2 = 3 < 4; d3 = 1+5 = 6 | [0, 3, 1, 6, ∞] |
| 3 | 1 (3) | d3 = 3+1 = 4 < 6 | [0, 3, 1, 4, ∞] |
| – | (4, 1) | entrada obsoleta, ignorada | |
| 4 | 3 (4) | d4 = 4+3 = 7 | [0, 3, 1, 4, 7] |
| – | (6, 3) | obsoleta | |
| 5 | 4 (7) | – | [0, 3, 1, 4, 7] |

π = [–, 2, 0, 1, 3]. O caminho até 4 é 0 → 2 → 1 → 3 → 4, com custo 1 + 2 + 1 + 3 = 7.

**Bellman-Ford** (arcos na ordem (0,1,4), (0,2,1), (1,0,4), (1,2,2), (1,3,1), (2,0,1), (2,1,2),
(2,3,5), (3,1,1), (3,2,5), (3,4,3), (4,3,3)):

- Passada 1: d1 = 4, d2 = 1, d3 = 4+1 = 5, d1 = 1+2 = 3, d4 = 5+3 = 8, logo d = [0, 3, 1, 5, 8].
- Passada 2: d3 = 3+1 = 4, d4 = 4+3 = 7, logo d = [0, 3, 1, 4, 7].
- Passada 3: nada muda, para (parada antecipada; `passadas` = 3).
- Verificação: nenhum arco relaxa, então não há ciclo negativo. O resultado é igual ao de Dijkstra.

**Floyd-Warshall** (matriz final):

```
     0  1  2  3  4
0 [  0  3  1  4  7 ]
1 [  3  0  2  1  4 ]
2 [  1  2  0  3  6 ]
3 [  4  1  3  0  3 ]
4 [  7  4  6  3  0 ]
```

Exercício: faça D^(0), D^(1) e D^(2) à mão. Por exemplo, D^(2)[0][1] = min(4, D[0][2] + D[2][1])
= min(4, 1 + 2) = 3.

**Prim** (a partir de 0): aceita 0–2 (1), 2–1 (2), 1–3 (1), 3–4 (3). **Kruskal** (arestas em ordem
de peso): aceita 0–2 (1), 1–3 (1), 2–1 (2) e 3–4 (3); 0–1 (4) e 2–3 (5) formariam ciclo. Nos dois casos
o peso total é **7** e há 4 = |V| − 1 arestas.

### Exemplo 3: Tarjan (CFC) num grafo dirigido

Arcos: 0→1, 1→2, 2→0, 2→3, 3→4, 4→3, 4→5.

- CFC: {0, 1, 2} (ciclo), {3, 4} (ciclo) e {5}.
- Ordem em que as CFC são fechadas por Tarjan: {5} primeiro, depois {3, 4}, depois {0, 1, 2}. É
  uma ordem topológica reversa do grafo das componentes.
- Se você ignorar o sentido dos arcos, há **uma** componente conexa. Por isso, num grafo dirigido,
  CFC ≠ componente conexa. Já no dirigido simétrico (nosso caso), elas coincidem.

### Exemplo 4: agrupamento bipartido de Latapy

Usuários 0, 1, 2; cervejas 3, 4, 5; arestas 0–3, 0–4, 1–3, 1–4, 1–5, 2–5.

- cc•(0): o único vértice a distância 2 é 1. |N(0) ∩ N(1)| = |{3,4}| = 2 e |N(0) ∪ N(1)| =
  |{3,4,5}| = 3, logo cc•(0) = **2/3**.
- cc•(1): a distância 2 estão 0 (2/3) e 2 (|{5}|/|{3,4,5}| = 1/3). A média dá **0,5**.
- cc•(2): só 1 está a distância 2, logo cc•(2) = **1/3**.
- Triângulos: 0, e C = 0, embora haja sobreposição clara entre os usuários 0 e 1.

É exatamente isso que o artigo argumenta: C = 0 não significa "ausência de agrupamento" num grafo
bipartido.

### Exemplo 5: troca de arestas

Arestas {0–3, 1–4}. Trocar dá {0–4, 1–3}.

- Graus antes: 0:1, 1:1, 3:1, 4:1. Depois: os mesmos.
- A troca é proibida se 0–4 ou 1–3 já existirem, porque criaria aresta repetida.

### Exemplo 6: intervalo de confiança com t-Student

Tempos (s): 0,52; 0,48; 0,50; 0,55; 0,45 (n = 5 < 30, então t-Student com 4 g.l.).

1. x̄ = 0,500.
2. s = √[(0,02² + 0,02² + 0 + 0,05² + 0,05²)/4] = √(0,0058/4) = 0,0381.
3. t_{0,025; 4} = 2,776.
4. Margem = 2,776 × 0,0381/√5 = 0,0473. **IC 95% = [0,453; 0,547]**.

Com n = 30 e a Normal, o valor crítico seria 1,96, e o intervalo ficaria mais estreito.

### Exemplo 7: inclinação log-log

Se o tempo dobra quando f(V, E) dobra, então log t cresce log 2 quando log f cresce log 2, e a
inclinação é 1.

Exemplo do Floyd-Warshall:

- de k = 200 para k = 400, V³ multiplica por 8;
- o tempo foi de 0,243 s para 2,082 s, ou seja, ×8,6;
- inclinação ≈ log 8,6 / log 8 ≈ 1,03.

---

## 8. Como ler cada tabela e figura

- **Tab. 1 (tratamento)**: quantas avaliações entraram e saíram em cada etapa. Confira que as
  contas fecham (Seção 2.3).
- **Tab. 2 (algoritmos e complexidade)**: o que foi implementado, a complexidade teórica e onde
  cada algoritmo rodou (MCC ou subgrafos).
- **Tab. 3 (Parte I)**: atende ao pedido "tabela indicando as informações computadas ou não".
  - Todas foram computadas.
  - A coluna "Obtenção" diz se o valor é exato, se veio de BFS ou de amostra (só a visualização).
- **Fig. 1 (distribuição de graus)**:
  - **Esquerda**: P(k) em log-log. A nuvem cai aproximadamente como reta até k ≈ 100. As "linhas"
    horizontais à direita são graus com 1, 2, 3… vértices: P = 1/n, 2/n…
  - **Direita**: CCDF. Usuários (azul) ficam acima das cervejas (laranja), ou seja, têm cauda mais
    pesada (máx. 5.782 contra 3.206). A curvatura para baixo depois de k ≈ 100 é o "corte".
- **Fig. 2 (distâncias)**:
  - fração dos pares a cada distância;
  - a maioria está a 3 ou 4 passos (82,4%); 86,9% estão a no máximo 4 e 99,6% a no máximo 5;
  - só 22 pares ordenados estão a distância 9 (o diâmetro).
- **Fig. 3 (visualização)**:
  - 250 vértices em ordem de BFS;
  - poucos usuários (azul, 5 no subgrafo) ligados a muitas cervejas (laranja);
  - os usuários de grau alto são os "centros" das estrelas.
- **Tab. 4 (resultados da Parte II)**: o que cada algoritmo devolveu na MCC.
  - Prim = Kruskal confirma a AGM.
  - Bellman-Ford = Dijkstra confirma os caminhos mínimos.
  - 42 árvores da DFS = 42 CFC = 42 componentes.
- **Tab. 5 (tempos na MCC)**: média, DP e IC 95% de cada algoritmo na MCC (R = 30 ou 10).
  - DFS, Tarjan e Prim custam ~3,5–5,5 vezes uma BFS, apesar de terem a mesma ordem de complexidade
    (ou um fator log a mais): é a constante do Python (tuplas na pilha, heap).
- **Fig. 4 (desempenho)**:
  - log-log de tempo × |V|;
  - retas paralelas indicam a mesma taxa de crescimento;
  - no painel direito, a reta de Floyd-Warshall tem inclinação ~3 contra V, e a de Bellman-Ford
    tem barras enormes (IC), pela variação de |E|.
- **Tab. 6 (inclinações)**: valores ≈ 1 contra o custo teórico confirmam a complexidade.
  - Coluna "médias": inclui a MCC nos quase lineares.
  - Coluna "repetições": usa cada amostra do experimento B.
  - Coluna "vs. V": mostra que o tempo cresce menos que V nos quase lineares (porque |E| das
    amostras não cresce proporcionalmente) e ~3 em Bellman-Ford e Floyd-Warshall.
- **Tab. 7 (medições em subgrafos)**: média, DP e IC 95% de cada algoritmo em cada tamanho k.
  - Em Bellman-Ford, o DP às vezes é maior que a média, e o IC inferior fica negativo: o tempo
    depende de |E|, que varia de poucas centenas a dezenas de milhares entre amostras do mesmo k.
  - Um IC negativo para tempo é sinal de que a hipótese de normalidade da t-Student não vale. Por
    isso o artigo não tira conclusão do IC nesse caso e usa a inclinação por repetição.
- **Tab. 8 (small-world)**:
  - L real (3,72) ≈ L dos modelos aleatórios (3,3–3,7): primeiro critério ok.
  - C = 0 contra C_ER = 3 × 10⁻⁴: segundo critério falha (bipartido).
  - Watts–Strogatz tem C = 0,53, mas L = 4,6.
  - Linhas de cc•: o grafo tem agrupamento bipartido 1,96 vezes o do nulo com os mesmos
    graus, e σ_bip = 1,93 > 1.
- **Tab. 9 e Fig. 5 (lei de potência)**:
  - γ̂ ≈ 1,57 com k_min = 2. D = 0,025 nos dados, contra D ≤ 0,006 nos sintéticos, com
    p = 0: **rejeitada**.
  - R > 0 contra a exponencial e R < 0 contra a lognormal e a truncada: a lei de potência ganha da
    exponencial, mas perde das outras duas.
  - Na figura, a reta vermelha (lei de potência) passa acima dos pontos na cauda, e a tracejada
    (truncada) acompanha a queda.
- **Tab. 10 e Fig. 6 (robustez)**:
  - Aleatória: S = 0,983 e ~1.578 componentes (quase todas vértices isolados, 1,7% dos restantes).
  - Por grau: S = 0,434, 52.451 componentes e 54,7% isolados.
  - Na figura, os boxplots (30 repetições) são estreitos e longe da estrela (ataque). A
    variabilidade da remoção aleatória é pequena perto da diferença entre os dois tipos de remoção.
- **Fig. 7 (modelos)**:
  - CCDF dos modelos clássicos contra a real;
  - ER e WS caem abruptamente (sem *hubs*);
  - BA tem cauda, mas termina em ~2.000, contra 5.782 no real.

---

## 9. 35 perguntas que o professor pode fazer (com respostas)

**1. Como você determinou o grafo?**
Matrícula 223115843: soma dos dígitos 29; últimos dois dígitos 43, mais 1 = 44; 29 × 44 = 1276;
1276 mod 129 = 115 (129 × 9 = 1161; 1276 − 1161 = 115). O G115 é o web-BeerAdvocate.

**2. O dataset não é uma lista de arestas. Como você construiu o grafo?**
Cada avaliação liga um usuário a uma cerveja. Criei um vértice por usuário (`profileName`), um por
cerveja (`beerId`) e uma aresta por par avaliado. O resultado é bipartido e não direcionado.

**3. Por que não direcionado?**
A relação "avaliou" tem sentido natural (usuário → cerveja), mas, num grafo bipartido em que todos
os arcos vão de U para B, nenhuma cerveja alcança nada. Distâncias, componentes e diâmetro
perderiam o sentido. O enunciado permite tratar como não direcionado.

**4. O que você fez com avaliações repetidas do mesmo par?**
Fundi-as numa aresta (multigrafo → simples), com a nota média. Foram 14.274 pares e 14.786
avaliações fundidas.

**5. Por que o grafo tem 0 triângulos? Isso é erro?**
Não. O grafo é bipartido (testei por 2-coloração com BFS), e grafos bipartidos não têm ciclo
ímpar. O triângulo é um ciclo de comprimento 3. O valor 0 confirma a implementação.

**6. Então o grafo não é small-world?**
Pelo critério do Apêndice A (C ≫ C_aleatório), não, porque C = 0 por construção. Com a medida
própria para bipartidos (Latapy), o agrupamento é 1,96 vezes o de um bipartido aleatório
com os mesmos graus, e L é próximo do aleatório. Na versão bipartida, há o padrão small-world
(σ_bip = 1,93 > 1).

**7. Qual a implicação prática de ser small-world aqui?**
Dentro da MCC, qualquer cerveja está a poucos passos de qualquer usuário: 87% dos pares estão a
no máximo 4 passos e 99,6% a no máximo 5. Recomendações por vizinhança de 2–3 passos alcançam quase todo o catálogo.
Isso não vale para os 41 pares isolados.

**8. Como você garantiu que o grafo aleatório de comparação tinha os mesmos graus?**
Com trocas de arestas: troca {u₁,b₁}, {u₂,b₂} por {u₁,b₂}, {u₂,b₁} se não criar repetição. Cada
troca preserva os graus. O código confere com `assert` que todo vértice mantém o grau.

**9. Quantas trocas bastam?**
Fiz 10|E| tentativas por instância, em 10 instâncias. Conferi a mistura: sobram 15,4%
das arestas originais, praticamente o que um grafo aleatório com os mesmos graus teria por acaso
(15,6%).

**10. Por que o diâmetro foi calculado só na maior componente?**
Num grafo desconexo, a distância entre componentes é ∞, e então e(v) = ∞ para todo v. A MCC tem
99,92% dos vértices; as outras 41 componentes são pares (diâmetro 1).

**11. O comprimento médio é exato ou estimado?**
Exato: uma BFS a partir de cada um dos 99.356 vértices da MCC, em 8 processos, durante 1,1 h. O
histograma de todas as distâncias está em `results/distancias_mcc.json`.

**12. Como você calculou diâmetro e raio sem n BFS?**
Pelo método de Takes e Kosters. Cada BFS dá limitantes para a excentricidade de todos os vértices:
e(w) ≥ max(d, e(v) − d) e e(w) ≤ e(v) + d. Descarto vértices que não podem mudar o resultado.
Foram 38 BFS. Conferi com todas as BFS: diâmetro 9 e raio 5.

**13. Por que a DFS é iterativa? O slide é recursivo.**
A recursão do Python estoura com ~10⁵ níveis. Uso uma pilha de (vértice, próximo índice), que
reproduz a mesma ordem da recursão. Os tempos d[] e f[] satisfazem o teorema dos parênteses, e isso
é testado.

**14. O grafo é euleriano?**
Não. Há 62.054 vértices de grau ímpar (61.972 na MCC). Para circuito, todos os graus precisariam
ser pares; para caminho, exatamente 2 ímpares (e o grafo conexo).

**15. Qual "algoritmo de Tarjan" você implementou?**
Os dois do artigo de Tarjan (1972), ambos com uma DFS e low[v]:

- CFC (o problema dos slides, que lá é resolvido com DFS em G e Gᵀ);
- pontos de articulação e pontes, para grafos não direcionados.

**16. Faz sentido rodar Tarjan de CFC num grafo não direcionado?**
Como verificação, sim. Tratando cada aresta como dois arcos, u alcança v se e somente se v alcança
u, então CFC = componentes conexas. Deu 42, o mesmo número da DFS e da BFS. A informação nova vem
da versão de articulações e pontes: 7.260 articulações e 34.340 pontes.

**17. O que significam as 34.340 pontes?**
34.185 delas ligam um vértice de grau 1: usuários com uma única avaliação, ou cervejas avaliadas
por uma única pessoa. Remover essa aresta isola o vértice.

**18. Por que Dijkstra pode ser usado? E Bellman-Ford?**
Os pesos w = 6 − nota estão em [1, 6], todos positivos, o que Dijkstra exige. Bellman-Ford também
funciona e confirmou que não há ciclo negativo. Ele deu exatamente as mesmas distâncias de Dijkstra.

**19. Por que Floyd-Warshall não rodou no grafo todo?**

- Tempo O(V³): ≈ 9,8 × 10¹⁴ iterações; medindo ~33 ns por iteração nos subgrafos, seria ≈
  1,0 ano(s).
- Memória O(V²): matriz de 9,9 × 10⁹ entradas, no mínimo 79 GB, com 15,7 GB de RAM.

Por isso rodei em subgrafos de até 400 vértices e medi a complexidade.

**20. E Bellman-Ford na MCC?**
Com |V|−1 passadas, a estimativa é ~7,8 h por execução. Ela vem do tempo de uma
passada medido na própria MCC, multiplicado por |V|. Usei a parada antecipada: para quando uma
passada não muda d[]. O resultado é idêntico; d[] mudou em 4 passadas.

**21. Como você mediu o tempo?**
`time.perf_counter`, sem contar leitura de dados nem preparação da entrada, com o coletor de lixo
desligado durante a medição. Usei R = 30 repetições (IC pela Normal) ou R = 10 nos caros (IC pela
t-Student com 9 g.l.).

**22. Por que o IC de Bellman-Ford tem limite inferior negativo?**
O desvio padrão é grande: cada repetição usa uma amostra diferente, e o número de arestas varia
muito (o tempo é ∝ VE). A distribuição é assimétrica, e a t-Student supõe normalidade. Por isso
olhei a inclinação por repetição (≈ 1,02), que leva em conta o |E| de cada amostra.

**23. Como você comparou a complexidade teórica com a observada?**
Ajustei a inclinação da reta log(tempo) × log f(V, E), com f o custo teórico. Se t ≈ c·f, a
inclinação é 1. Deu 0,76–1,18 nos quase lineares, 1,02–1,06 em Bellman-Ford e 1,00 em
Floyd-Warshall.

**24. Por que Kruskal tinha inclinação 0,76?**
Esse valor usa as médias por tamanho (incluindo a MCC). O custo medido por unidade de E log V cai
de ~54 ns na menor amostra para ~29 ns na MCC, e a inclinação sobre as médias reflete essa queda.
Ajustando sobre cada repetição dos subgrafos, a inclinação é 1,00: dentro de cada tamanho, o tempo
acompanha E log V. A causa da queda não foi investigada; o artigo diz isso. A primeira versão do
texto atribuía a queda à ordenação feita em C, mas isso não foi medido, por isso a frase saiu.

**25. Por que Dijkstra é ~5 vezes mais lento que a BFS, se só tem um fator log a mais?**
log₂ V ≈ 17, mas a BFS também tem constante. A diferença real vem das operações do `heapq`
(inserção e remoção com comparações de tuplas) e das reinserções. Em Python, constantes pesam
muito.

**26. O que é a amostra por BFS e qual seu viés?**
Os k primeiros vértices de uma BFS a partir de um vértice sorteado, com o subgrafo induzido. Isso
garante conexidade. Viés: a BFS alcança cedo os *hubs*, então as amostras são mais densas que a MCC.
Por isso comparei contra f(V, E), e não só V.

**27. A distribuição de graus segue lei de potência?**
Tem cauda pesada e *hubs*, mas não é lei de potência pura. O teste de bondade de ajuste de Clauset
et al. dá p = 0 (D = 0,025 nos dados contra ≤ 0,006 nos sintéticos). Na comparação
relativa, a lognormal e a lei de potência truncada são melhores (R < 0).

**28. Qual a diferença entre o teste de bondade de ajuste e a razão de verossimilhança?**
O primeiro é absoluto: "os dados poderiam ter vindo desse modelo?". O segundo é relativo: "qual de
dois modelos é melhor?". A lei de potência perde nos dois; a truncada ganha no relativo, mas isso
não prova que ela seja o modelo correto.

**29. Por que γ < 2? Redes livres de escala não têm 2 < γ < 3?**
O k_min escolhido é 2, então o ajuste é dominado pelo corpo da distribuição (graus baixos, onde a
queda é mais lenta). Além disso, a cauda tem corte. γ < 2 aqui não é "rede livre de escala com γ
anômalo"; é sinal de que uma lei de potência única não descreve a distribuição.

**30. Como você escolheu k_min?**
Pelo k_min que minimiza a distância KS entre a CCDF empírica e a do modelo ajustado (Clauset et
al.), entre os graus observados ≤ 1.000 com pelo menos 50 vértices na cauda.

**31. A rede é robusta?**
A falhas aleatórias, sim: removendo 5% ao acaso, S = 0,983, a fração de isolados é 1,7% e a
distância média não muda. A ataques, não: removendo os 5% de maior grau, S = 0,434, surgem 52.451
componentes, 54,7% dos restantes ficam isolados e a distância média sobe para 6,0.

**32. Por que você escolheu o grau, e não a intermediação (betweenness)?**
As duas são recomendadas pelo enunciado. A intermediação exata (Brandes) custa O(VE) ≈ 1,6 × 10¹¹
operações em Python puro, inviável aqui. O grau é exato, barato e, numa rede com *hubs*, já remove
os vértices que concentram as conexões: 70,8% da soma dos graus.

**33. Como você tratou o grafo desconexo na robustez?**
Seguindo a recomendação do Apêndice C: trabalhei na MCC (n = 99.356, r = 4.968). Os 41 pares
isolados ficam de fora.

**34. Qual a descoberta mais interessante?**
Os 4.968 vértices de maior grau (2.546 usuários e 2.422 cervejas) concentram 70,8% da soma dos
graus. Removê-los isola 51.618 vértices, 38.721 deles cervejas: todos os avaliadores dessas
cervejas estavam entre os 2.546 usuários removidos. A maior parte do catálogo só se liga ao resto
da rede por um grupo pequeno de usuários muito ativos.

**35. O grafo se parece com algum modelo clássico?**
Não exatamente:

- ER e WS têm graus concentrados (sem *hubs*), e WS tem muitos triângulos.
- BA tem cauda pesada, mas mais leve (grau máx. ~2.000 contra 5.782; γ = 3) e não é bipartido.
- O mais próximo na distribuição de graus é o BA.
- Um modelo adequado seria bipartido com ligação preferencial nos dois lados.

**Perguntas bônus rápidas**

- *Por que listas de adjacência?* O grafo é esparso: a matriz teria 10¹⁰ posições.
- *Prim e Kruskal deram árvores iguais?* O mesmo peso (177.260,33) e o mesmo número de arestas
  (99.355). As árvores podem diferir em empates de peso, e há muitos, porque as notas variam em
  passos de 0,5.
- *O que é IC de 95%?* Um intervalo construído de forma que, em 95% das repetições do experimento,
  conteria a média verdadeira.
- *Por que n−1 no desvio padrão?* Porque a média é estimada dos próprios dados (correção de
  Bessel, estimador sem viés da variância).

---

## 10. Glossário

| Termo | Significado |
|---|---|
| AGM (MST) | árvore geradora mínima: árvore com todos os vértices e soma de pesos mínima |
| Aresta de retorno | na DFS, aresta para um ancestral já descoberto (cinza) |
| Articulação | vértice cuja remoção desconecta o grafo |
| BFS | busca em largura (fila); dá distâncias em grafos não ponderados |
| Bipartido | vértices divididos em dois lados; arestas só entre lados |
| *Bootstrap* | gerar conjuntos sintéticos a partir de um modelo ou dos dados para estimar uma distribuição |
| CCDF | distribuição acumulada complementar P(K ≥ k) |
| CFC (SCC) | componente fortemente conexa (grafo dirigido) |
| Clusterização C | fração dos pares de vizinhos que são vizinhos entre si |
| Componente conexa | conjunto maximal de vértices mutuamente alcançáveis |
| Densidade ρ | fração das arestas possíveis presentes |
| DFS | busca em profundidade (pilha/recursão); dá d[], f[], floresta DFS |
| Diâmetro | maior excentricidade (maior distância entre dois vértices) |
| Distância KS (D) | maior diferença entre duas funções de distribuição acumulada |
| Esparso | \|E\| ≪ \|V\|² |
| Excentricidade e(v) | maior distância de v a qualquer vértice |
| Grau k_v | número de arestas incidentes em v |
| *Hub* | vértice de grau muito maior que a média |
| IC | intervalo de confiança |
| Inclinação (log-log) | expoente empírico: tempo ∝ f^b |
| Latapy cc• | agrupamento bipartido: sobreposição média das vizinhanças a distância 2 |
| Lei de potência | P(k) ∝ k^(−γ) |
| Lei de potência truncada | P(k) ∝ k^(−α) e^(−λk): lei de potência com corte exponencial |
| Lognormal | log k tem distribuição normal; também gera cauda pesada |
| low[v] | menor d[] alcançável da subárvore de v com até uma aresta de retorno |
| MCC | maior componente conexa |
| MLE | estimador de máxima verossimilhança |
| Modelo nulo | grafo aleatório que preserva algumas propriedades (aqui, os graus) para comparação |
| Multigrafo | grafo com arestas repetidas entre o mesmo par |
| Ponte | aresta cuja remoção desconecta o grafo |
| Raio | menor excentricidade |
| Relaxa | teste e atualização d[v] > d[u] + w → d[v] = d[u] + w |
| Robustez | quanto a conectividade resiste à remoção de vértices |
| S | fração dos vértices restantes que está na maior componente |
| Small-world | L pequeno (≈ aleatório) e agrupamento alto (≫ aleatório) |
| Troca de arestas | {u₁,b₁},{u₂,b₂} → {u₁,b₂},{u₂,b₁}; preserva graus |
| *Union-find* | estrutura de conjuntos disjuntos (encontrar/unir) usada por Kruskal |
| Zeta de Hurwitz ζ(s, q) | Σ_{j≥0} (j+q)^(−s): normalização da lei de potência discreta |
