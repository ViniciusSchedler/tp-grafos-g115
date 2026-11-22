# Auditoria final do TP (G115, web-BeerAdvocate)

Data: 22/11/2026. Revisão crítica do trabalho já desenvolvido: código, resultados e artigo.

**Situação: o trabalho NÃO está concluído.** Faltam as etapas de publicação e entrega que só o
autor pode fazer (Seção 6).

Os resultados da primeira versão foram preservados para comparação:

- em `results/anteriores_v1/` (JSON, CSV, macros e o PDF antigo);
- na tag git `v1-pre-auditoria` (commit `b536687`).

---

## 1. Como a auditoria foi feita

- **Fontes relidas:**
  - o enunciado (`Documento sem título.pdf`);
  - os slides `bps-MATA53-g01` a `g15` e `paa.2010.2.*`, convertidos para texto.
  - Os PDFs `g15-NOTES`, `g16-notes` e `g17-notes` são só imagem e **não** foram lidos.
- **Código:**
  - revisado por mim;
  - revisado também por um revisor independente (agente de revisão de código), que recebeu o
    código, e não as minhas conclusões.
- **Testes:**
  - `python tests/test_algoritmos.py`: 13 testes, todos passam. Eram 8; foram acrescentados 5.
  - O `pytest` não está instalado no Python 3.15. Os testes rodam como script, conforme o README.
- **Consistência:** `python src/conferir_consistencia.py` confere 23 relações aritméticas entre
  avaliações, vértices, arestas, graus, componentes, distâncias e robustez. Resultado: **23/23 ok**.
- **Versões efetivamente instaladas** (`pip list`): Python 3.15.2, networkx 3.7, scipy 1.18.1,
  numpy 2.5.5, matplotlib 3.11.2, powerlaw 2.0.0. Coincidem com `requirements.txt` e com o
  artigo. Hardware: i5-12450H, 15,7 GB.
- **Números do artigo × arquivos:**
  - Todo número do texto e das tabelas vem de macros geradas por `src/gerar_artigo.py` a partir
    de `results/`, e nenhum é digitado à mão.
  - Os poucos números fixos no `.tex` foram conferidos: 1.586.259 e 355 (SNAP), 9,8 × 10¹⁴ = |V|³,
    15,7 GB, ~15 anos (22/08/1996 a 2012) e "13 testes".
  - O gerador agora tem `assert`s para as afirmações qualitativas que dependem dos dados, como
    "p = 0 nos três grupos" e "a amostra tem exatamente k vértices".
- **Experimentos refeitos** (sementes fixas):
  - Parte III inteira: lei de potência com bootstrap; robustez; small-world com o novo modelo nulo.
  - Medições novas da Parte II: Tarjan-CFC e Bellman-Ford com contagem de passadas.
  - **Não** foram refeitos, pois validações mais simples bastavam: as distâncias exatas (1,1 h),
    a Parte I e as demais medições de tempo.
- **Termos de uso dos dados:** consultei as páginas do SNAP (`web-BeerAdvocate.html` e `index.html`).

---

## 2. Conformidade com o enunciado

