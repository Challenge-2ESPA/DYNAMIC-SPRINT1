# Desafio Motiva — Escadas rolantes (Dynamic Programming, Sprint 1)

Este projeto resolve a parte de Dynamic Programming do Challenge Motiva. A Motiva (ViaQuatro, Linha 4-Amarela) opera escadas rolantes nas estações e quer reduzir o custo de manutenção, identificando quais escadas precisam de atenção antes de falhar e planejando o atendimento da equipe.

Tudo foi feito em **Python puro**: buscas linear e binária escritas à mão, fila e pilha feitas com listas (`append`, `pop(0)`, `pop()`). Não usamos grafos, `deque` nem bibliotecas prontas de busca.

## Integrantes

| Nome | RM |
|---|---|
| David Ernesto Mogollon Gama | 567855 |
| Felipe Menezes Santos | 566607 |
| João Antonio Sarracine Faedrich de Souza | 567407 |
| Pedro Henrique Tavares Viana | 567680 |
| Roger de Carvalho Paiva | 566949 |

## Aviso sobre os dados

Os dados são **fictícios**, gerados por `gerar_dataset.py` com semente fixa. Os minutos entre estações, o tempo de serviço e o horário do turno são **premissas do grupo**, não medições da Motiva. Os resultados mostram como os métodos funcionam e o que os números significam, não a situação real da operação.

## Como executar

Na pasta do projeto:

```bash
python gerar_dataset.py                       # gera sensores.csv e saidas/resumo_dataset.csv (semente 42)
python main.py sensores.csv linha.csv saidas  # roda as três atividades e grava os resultados em saidas/
python -m unittest discover -s tests -v       # roda os 51 testes automáticos
```

O `notebook.ipynb` roda tudo passo a passo, com explicação e interpretação em cada etapa, e já está **executado** (com as saídas salvas). Para rodar no Colab, envie para a pasta de trabalho os arquivos `.py` e o `linha.csv`.

## Onde está cada requisito do enunciado

| Requisito | Onde está |
|---|---|
| `gerar_dataset(n_escadas, n_leituras, semente)` com `random.seed(semente)` | `gerar_dataset.py` |
| 30 a 197 escadas, ≥ 200 leituras por escada, 1 por hora, escadas embaralhadas | `gerar_dataset.py` (a função recusa valores fora dos limites) |
| Colunas e faixas normais pedidas | `COLUNAS` e `FAIXAS` em `gerar_dataset.py` |
| Perfis 60% / 30% / 10% | `gerar_dataset.py` (30 / 15 / 5 escadas) |
| Entrega 1: função, `sensores.csv` e resumo | `sensores.csv`, `saidas/resumo_dataset.csv`, notebook (Etapa 0) |
| `busca_linear` e `busca_binaria` à mão, contando comparações | `busca.py` |
| 1.000 consultas por ID (linear no arquivo × binária na lista ordenada) | `main.py` → `saidas/comparacoes_consultas.csv` e `comparacoes_resumo.csv` |
| Primeira leitura com 5 alertas acumulados, com as duas buscas | `busca.py` → `saidas/comparacoes_primeira_leitura.csv` |
| `linha.csv` com ≥ 8 estações em ordem, base na primeira posição | `linha.csv` (11 estações da Linha 4-Amarela) |
| `tempo_ate` com busca linear e `rota_ida_e_volta` com pilha | `linha.py` |
| `tempos_base.csv` (estação, minutos de ida, minutos de ida e volta) | `saidas/tempos_base.csv` |
| `planejar_turno(base, horas)` com `fila_critica` e `fila_normal`, `pop(0)`, agenda e pendentes | `turno.py` |
| Perda de 1 hora desfazendo a agenda com `pop()` | `perder_hora` em `turno.py` |
| Plano de 4, 6 e 8 h (escada, estação, rota, início e fim) com pendentes | `saidas/planos_turno.csv`, `saidas/planos_turno.json`, notebook (Atividade 3) |
| Notebook executado, dados e README | `notebook.ipynb`, `sensores.csv`, `linha.csv`, `saidas/`, este arquivo |

## Estrutura do projeto

