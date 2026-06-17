# Sistema Completo de Atendimento e Analise

Sistema de linha de comando em Python para uma clinica ou central de
atendimento. O projeto controla clientes, atendentes, filas, historico,
relatorios, exportacao CSV e analise de desempenho.

## Objetivo

Aplicar os conteudos de estrutura de dados em um sistema completo:

- Python basico e tratamento de entradas.
- Big-O e analise de desempenho.
- Vetor nao ordenado e vetor ordenado.
- Fila comum e fila de prioridade.
- Pilha para desfazer finalizacao.
- Lista encadeada para remocao de clientes inativos.
- Recursao.
- Ordenacao com merge sort.

## Funcionalidades

- Cadastro de clientes com id, nome, telefone, prioridade e status ativo.
- Cadastro de atendentes.
- Abertura de atendimento em fila comum ou fila de prioridade.
- Chamada do proximo atendimento, sempre considerando prioridade.
- Finalizacao com data, duracao, atendente e tempo de espera.
- Historico de atendimentos por cliente.
- Desfazer a ultima finalizacao usando pilha.
- Desativar e remover clientes inativos usando lista encadeada.
- Relatorio de tempo medio de atendimento.
- Exportacao de relatorios em CSV.
- Busca rapida por cliente usando vetor ordenado e busca binaria.
- Filtro de historico e media por data.
- Top 5 clientes mais atendidos.
- Alertas para tempo de espera alto.
- Logs simples de operacoes importantes.

## Estrutura do projeto

```text
Projeto02_Estrutura_de_dados_1/
|-- main.py
|-- requirements.txt
|-- atendimento/
|   |-- __init__.py
|   |-- arquivos.py
|   |-- estruturas.py
|   |-- interface.py
|   |-- logs.py
|   |-- modelos.py
|   |-- relatorios.py
|   `-- servico.py
|-- dados/
|   `-- estado.json
|-- exports/
|-- logs/
|-- tests/
|   `-- test_sistema.py
|-- RELATORIO.md
|-- README.md
`-- .gitignore
```

## Como executar

Abra o terminal na pasta do projeto e execute:

```bash
python main.py
```

O sistema carrega automaticamente o arquivo `dados/estado.json`. As operacoes
que alteram dados salvam o estado novamente no mesmo arquivo.

## Como testar

Execute os testes unitarios:

```bash
python -m unittest discover -s tests
```

Confira tambem a sintaxe dos arquivos Python:

```bash
python -m compileall .
```

## Dados de exemplo

O arquivo `dados/estado.json` ja contem:

- clientes comuns e prioritarios;
- atendentes cadastrados;
- uma fila de prioridade;
- uma fila comum;
- um atendimento em andamento;
- historico de atendimentos finalizados;
- um cliente inativo para testar a remocao.

## Relatorios CSV

No menu, use a opcao `11` para exportar:

- `exports/historico.csv`
- `exports/resumo.csv`
- `exports/top_clientes.csv`

## Observacoes para uso

- Cliente prioritario sempre entra na fila de prioridade.
- Dentro da mesma fila, a ordem de chegada e preservada.
- Um atendente nao pode atender dois clientes ao mesmo tempo.
- Nao e permitido desativar ou remover cliente com atendimento aberto.
- Para remover um cliente, primeiro use a opcao `8` para desativar e depois
  a opcao `9` para remover inativos.