| Exigência | Situação | Onde / observação |
|---|---|---|
| Cálculo de determinação do grafo | ✅ | artigo §1; README (29 × 44 mod 129 = 115) |
| Tratamentos informados | ✅ | §2.2, Tab. 1; `tratamento.json` |
| Parte I: vértices, arestas, graus mín./máx./médio, distribuição, densidade | ✅ | Tab. 3, Fig. 1 |
| Parte I: nº de componentes e tamanho de cada uma | ✅ | Tab. 3 (1 × 99.356 + 41 × 2) |
| Parte I: diâmetro, raio, comprimento médio | ✅ exatos, na MCC | Tab. 3, Fig. 2; justificada a restrição à MCC |
| Parte I: clusterização, triângulos | ✅ (0, por ser bipartido) | Tab. 3 |
| Parte I: visualização reduzida | ✅ | Fig. 3 |
| Parte I: tabela do que foi ou não computado | ✅ | Tab. 3 |
| Parte II: BFS, DFS, Euler, Dijkstra, Bellman-Ford, Floyd-Warshall, Prim/Kruskal | ✅ | `algoritmos.py`; Tab. 4 |
| Parte II: Tarjan | ✅ agora as duas versões: CFC e articulações/pontes | §3.1 |
| Complexidade teórica e observada | ✅ | Tab. 2, 5, 6 e 7; Fig. 4 |
| Média, DP e IC (Z se n ≥ 30; t se n < 30) | ✅ | Tab. 5 (MCC) e **Tab. 7 (subgrafos, nova)** |
| Floyd-Warshall e Bellman-Ford no grafo | ⚠️ só em subgrafos e, no caso de Bellman-Ford, com parada antecipada | justificado com estimativa medida (§4.2) |
| III.1 small-world, com código próprio | ✅ | §4.3, Tab. 8 |
| III.2 lei de potência | ✅ agora com teste absoluto e relativo | Fig. 5, Tab. 9 |
| III.3 robustez: aleatória (T = 30, boxplot, média ± DP) e por centralidade | ✅ | Fig. 6, Tab. 10 |
| III.4 descoberta mais interessante | ✅ respondida (recomendação: o autor revisar o texto) | §4.3 item 4 |
| III.5 modelos clássicos (extra) | ✅ | Fig. 7, Tab. 8 |
| Seções: descrição, metodologia, resultados, discussão, conclusão | ✅ | artigo |
| Comentário para cada tabela e figura | ✅ | artigo |
| Template WebMedia (Overleaf) | ✅ `webmedia.cls` oficial aplicado | §4 |
| PDF nomeado com a matrícula | ✅ | `artigo/223115843.pdf` |
| Link do GitHub no relatório | ❌ placeholder `USUARIO` | ver §6 |
| Repositório com código, dados tratados e README | ⚠️ pronto e commitado localmente; falta hospedar | ver §6 |
| Declaração de uso de IA | não exigida pelo enunciado; mantida no artigo por transparência, sem marcadores | artigo, seção final |

---

## 3. Problemas encontrados

Gravidade:

- **Alta**: altera uma conclusão ou impede a entrega.
- **Média**: altera um número reportado ou a validade de um método.
- **Baixa**: redação, apresentação ou bug latente sem efeito nos resultados.