| Arquivo | O que faz |
|---|---|
| `gerar_dataset.py` | Gera o dataset sintético, grava `sensores.csv` e o resumo. |
| `dados.py` | Lê o `sensores.csv`, define a regra de alerta e monta a lista de escadas em alerta. |
| `busca.py` | Busca linear, busca binária, primeira leitura com o limite de alertas e soma acumulada. |
| `linha.py` | Lê a linha, calcula o tempo até cada estação e a rota de ida e volta com pilha. |
| `turno.py` | Monta as filas, planeja o turno e simula a perda de 1 hora. |
| `main.py` | Liga tudo: roda as análises, confere os resultados e grava os arquivos em `saidas/`. |
| `notebook.ipynb` | Notebook executado, com explicação e interpretação de cada etapa. |
| `linha.csv` | As 11 estações da Linha 4-Amarela, em ordem, com os minutos até a seguinte. |
| `sensores.csv` | Dataset gerado: 10.000 leituras de 50 escadas. |
| `saidas/` | Resultados (CSV e JSON) usados nas tabelas deste README. |
| `tests/` | 51 testes automáticos, um arquivo por módulo. |

Dividimos o código em módulos para separar cada atividade e facilitar a leitura e a correção. As funções calculam e retornam valores; só o `main.py`, o bloco principal do `gerar_dataset.py` e o notebook imprimem e gravam arquivos.

---

## Etapa 0 - Dataset sintético

### Regras da geração

- **Semente: 42.** `random.seed(semente)` é chamado no começo, então o arquivo sai igual toda vez.
- **Tamanho:** 50 escadas × 200 leituras = 10.000 leituras. A função aceita de 30 a 197 escadas e pelo menos 200 leituras (fora disso, levanta `ValueError`).
- **Tempo:** uma leitura por hora para cada escada, a partir de 01/01/2026 00:00, em ordem de horário.
- **Ordem no arquivo:** dentro de cada hora, a ordem das escadas é embaralhada, como num registro real.
- **Escadas:** IDs `ESC-001` a `ESC-050` (com 3 dígitos — ver a Atividade 1), cada uma numa das 11 estações da linha e sorteada como **crítica** ou **não crítica**.
- **Colunas:** `id_escada, estacao, grupo, data_hora, vibracao, temperatura, corrente, tensao, nivel_oleo, velocidade`.
- **Faixas normais:** vibração 1–4 mm/s · temperatura 35–65 °C · corrente 10–25 A · tensão 361–399 V · óleo 60–100 % · velocidade 0,48–0,52 m/s.
- **Perfis:**
  - **Saudável (60%, 30 escadas):** todos os sensores sorteados dentro da faixa normal.
  - **Desgaste gradual (30%, 15 escadas):** a vibração sobe até +4 mm/s, a temperatura até +20 °C e o óleo cai até −30 pontos, de forma proporcional às horas que passam.
  - **Falha pontual (10%, 5 escadas):** normal na maior parte do tempo, mas cada leitura tem 5% de chance de um pico de vibração (7–10 mm/s) e temperatura (75–90 °C).

### Resumo (Entrega 1)

| Sensor | Faixa normal | Mínimo | Média | Máximo |
|---|---|---|---|---|
| Vibração (mm/s) | 1–4 | 1,00 | 3,13 | 9,78 |
| Temperatura (°C) | 35–65 | 35,0 | 53,14 | 89,2 |
| Corrente (A) | 10–25 | 10,00 | 17,47 | 25,00 |
| Tensão (V) | 361–399 | 361,0 | 380,11 | 399,0 |
| Nível de óleo (%) | 60–100 | 30,6 | 75,73 | 100,0 |
| Velocidade (m/s) | 0,48–0,52 | 0,48 | 0,50 | 0,52 |

| Perfil | Escadas | | Grupo | Escadas |
|---|---|---|---|---|
| Saudável | 30 | | Crítica | 24 |
| Desgaste | 15 | | Não crítica | 26 |
| Falha pontual | 5 | | | |

**Interpretação.** Corrente, tensão e velocidade ficam sempre dentro da faixa, porque nenhum perfil mexe nelas. Os valores fora da faixa (vibração até 9,78, temperatura até 89,2, óleo até 30,6) vêm dos perfis de desgaste e de falha, não de erro no código. A média de vibração (3,13) fica acima do meio da faixa (2,5) por causa das escadas em desgaste.

