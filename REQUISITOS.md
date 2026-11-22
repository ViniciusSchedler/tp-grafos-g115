# Conferência: requisitos do enunciado × arquivos

Legenda: ✅ atendido · ⚠️ atendido com ressalva · ❌ pendente

| Requisito | Situação | Onde |
|---|---|---|
| Cálculo de determinação do grafo (G115) | ✅ | artigo §1, README |
| Tratamentos informados no relatório | ✅ | artigo §2.2, Tab. 1; `data/processed/tratamento.json` |
| **Parte I:** nº de vértices e de arestas, graus mín./máx./médio | ✅ | artigo Tab. 3; `results/parte1.json` |
| Distribuição de graus | ✅ | Fig. 1 |
| Densidade | ✅ | Tab. 3 |
| Nº de componentes e tamanho de cada uma | ✅ | Tab. 3 e §4.1 (1×99.356 + 41×2) |
| Diâmetro, raio, comprimento médio | ✅ exatos (MCC) | Tab. 3, Fig. 2; `results/distancias_mcc.json` |
| Clusterização média, triângulos | ✅ (0, por ser bipartido) | Tab. 3 |
| Visualização (versão reduzida) | ✅ | Fig. 3 |
| Tabela do que foi ou não computado | ✅ | Tab. 3 (coluna "Comp.?") |
| **Parte II:** BFS, DFS, Euler, Dijkstra, Bellman-Ford, Floyd-Warshall, Tarjan, Prim/Kruskal | ✅ | `src/algoritmos.py`; Tab. 4 |
| Complexidade teórica e observada | ✅ | Tab. 2, 5, 6; Fig. 4 |
| Média, desvio padrão e IC (Z se n≥30; t se n<30) | ✅ | Tab. 5; `results/tables/desempenho_resumo.csv` |
| Floyd-Warshall e Bellman-Ford na MCC | ⚠️ só em amostras / com parada antecipada (justificado com estimativa de tempo) | §4.2 |
| Tarjan | ⚠️ variante de articulações/pontes (grafo não direcionado), justificada | §3.1 |
| **Parte III:** 1) small-world, com código próprio | ✅ | §4.3, Tab. 7 |
| 2) lei de potência | ✅ | Fig. 5, Tab. 8 |
| 3) robustez: aleatória (T=30, boxplot média ± dp) e direcionada (grau) | ✅ | Fig. 6, Tab. 9 |
| 4) descoberta mais interessante | ⚠️ redigida a partir dos dados; **o aluno deve revisar e assumir** | §4.3 item 4 |
| 5) modelos clássicos (extra) | ✅ | Fig. 7, Tab. 7 |
| Seções: descrição, metodologia, resultados, discussão crítica, conclusão | ✅ | artigo |
| Comentário para cada tabela/figura | ✅ | artigo |
| Template WebMedia | ⚠️ `webmedia.cls` provisório (acmart); trocar pelo oficial do Overleaf | `artigo/` |
| PDF nomeado com a matrícula | ✅ | `artigo/223115843.pdf` |
| Link do GitHub no relatório | ❌ placeholder `USUARIO` | `src/gerar_artigo.py` (LINK_REPOSITORIO) |
| Repositório com códigos, dados tratados e README | ⚠️ pronto localmente; ainda não publicado | `tp-grafos/` |
| Regras da disciplina sobre uso de IA | ❌ declaração marcada como PENDENTE | `src/gerar_artigo.py` (DECLARACAO_IA) |