| # | Gravidade | Problema | Correção | Efeito |
|---|---|---|---|---|
| 1 | Alta (metodológica) | O modelo nulo "bipartido com os mesmos graus" (modelo de configuração) **descartava 139.336 arestas repetidas (8,9%)**. Como os *hubs* perdem mais arestas, a sequência de graus deixava de ser preservada. | Substituído por **trocas de arestas bipartidas** (Maslov e Sneppen, 2002; Gionis et al., 2007): 10 instâncias, 10·\|E\| tentativas cada. O código confere que todo vértice mantém o grau. Diagnóstico de mistura: restam 15,4% das arestas originais, contra 15,6% esperados por acaso. | cc• do nulo 0,0288 → **0,0306**; L do nulo 3,747 → **3,672**; σ_bip 2,10 → **1,93**; razão de cc• 2,08 → **1,96**. Conclusão mantida (σ > 1, ICs disjuntos). |
| 2 | Alta (entrega) | Declaração de uso de IA era um placeholder ("PENDENTE") visível no PDF. A declaração não é exigida pelo enunciado. | Reescrita, descrevendo só o que de fato ocorreu, sem marcadores. | – |
| 3 | Alta (entrega) | Link do repositório é placeholder. | Nenhuma: depende do autor criar o repositório. | Ver §6. |
| 4 | Média | A lei de potência usava a **fórmula aproximada** do MLE discreto (Clauset et al., eq. 3.7) e uma CCDF aproximada na distância KS. Com k_min = 2, a própria referência diz que a aproximação é ruim (boa só para k_min ≳ 6). O texto dizia "conferido com o `powerlaw` (1,57)", mas o valor próprio era 1,55. | **MLE discreto exato** com a zeta de Hurwitz e KS com a CCDF exata. Coincide com o pacote `powerlaw` até a 4ª casa. Teste em `tests/`. | γ (todos) 1,554 → **1,565**. Usuários: k_min 2 → 1, γ 1,474 → **1,448**. Cervejas: k_min 3 → 2, γ 1,638 → **1,625**. |
| 5 | Média | Faltava a **qualidade absoluta** do ajuste. Só havia comparação relativa (razão de verossimilhança), que não diz se a lei de potência é plausível. | **Teste de bondade de ajuste por bootstrap** (Clauset et al., §4.1), B = 500, refazendo a escolha de k_min em cada conjunto sintético. Absoluto e relativo agora são distinguidos no texto. | p = 0 nos três grupos (D dos dados 0,020–0,045; maior D sintético 0,006): lei de potência pura **rejeitada**. A conclusão não muda, mas agora tem teste formal. |
| 6 | Média | "Algoritmo de Tarjan" implementado só na versão de articulações e pontes. | Acrescentado **Tarjan para CFC** (`tarjan_cfc`), com testes (exemplo do CLRS e 20 dígrafos contra o NetworkX), tempos na MCC e nos subgrafos e explicação da aplicação ao grafo não direcionado (dirigido simétrico ⇒ CFC = componentes). | 42 CFC = 42 componentes (conferência); tempo na MCC 0,912 s. |
| 7 | Média | Robustez, métrica C: o valor "sem remoção" era uma **estimativa** com 100 origens (3,807), embora o valor exato (3,7245) fosse conhecido; o estimador estava ~2,5 erros-padrão acima. O ataque por grau também usava só 100 origens. | Sem remoção: valor exato. Ataque: 2.000 origens, com IC. | C (ataque) 5,935 → **6,011** [5,98; 6,04]. A antiga comparação "3,807 → 3,730" sugeria uma queda que não existe; agora é 3,7245 → 3,724. |
| 8 | Baixa | Robustez: a mesma semente sorteava os vértices removidos **e** as origens das BFS (sorteios correlacionados). | Sementes independentes para as origens. | C (aleatória) 3,7296 → 3,7235. As demais métricas não mudam (mesmos vértices removidos). |
| 9 | Média | Extrapolação de Bellman-Ford na MCC (~5,1 h) feita pela razão tempo/custo da amostra de 1.000 vértices, em que dados e arcos cabem no *cache*. | Medido o **tempo de uma passada na própria MCC** (0,281 s) e multiplicado por \|V\|. | Estimativa 5,1 h → **7,8 h** por execução. |
| 10 | Baixa | Memória de Floyd-Warshall apresentada como "~79 GB". Esse é só o limite inferior (8 bytes por entrada); listas Python de floats ocupam mais. | Texto diz "pelo menos 79 GB". | – |
| 11 | Média | Explicação **especulativa** para a inclinação baixa de Kruskal (0,76): "ordenação executada em C". Não foi medida. | Calculada a **inclinação por repetição** (usa \|V\| e \|E\| reais de cada amostra): 1,00 para Kruskal. O custo por unidade de E log V cai de 54 para 29 ns; o texto diz isso e que a causa não foi investigada. | Afirmação sem evidência removida. |
| 12 | Média | Faltava tabela numérica (média, DP, IC) das medições em **subgrafos**, em especial Floyd-Warshall e Bellman-Ford. | Tab. 7 (nova, largura total) com todas as 40 combinações algoritmo × tamanho, incluindo o intervalo de \|E\| nos algoritmos caros. | – |
| 13 | Baixa | IC de Bellman-Ford com limite inferior negativo, sem explicação adequada. | O texto explica: tempo ∝ VE, \|E\| varia muito entre amostras, distribuição assimétrica, hipótese de normalidade da t violada. A conclusão usa a inclinação por repetição (1,02). | – |
| 14 | Média | **Afirmações abrangentes que ignoravam as componentes desconexas**: "O grafo tem distâncias curtas"; "qualquer cerveja está a poucos passos de qualquer usuário". | Restritas à MCC (99,92% dos vértices) no resumo, nos resultados e na conclusão; legenda da Tab. 3 explicita o escopo. | – |
| 15 | Baixa | Bellman-Ford: "estabiliza após 5 passadas". O contador inclui a última passada, que não muda nada. | "d[] muda em 4 passadas; a seguinte confirma". Medido em 10 origens: sempre 4. | – |
| 16 | Baixa | Gerador **Watts–Strogatz** podia perder ou duplicar arestas: a checagem só via as arestas já religadas. Gerou 1.590.994 arestas, e não as n·k/2 = 1.591.008. | Religação checa o conjunto atual de arestas; teste garante n·k/2 arestas sem repetição. | L 4,6459 → 4,6433; C 0,53052 → 0,53058 (desprezível). |
| 17 | Baixa | Figuras geradas com 9–10 polegadas e reduzidas para a coluna: fonte efetiva de ~3 pt. Legendas sobre as curvas (desempenho, lei de potência, modelos). Rótulo "0,0%" para distâncias que existem. | Módulo `estilo.py`: figuras no tamanho de impressão (3,33 in ou 7 in), fonte de 7–8 pt, paleta Okabe-Ito (legível para daltônicos), legendas fora das curvas, "<0,1%". | – |
| 18 | Baixa | "Descoberta" e composição do ataque calculadas por um trecho de código fora dos scripts; placeholder `"ver contagem"` gravado no JSON. | Cálculo integrado a `robustez()`; placeholder removido. Também se registram os empates no grau de corte: 33 vértices de grau 136, dos quais 20 removidos. | – |
| 19 | Baixa | Interpretação não verificada no texto ("usuários avaliam cervejas do mesmo estilo ou região"). | Marcada explicitamente como hipótese não testada. | – |
| 20 | Baixa | Cobertura de testes: geradores, ajuste de lei de potência, IC, Takes–Kosters em árvores e Tarjan-CFC não eram testados. | 5 testes novos (13 no total). | – |
| 21 | Baixa (latente) | `tarjan_articulacoes_pontes` ignora toda aresta paralela ao pai; estaria errado em multigrafo. | Comentário no código. O grafo é simples por construção. | Nenhum. |
| 22 | Baixa (latente) | Casos extremos sem proteção: `verificar_euleriano` sem arestas diz "circuito"; `resumo` com n = 1 dá valor crítico NaN; `densidade` com n ≤ 1 divide por zero. | Registrados aqui. Não ocorrem nos dados; não alterados, para manter o código simples. | Nenhum. |
| 23 | Info | Suspeita de erro no método de Takes–Kosters (remover vértice com excentricidade já determinada sem atualizar os limites). | Verificado: após a 1ª BFS, todo limitante inferior ≤ diâmetro atual e todo superior ≥ raio atual; não há erro. Testado em 30 árvores e num caminho. | Nenhum. |
| 24 | Info | Tempo de Bellman-Ford com parada antecipada medido de novo: 1,506 s → 1,686 s (+12%) entre sessões, com o mesmo código e as mesmas origens. | Registrado na limitação (§5): tempos absolutos variam entre sessões; só as comparações dentro da mesma sessão são confiáveis. | – |