### Regra de alerta

Uma leitura está **em alerta** quando **qualquer** sensor sai da faixa normal. O limite conta como normal (vibração de exatamente 4,0 não alerta). A função é `esta_em_alerta`, em `dados.py`. Com essa regra, as escadas que têm alerta são as 15 em desgaste e as 5 com falha; as 30 saudáveis nunca saem da faixa.

---

## Atividade 1 - Busca linear × busca binária

### Métodos

- **`busca_linear`:** percorre a lista do começo ao fim. 1 comparação por item. Não precisa de lista ordenada.
- **`busca_binaria`:** olha o meio da lista e descarta a metade que não pode ter o alvo. Precisa de lista ordenada. Contamos **2 comparações por passo** (`==` e `<`).

### Parte A - localizar escadas pelo ID (1.000 consultas)

Sorteamos 1.000 IDs com semente 42 e procuramos cada um de três formas. O `main.py` **confere** se cada busca achou a escada certa e se a binária achou a mesma posição da linear; se não, o programa para com erro.

| Método | Total de comparações | Média | Máximo |
|---|---|---|---|
| Linear na lista do arquivo (10.000 leituras) | 25.127 | 25,13 | 50 |
| Linear na lista de IDs | 25.835 | 25,84 | 50 |
| **Binária na lista de IDs ordenada** | **8.788** | **8,79** | **11** |

A tabela de cada consulta está em `saidas/comparacoes_consultas.csv`.

### Parte B - primeira leitura com 5 alertas acumulados

Para cada escada, as 200 leituras (em ordem de horário) viram 0 ou 1 (alerta ou não).

- **Linear (`primeira_leitura_linear`):** soma os alertas um a um até chegar a 5.
- **Binária (`primeira_leitura_binaria`):** a soma acumulada nunca diminui, ou seja, é uma lista ordenada. A binária acha a primeira posição em que ela vale 5 ou mais.

O código confere se as duas buscas acham a mesma posição em todas as escadas.

| | Comparações (50 escadas) |
|---|---|
| Busca linear | 6.850 |
| Busca binária | 392 |
| Passos para montar a soma acumulada (a binária precisa dela) | 10.000 |

20 escadas chegam a 5 alertas e 30 não chegam. A tabela por escada (posição, data e hora, comparações) está no notebook e em `saidas/comparacoes_primeira_leitura.csv`.

### Interpretação

- **Por ID, a binária faz ≈3× menos comparações** (8,8 contra 25,8 na mesma lista). Isso bate com a teoria: log₂(50) ≈ 5,6 passos, com 2 comparações cada → no máximo 11–12. A linear olha, em média, metade da lista. A diferença cresce com o tamanho: com 197 escadas, a linear iria a ≈99 de média e a binária só a ≈14.
- **A linear no arquivo** tem média parecida com a linear nos IDs. Isso acontece porque a primeira hora do arquivo já tem todas as 50 escadas (embaralhadas), então qualquer ID aparece nas 50 primeiras linhas. Esse número depende do arquivo, não só do algoritmo.
- **Primeira leitura com 5 alertas:** a binária faz ≈8 comparações por escada, contra até 200 da linear. Mas ela só funciona porque antes montamos a soma acumulada, que custa 1 passo por leitura. Se a pergunta for feita **uma vez só**, a linear sai mais barata, porque para assim que chega a 5. A binária compensa quando a mesma soma é consultada várias vezes (por exemplo, "quando chegou a 5? e a 10? e a 20?").
- **Erro que encontramos e corrigimos:** a binária só funciona se a lista estiver ordenada **pelo mesmo critério da comparação**. Na primeira versão, os IDs não tinham zeros (`ESC-2`, `ESC-10`). A lista estava ordenada pelo número, mas o `<` compara texto, e `"ESC-10" < "ESC-2"`. Resultado: a binária não achava 10 das 50 escadas, e a tabela de comparações estava errada. A correção foi usar IDs com 3 dígitos (`ESC-002`, `ESC-010`), que deixam a ordem do texto igual à do número, e conferir cada resultado no `main.py`. O teste `test_acha_todos_os_ids_do_dataset` garante que isso não volta.

