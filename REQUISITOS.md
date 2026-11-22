# Conferência: requisitos do enunciado × arquivos

Legenda: ✅ atendido · ⚠️ atendido com ressalva · ❌ pendente.
Detalhes e histórico das correções: [`AUDITORIA_FINAL.md`](AUDITORIA_FINAL.md).

| Requisito | Situação | Onde |
|---|---|---|
| Cálculo de determinação do grafo (G115) | ✅ | artigo §1, README |
| Tratamentos informados no relatório | ✅ | artigo §2.2, Tab. 1; `data/processed/tratamento.json` |
| **Parte I:** nº de vértices e de arestas, graus mín./máx./médio | ✅ | Tab. 3; `results/parte1.json` |
| Distribuição de graus | ✅ | Fig. 1 |
| Densidade | ✅ | Tab. 3 |
| Nº de componentes e tamanho de cada uma | ✅ | Tab. 3 (1 × 99.356 + 41 × 2) |
| Diâmetro, raio, comprimento médio | ✅ exatos (MCC) | Tab. 3, Fig. 2; `results/distancias_mcc.json` |
| Clusterização média, triângulos | ✅ (0, por ser bipartido) | Tab. 3 |
| Visualização (versão reduzida) | ✅ | Fig. 3 |
| Tabela do que foi ou não computado | ✅ | Tab. 3 |
| **Parte II:** BFS, DFS, Euler, Dijkstra, Bellman-Ford, Floyd-Warshall, Tarjan (CFC e articulações/pontes), Prim/Kruskal | ✅ | `src/algoritmos.py`; Tab. 4 |
| Complexidade teórica e observada | ✅ | Tab. 2, 5, 6, 7; Fig. 4 |
| Média, desvio padrão e IC (Z se n ≥ 30; t se n < 30) | ✅ | Tab. 5 (MCC), Tab. 7 (subgrafos); `results/tables/desempenho_resumo.csv` |
| Floyd-Warshall e Bellman-Ford na MCC | ⚠️ só em subgrafos; Bellman-Ford na MCC com parada antecipada | §4.2 (estimativas medidas) |
| **Parte III:** 1) small-world, com código próprio | ✅ | §4.3, Tab. 8 (nulo por trocas de arestas) |
| 2) lei de potência | ✅ | Fig. 5, Tab. 9 (MLE exato + bootstrap + razão de verossimilhança) |
| 3) robustez: aleatória (T = 30, boxplot, média ± DP) e direcionada (grau) | ✅ | Fig. 6, Tab. 10 |
| 4) descoberta mais interessante | ✅ (recomendação, não exigência: o autor revisar o texto) | §4.3 item 4 |
| 5) modelos clássicos (extra) | ✅ | Fig. 7, Tab. 8 |
| Seções: descrição, metodologia, resultados, discussão crítica, conclusão | ✅ | artigo |
| Comentário para cada tabela e figura | ✅ | artigo |
| Template WebMedia | ✅ `webmedia.cls` oficial (zip do Overleaf) | `artigo/` |
| PDF nomeado com a matrícula | ✅ | `artigo/223115843.pdf` |
| Link do GitHub no relatório | ✅ https://github.com/ViniciusSchedler/tp-grafos-g115 | artigo, "Disponibilidade" |
| Repositório com códigos, dados tratados e README | ✅ publicado no GitHub (~10 MB, maior arquivo 6,2 MB) | `tp-grafos/` |
| Declaração de uso de IA | não exigida pelo enunciado; mantida por transparência, sem marcadores | artigo, seção final |