### Comparação dos principais números (antes → depois)

| Medida | v1 | Atual |
|---|---|---|
| γ̂ (todos; k_min) | 1,554 (2), aproximado | **1,565 (2)**, exato |
| γ̂ usuários / cervejas | 1,474 / 1,638 | **1,448 / 1,625** |
| p do teste de bondade de ajuste | não calculado | **0 (B = 500)** |
| cc• do nulo bipartido | 0,0288 (configuração, −8,9% arestas) | **0,0306** (trocas, graus exatos) |
| L do nulo bipartido | 3,747 | **3,672** |
| σ_bip | 2,10 | **1,93** |
| Robustez C sem remoção | 3,807 (estimado) | **3,7245 (exato)** |
| Robustez C aleatória | 3,730 | **3,724** |
| Robustez C ataque | 5,935 (100 origens) | **6,011** [5,98; 6,04] (2.000 origens) |
| Bellman-Ford completo na MCC (estimativa) | ~5,1 h | **~7,8 h** (medido por passada) |
| Inclinação de Kruskal | 0,76 (médias) | 0,76 (médias) / **1,00** (repetições) |
| Watts–Strogatz: arestas | 1.590.994 | **1.591.008** = n·k/2 |

Não mudaram: tudo da Parte I, distâncias exatas, resultados dos algoritmos da Parte II e métricas
A, B e D da robustez.