---

## Atividade 2 - Percurso na linha com pilha

### Linha (`linha.csv`)

As 11 estações da Linha 4-Amarela, na ordem. Os minutos até a estação seguinte são **premissas do grupo**. A base é **Luz**, na primeira posição.

| Trecho | Minutos |
|---|---|
| Luz → República | 2 |
| República → Higienópolis-Mackenzie | 2 |
| Higienópolis-Mackenzie → Paulista | 2 |
| Paulista → Oscar Freire | 2 |
| Oscar Freire → Fradique Coutinho | 2 |
| Fradique Coutinho → Faria Lima | 2 |
| Faria Lima → Pinheiros | 2 |
| Pinheiros → Butantã | 3 |
| Butantã → São Paulo-Morumbi | 3 |
| São Paulo-Morumbi → Vila Sônia | 3 |

### Método

- **`tempo_ate(linha, estacao)`:** busca linear pela estação, somando os minutos de cada trecho desde a base.
- **`rota_ida_e_volta(linha, estacao)`:** usa uma pilha ("o último que entra é o primeiro que sai").
  - **Ida:** cada estação visitada é empilhada com `append`, até o destino.
  - **Volta:** as estações são desempilhadas com `pop()`, do destino até a base. Os minutos da volta são somados durante o `pop()`, trecho por trecho.

### Resultado (`saidas/tempos_base.csv`)

| Estação | Ida (min) | Ida e volta (min) |
|---|---|---|
| Luz (base) | 0 | 0 |
| República | 2 | 4 |
| Higienópolis-Mackenzie | 4 | 8 |
| Paulista | 6 | 12 |
| Oscar Freire | 8 | 16 |
| Fradique Coutinho | 10 | 20 |
| Faria Lima | 12 | 24 |
| Pinheiros | 14 | 28 |
| Butantã | 17 | 34 |
| São Paulo-Morumbi | 20 | 40 |
| Vila Sônia | 23 | 46 |

Exemplo de volta (Vila Sônia): Vila Sônia → São Paulo-Morumbi → Butantã → Pinheiros → Faria Lima → Fradique Coutinho → Oscar Freire → Paulista → Higienópolis-Mackenzie → República → Luz.

### Interpretação

A pilha devolve a volta exatamente na ordem inversa da ida, sem precisar inverter a lista: o destino, último a entrar, é o primeiro a sair. Como os trechos são iguais nos dois sentidos, a volta leva o mesmo tempo da ida. Ir até Vila Sônia e voltar custa 46 min só de deslocamento, quase o tempo de um serviço normal (40 min). Isso pesa bastante no plano do turno.

---

## Atividade 3 - Plano do turno com fila e pilha

### Regras (`planejar_turno(base, horas)`, em `turno.py`)

1. As escadas com pelo menos uma leitura em alerta entram em duas filas (listas), **na ordem do primeiro alerta**: `fila_critica` e `fila_normal`.
2. A fila crítica é atendida antes da normal, retirando com `pop(0)` (fila: o primeiro que entra é o primeiro que sai).
3. **Custo = ida + serviço + volta**, com serviço de **60 min** (crítica) ou **40 min** (não crítica).
4. Se o custo cabe no que sobra do turno, a escada vai para a **agenda** (`append`), com horário de início e fim. Se não cabe, vai para **pendentes**, e tentamos a próxima.
5. **Perda de 1 hora** (`perder_hora`): a agenda é desfeita com `pop()` (pilha: o último agendado sai primeiro) até caber no novo limite. As escadas desfeitas vão para o fim dos pendentes.

Premissas: o turno começa às **08:00**, sem pausas, e a equipe volta à base depois de cada atendimento.

### Escadas em alerta

20 escadas: 10 críticas e 10 não críticas. O custo de cada atendimento vai de 40 min (não crítica na própria base) a 106 min (crítica em Vila Sônia).

### Resultados

| Turno | Na agenda | Pendentes | Tempo usado | Perdendo 1 h: na agenda | Tempo usado (−1 h) |
|---|---|---|---|---|---|
| 4 h (240 min) | 3 | 17 | 228 min | 1 | 88 / 180 min |
| 6 h (360 min) | 4 | 16 | 332 min | 3 | 268 / 300 min |
| 8 h (480 min) | 6 | 14 | 464 min | 5 | 400 / 420 min |

