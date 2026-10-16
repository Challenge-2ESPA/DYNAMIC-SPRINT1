# Challenge Motiva: Dynamic Programming (DP), Sprints 1 e 2

Este projeto resolve a parte de programação (DP) do Challenge Motiva. A Motiva opera escadas rolantes nas estações da linha e quer reduzir o custo de manutenção preventiva, identificando quais escadas precisam de atenção antes de falhar.

## Integrantes

| Nome | RM |
|---|---|
| David Ernesto Mogollon Gama | 567855 |
| Felipe Menezes Santos | 566607 |
| João Antonio Sarracine Faedrich de Souza | 567407 |
| Pedro Henrique Tavares Viana | 567680 |
| Roger de Carvalho Paiva | 566949 |

## Aviso sobre os dados

Os dados são **fictícios**, gerados por `gerar_dataset.py` com uma semente fixa. As premissas de tempo entre estações e de tempo de serviço são suposições do grupo, não medições da Motiva. Por isso, os resultados mostram como o método funciona e o que os números significam, não a situação real da operação.

## Como executar

Rode a partir da pasta do projeto:

```bash
python gerar_dataset.py                       # gera sensores.csv (semente 42)
python main.py sensores.csv linha.csv saidas  # roda todas as análises e grava os resultados em saidas/
python -m unittest discover -s tests -v       # roda os testes automáticos
```

O `main.py` roda em menos de 1 segundo. O `gerar_dataset.py` gera o mesmo `sensores.csv` sempre que rodado, porque a semente é fixa.

Também existe o notebook `SPRINT1notebook.ipynb`, que roda as mesmas análises passo a passo, com explicação em cada parte. Ele foi executado no Google Colab.

## Estrutura do projeto

| Arquivo | O que faz |
|---|---|
| `gerar_dataset.py` | Gera o dataset sintético de sensores e grava `sensores.csv`. |
| `dados.py` | Lê o `sensores.csv`, define a regra de alerta (uma leitura está em alerta se algum sensor sai da faixa normal) e monta a lista de escadas em alerta. |
| `busca.py` | Busca linear, busca binária, primeira leitura com o limite de alertas, soma acumulada e ordenação dos IDs. |
| `linha.py` | Lê a linha de estações e calcula o tempo até cada uma, com a rota de ida e volta usando pilha. |
| `turno.py` | Monta as filas de atendimento e planeja o turno, com a simulação da perda de 1 hora. |
| `main.py` | Liga tudo. Roda todas as análises, imprime o resumo e grava os resultados em `saidas/`. |
| `linha.csv` | Premissa da linha: as 8 estações, na ordem, com os minutos até a próxima. |
| `sensores.csv` | Dataset gerado: 10.000 leituras de 50 escadas. |
| `saidas/` | Resultados gerados pelo `main.py` (CSV e JSON), usados nas tabelas deste README. |
| `tests/` | Testes automáticos de cada módulo (40 testes). |
| `SPRINT1notebook.ipynb` | Notebook que roda as análises com explicação. |

A divisão em vários arquivos foi uma escolha do grupo, para separar cada análise e facilitar a leitura e a correção. Cada módulo tem uma responsabilidade clara. As funções calculam e retornam valores. Só o `main.py` e o bloco principal do `gerar_dataset.py` imprimem na tela e gravam arquivos.

## Dataset sintético

### Por que um dataset sintético

A Motiva ainda não forneceu dados reais de sensores. Por isso, criamos um dataset que imita o comportamento esperado de uma escada rolante, com faixas normais por sensor e três situações de operação.

### Como os dados são gerados

- **Escadas:** 50 escadas, cada uma em uma estação, com grupo "crítica" ou "não crítica" sorteado.
- **Leituras:** uma leitura por hora para cada escada, durante 200 horas, começando em 01/01/2026 às 00:00. Total: 10.000 leituras.
- **Sensores:** vibração, temperatura, corrente, tensão, nível de óleo e velocidade. Cada um tem uma faixa normal, definida em `FAIXAS` no `gerar_dataset.py`.
- **Perfis:** 60% das escadas são saudáveis (30 escadas), 30% estão em desgaste (15 escadas) e 10% têm falha pontual (5 escadas).
  - **Saudável:** todos os sensores ficam dentro da faixa normal, com valores sorteados ao acaso.
  - **Desgaste:** a vibração sobe até 4 unidades, a temperatura sobe até 20 °C e o nível de óleo cai até 30 pontos, de forma gradual, conforme as horas passam.
  - **Falha:** na maioria das horas, a escada é normal, mas cada leitura tem 5% de chance de um pico isolado de vibração (7 a 10) e temperatura (75 a 90).