---

## 4. Revisões de texto e apresentação

- **Texto reescrito para ficar mais direto:**
  - resumo, metodologia (Tarjan, small-world, lei de potência, robustez) e resultados da Parte III;
  - removidas repetições e afirmações sem evidência;
  - as técnicas complementares (zeta de Hurwitz, *bootstrap*, trocas de arestas, Latapy,
    Takes–Kosters) são explicadas em linguagem de graduação.
- **Tabelas:** colunas alinhadas com `@{}` e sem casas decimais em contagens; a Tab. 7 tem
  largura total.
- **Template oficial:** o `webmedia.cls` provisório foi substituído pelo do zip oficial do Overleaf,
  e o preâmbulo passou a seguir o `Paper.tex` do template (`lmodern`, `printfolios=false`, rodapé
  SBC/ISSN). Com `lmodern`, a classe fazia sumir ( ) [ ] + = / < > Σ em modo matemático; o
  preâmbulo devolve esses símbolos às definições padrão do LaTeX. O PDF final não tem caracteres
  faltando nem linhas além da margem.
- **Referências:** 2 novas, ambas reais e conferidas: Maslov e Sneppen (Science, 2002) e Gionis
  et al. (ACM TKDD, 2007).
- **`GUIA_DE_ESTUDO.md`:**
  - conceitos, algoritmos linha por linha, fórmulas, decisões, leitura de tabelas e figuras;
  - 35 perguntas com resposta e exemplos para fazer à mão;
  - os resultados dos exemplos foram conferidos com o código do projeto.

---

## 5. Limitações remanescentes

1. **Dados e redistribuição.**
   - O SNAP diz "As per request from BeerAdvocate the data is no longer available" e não declara
     licença nem permissão de redistribuição.
   - O repositório não inclui o arquivo bruto, os textos nem os nomes de usuário. Inclui a lista de
     arestas tratada (ids numéricos + nota média) e o mapeamento id → beerId.
   - O enunciado exige os dados tratados no repositório ("Conjunto de dados usados (tratados)").
     Eles estão incluídos, na forma mínima necessária para executar o código.
   - O enunciado não exige repositório público; basta que o avaliador tenha acesso.
2. **Tempos absolutos** dependem da sessão: até 12% de diferença observada entre execuções.
   Outros processos do sistema estavam ativos, e a Parte III rodou em paralelo com outras etapas
   (não com as medições de tempo novas, que rodaram sozinhas).
3. **Estimativas de Floyd-Warshall e Bellman-Ford na MCC** supõem custo constante por operação.
   Efeitos de *cache* tendem a torná-las otimistas.
4. **Amostras por BFS** são mais densas que a MCC, o que mistura os efeitos de V e de E.
5. **Valores estimados**, todos com IC:
   - L dos modelos;
   - C da robustez depois da remoção;
   - cc• (amostra de 2.000 vértices).
6. **IC pela t-Student** em Bellman-Ford (subgrafos) é pouco informativo (assimetria).
7. **Ataque por grau** com ranking fixo, como no enunciado. Não foram feitos ataque adaptativo nem
   por intermediação (O(VE)).
8. **Casos extremos** listados no item 22 não são tratados no código.
9. **Teste de bondade de ajuste** com B = 500: resolução de p é 0,002, suficiente para decidir com
   o limiar 0,1.

---

## 6. O que falta para a entrega (exigências do enunciado)

| Pendência | Classificação | Como |
|---|---|---|
| Hospedar o repositório (GitHub ou similar) com código, dados tratados e README | obrigatória | criar o repositório vazio e enviar o conteúdo já commitado (`git remote add origin <url>`; `git push -u origin main`) |
| Pôr o link real no artigo | obrigatória | trocar `LINK_REPOSITORIO` em `src/gerar_artigo.py`; `python src/gerar_artigo.py`; recompilar |
| Entregar `artigo/223115843.pdf` no Moodle | obrigatória | – |

Recomendações, sem exigência do professor: revisar o texto da "descoberta mais interessante" e as
interpretações da Parte III antes de entregar. Nenhum trecho do artigo ou desta auditoria afirma
que o autor revisou ou validou algo.