Agenda do turno de 8 h:

| # | Escada | Grupo | Estação | Custo | Início | Fim |
|---|---|---|---|---|---|---|
| 1 | ESC-050 | crítica | Pinheiros | 88 | 08:00 | 09:28 |
| 2 | ESC-016 | crítica | São Paulo-Morumbi | 100 | 09:28 | 11:08 |
| 3 | ESC-034 | crítica | Fradique Coutinho | 80 | 11:08 | 12:28 |
| 4 | ESC-037 | crítica | República | 64 | 12:28 | 13:32 |
| 5 | ESC-030 | crítica | Higienópolis-Mackenzie | 68 | 13:32 | 14:40 |
| 6 | ESC-025 | crítica | República | 64 | 14:40 | 15:44 |

A rota de cada atendimento (ida e volta), as agendas de 4 e 6 h e a lista completa de pendentes de cada cenário estão no notebook e em `saidas/planos_turno.csv` (uma linha por escada, com turno, cenário, situação, rota, início e fim).

### Interpretação

- **O gargalo é a capacidade do turno, não a ordem.** Com 20 escadas em alerta e custo de 40 a 106 min, nem o turno de 8 h atende todas as críticas: atende 6 e deixa 14 pendentes (4 delas críticas).
- **Uma não crítica pode entrar antes de uma crítica.** No turno de 4 h, a ESC-023 (não crítica, na própria base Luz, 40 min) entra na agenda enquanto 8 críticas ficam pendentes. Depois das duas primeiras críticas, sobram 52 min; as outras críticas custam 64 min ou mais e não cabem, mas a ESC-023 cabe. Ou seja, a fila garante a **ordem de tentativa**, não que toda crítica seja atendida antes de qualquer normal. Escolhemos continuar tentando depois de uma escada que não cabe porque parar desperdiçaria o tempo que sobra.
- **Perda de 1 hora:** o `pop()` tira primeiro o último agendado, que é o de menor prioridade. No turno de 4 h, isso tira duas escadas (ESC-023 e ESC-016), porque tirar só a primeira ainda deixa 188 min, acima dos 180 do novo limite. Sobram 92 min livres, que a regra do enunciado não tenta preencher de novo.
- **A distância da base pesa.** Escadas em São Paulo-Morumbi e Vila Sônia gastam 40 a 46 min só de deslocamento. Uma segunda base no meio da linha (por exemplo, Paulista ou Pinheiros) reduziria bastante esse custo.

---

## Premissas do grupo

Estas são suposições do trabalho, não medições. Se mudarem, os resultados das Atividades 2 e 3 mudam:

- Minutos entre estações (tabela da Atividade 2).
- Base em Luz, na primeira posição da linha.
- Tempo de serviço: 60 min (crítica) e 40 min (não crítica).
- Turno de 4, 6 ou 8 horas, começando às 08:00, sem pausas.
- A equipe volta à base depois de cada atendimento.
- A perda de 1 hora é simulada.

## Limitações

- Os dados são sintéticos: mostram como o método se comporta, não a operação real.
- Uma única equipe e uma única base.
- Tempo de serviço fixo por grupo; na prática, ele varia com o tipo de falha.
- A regra do turno é gulosa: não procura a melhor combinação de escadas. Encontrar a combinação ótima seria outro problema (parecido com o problema da mochila, que dá para resolver com programação dinâmica numa próxima sprint).

## Conclusão

A busca binária faz cerca de 3× menos comparações que a linear para achar um ID, e a vantagem cresce com o tamanho da lista, desde que a lista esteja ordenada pelo mesmo critério usado na comparação. A pilha gera a rota de volta na ordem inversa sem precisar inverter listas, e a fila garante a ordem de atendimento dentro de cada grupo.

O resultado mais importante é o do planejamento: com as premissas atuais, um turno não cobre todas as escadas em alerta, nem só as críticas. Antes de qualquer decisão, o próximo passo é validar os tempos de deslocamento e de serviço com a equipe de manutenção da Motiva e avaliar uma segunda base.