- **Ordem:** em cada hora, a ordem das escadas é embaralhada, como aconteceria num registro real.
- **Semente:** 42. A semente fixa faz o sorteio ser igual toda vez que o gerador roda.

### Resumo do dataset

| Sensor | Mínimo | Média | Máximo |
|---|---|---|---|
| Vibração (mm/s) | 1,00 | 3,13 | 10,00 |
| Temperatura (°C) | 35,00 | 53,16 | 89,90 |
| Corrente (A) | 10,00 | 17,48 | 25,00 |
| Tensão (V) | 361,00 | 379,84 | 399,00 |
| Nível de óleo (%) | 30,60 | 75,47 | 100,00 |
| Velocidade (m/s) | 0,48 | 0,50 | 0,52 |

Os valores acima da faixa normal vêm dos perfis de desgaste e de falha, não de erro no código.

### Regra de alerta

Uma leitura está em alerta quando **qualquer** sensor sai da faixa normal. O limite conta como normal: vibração de exatamente 4 não dispara alerta. A função `esta_em_alerta`, em `dados.py`, faz essa verificação, e os testes cobrem o caso do limite.

Como os perfis funcionam, as escadas em alerta são as 15 de desgaste e as 5 de falha. As 30 saudáveis nunca saem da faixa.

## Busca linear × busca binária

### O problema

Precisamos encontrar informações sobre escadas e leituras no arquivo de sensores. A pergunta é: qual método é mais eficiente para isso? Medimos o custo de cada busca pelo **número de comparações** de chave. Esse número independe do computador e permite comparar os métodos de forma justa.

### Métodos

- **Busca linear** (`busca_linear`): percorre a lista do início ao fim, comparando um item por vez, até achar o alvo. Não exige lista ordenada, mas o custo cresce com o tamanho da lista.
- **Busca binária** (`busca_binaria`): divide a lista ao meio a cada passo e descarta a metade que não pode conter o alvo. Exige lista ordenada. Cada passo faz duas comparações: primeiro checa se é igual, depois se é menor. Por isso, o código conta essas duas separadamente.

Para as consultas, sorteamos 1.000 IDs de escada com a semente 42. Assim, todos os métodos buscam exatamente os mesmos IDs. Testamos três situações:

1. busca linear no arquivo de leituras;
2. busca linear em uma lista com só os IDs;
3. busca binária na lista de IDs, ordenada pelo número (`ESC-2` vem antes de `ESC-10`).

### Primeira leitura com 5 alertas

Para cada escada, procuramos a primeira leitura em que o número acumulado de alertas chega a 5.

- **Linear:** conta os alertas um a um, até o acumulado chegar a 5 (`primeira_leitura_linear`).
- **Binária:** a soma acumulada de alertas nunca diminui. Por isso, a busca binária pode ser feita sobre essa soma, achando o primeiro ponto em que o valor atinge 5 (`primeira_leitura_binaria`).

Antes de contar, o código confere se os dois métodos acham a mesma posição. Se não acharem, o programa para com erro. Esse teste garante que a busca binária sobre o acumulado está correta.

### Resultados

Consultas por ID (1.000 consultas):

| Método | Total de comparações | Média | Máximo |
|---|---|---|---|
| Linear no arquivo de leituras | 26.305 | 26,3 | 50 |
| Linear na lista de IDs | 25.835 | 25,8 | 50 |
| Binária na lista de IDs | 9.342 | 9,3 | 12 |

Primeira leitura com 5 alertas (50 escadas):

- 20 escadas chegam a 5 alertas e 30 não chegam.
- Busca linear: 6.828 comparações.
- Busca binária: 390 comparações.

A tabela por escada está no notebook e em `saidas/comparacoes_primeira_leitura.csv`.

### Interpretação

A busca binária faz cerca de um terço das comparações da linear na mesma lista de IDs, e a diferença cresce com o tamanho da lista. Isso acontece porque ela descarta metade dos candidatos a cada passo, enquanto a linear olha um item por vez.

A linear no arquivo de leituras tem média parecida com a linear na lista de IDs. Isso acontece porque o arquivo embaralha as escadas a cada hora, então a primeira ocorrência de cada escada cai nas primeiras 50 linhas. Esse número depende do arquivo, não só do algoritmo.

## Percurso na linha com pilha

### O problema

Uma equipe sai da base, em Luz, vai até uma estação para dar manutenção e volta. Precisamos saber quanto tempo cada atendimento leva de ida e volta, e qual é a rota de cada um.

### Premissas

A linha tem 8 estações, na ordem abaixo. Os minutos entre estações são premissas do grupo, guardadas em `linha.csv`:

| Trecho | Minutos |
|---|---|
| Luz → República | 3 |
| República → Paulista | 3 |
| Paulista → Oscar Freire | 2 |
| Oscar Freire → Faria Lima | 3 |
| Faria Lima → Pinheiros | 3 |
| Pinheiros → Butantã | 3 |
| Butantã → Vila Sônia | 3 |

A base é Luz, que fica na primeira posição da linha. Como a equipe volta à base, o tempo de ida e volta é sempre o dobro do tempo de ida.

### Método

- **Tempo até a estação** (`tempo_ate`): busca linear pela estação, somando os minutos de cada trecho até chegar nela.
- **Rota de ida e volta** (`rota_ida_e_volta`): usa uma pilha, que é uma estrutura do tipo "o último que entra é o primeiro que sai".
  - Na **ida**, cada estação visitada é empilhada com `append`, até chegar ao destino.
  - Na **volta**, as estações são desempilhadas com `pop()`, começando no destino e terminando na base.

Usamos pilha porque a volta precisa percorrer exatamente a ida na ordem inversa. A pilha faz isso naturalmente, sem precisar inverter a lista.

### Resultados

| Estação | Ida (min) | Ida e volta (min) |
|---|---|---|
| Luz (base) | 0 | 0 |
| República | 3 | 6 |
| Paulista | 6 | 12 |
| Oscar Freire | 8 | 16 |
| Faria Lima | 11 | 22 |
| Pinheiros | 14 | 28 |
| Butantã | 17 | 34 |
| Vila Sônia | 20 | 40 |

A rota de volta de Vila Sônia, por exemplo, é Vila Sônia → Butantã → Pinheiros → Faria Lima → Oscar Freire → Paulista → República → Luz.

## Plano do turno com fila e pilha

### O problema

Cada turno tem tempo limitado. Precisamos decidir quais escadas em alerta serão atendidas no turno, na ordem certa, e quais ficam para depois.

### Escadas em alerta

Uma escada entra no plano se tiver pelo menos uma leitura em alerta. Para cada uma, consideramos a estação, o grupo e a data do primeiro alerta. Ao todo, são 20 escadas.

### Custo de cada atendimento

Cada atendimento custa:

**custo = tempo de ida e volta + tempo de serviço**

Premissas de tempo de serviço, também do grupo:

- **Crítica:** 60 minutos de serviço.
- **Não crítica:** 40 minutos de serviço.

Com as premissas acima, o custo de cada atendimento fica entre **46 e 94 minutos**.

### Filas

As escadas são organizadas em duas filas, na ordem do primeiro alerta (ou seja, a que alertou antes é atendida antes):

- **Fila crítica:** atendida primeiro (`pop(0)`). Esse é o critério de prioridade.
- **Fila normal:** atendida só depois que a fila crítica acabar.

Usamos fila porque o atendimento segue a ordem de chegada dentro de cada grupo: quem alertou primeiro é atendido primeiro.

### Planejamento do turno

A função `planejar_turno(base, horas)` gera o plano. Ela lê sozinha a linha (`linha.csv`) e as escadas em alerta (`sensores.csv`), mas também aceita esses dados como argumentos opcionais. Assim, os testes podem usar dados de exemplo, sem depender dos arquivos.

O turno tem 4, 6 ou 8 horas, ou seja, 240, 360 ou 480 minutos. Para cada escada, na ordem das filas:

1. calculamos o custo;
2. se o custo cabe no tempo que ainda resta, a escada entra na **agenda** e registramos o horário de início e de fim;
3. se não cabe, a escada vai para **pendentes**, e tentamos a próxima.

A agenda guarda a ordem de atendimento e a rota de ida de cada um.

### Perda de uma hora

Simulamos o caso de a equipe perder 1 hora do turno, por qualquer motivo. A função `perder_hora` remove atendimentos da agenda usando `pop()`, sempre do último que entrou, até o plano caber no novo limite. As escadas removidas vão para o fim dos pendentes.

Desfazemos pelo último a entrar porque, como a agenda segue a ordem de prioridade, os últimos são os de menor prioridade. O plano original não é alterado, então é possível comparar o antes e o depois.

### Resultados

| Turno | Na agenda | Pendentes | Tempo usado | Se perder 1 h: na agenda |
|---|---|---|---|---|
| 4 h (240 min) | 3 | 17 | 214 min | 2 |
| 6 h (360 min) | 5 | 15 | 342 min | 4 |
| 8 h (480 min) | 6 | 14 | 456 min | 5 |

### Interpretação

Com 20 escadas em alerta e custo de 46 a 94 minutos cada, o turno de 8 horas atende só 6. A maioria das escadas fica pendente em todos os cenários. Isso mostra que o gargalo é a **capacidade do turno**, não a ordem de atendimento. Com as premissas atuais, a equipe não consegue atender todas as escadas em alerta em um único turno.

### Por que o planejamento continua depois de uma escada que não cabe

Essa foi uma decisão de regra, e ela tem um efeito que precisa ser conhecido. Quando uma escada não cabe no tempo restante, pulamos para a próxima da fila. A alternativa seria parar na primeira que não cabe. Escolhemos continuar porque parar desperdiçaria o tempo que sobra, que pode ser usado por uma escada menor.

O efeito colateral é este: uma escada crítica cara pode ficar pendente enquanto uma crítica mais barata entra. Por isso, a prioridade é de **ordem de atendimento**, não uma garantia de que todas as críticas serão atendidas antes de qualquer normal.

## Premissas do grupo

Estas são suposições do trabalho, não medições. Se mudarem, os resultados das análises de percurso e de turno mudam:

- Minutos entre estações (tabela da seção de percurso).
- Base em Luz, na primeira posição da linha.
- Tempo de serviço: 60 min para escadas críticas e 40 min para não críticas.
- Turno de 4, 6 ou 8 horas, sem pausas.
- A equipe volta à base após cada atendimento.
- A perda de 1 hora é simulada, não real.
- As escadas do dataset são fictícias.

## Limitações

- Os dados são sintéticos. Os resultados dizem como o método se comporta, não o que acontece na operação real.
- Uma única equipe e uma única base.
- O tempo de serviço é fixo por grupo. Na prática, ele varia com o tipo de falha.
- A regra de planejamento é gulosa: ela não otimiza a escolha entre escadas. Encontrar a combinação ótima de atendimentos seria outro problema, e não foi o escopo deste trabalho.

## Histórico do projeto (controle de versão)

O projeto foi versionado com Git, e o histórico registra a evolução passo a passo. Cada commit descreve uma parte entregue:

1. Gerador do dataset sintético, com testes de tamanho e de reprodutibilidade.
2. README inicial.
3. Regra de alerta e leitura do CSV de sensores, com testes.
4. Buscas linear e binária e primeira leitura com o limite de alertas, com testes.
5. Linha de estações, premissas de tempo e rota de ida e volta com pilha, com testes.
6. Planejamento do turno com filas e pilha, e perda de hora, com testes.
7. `main.py`, que roda todas as análises e grava os resultados.
8. Organização dos testes na pasta `tests/`.

## Conclusão

A busca binária faz menos comparações que a linear, desde que a lista esteja ordenada. A pilha dá a rota de ida e volta na ordem certa, sem precisar inverter listas. A fila garante a ordem de atendimento dentro de cada grupo.

O resultado mais importante, porém, é o do planejamento: com as premissas atuais, um turno não cobre todas as escadas em alerta. Por isso, antes de qualquer decisão sobre a manutenção preventiva, o próximo passo é validar as premissas de tempo com a equipe de manutenção da Motiva.
