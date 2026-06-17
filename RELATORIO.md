# Relatorio tecnico - estruturas, Big-O e escolhas

## Visao geral

O sistema foi dividido em camadas:

- `modelos.py`: classes de dados e validacoes.
- `estruturas.py`: lista encadeada, busca binaria recursiva e merge sort.
- `servico.py`: regras de negocio.
- `arquivos.py`: persistencia JSON.
- `relatorios.py`: exportacao CSV.
- `interface.py`: menu de terminal.

Essa separacao evita codigo duplicado e facilita testes unitarios.

## Vetor nao ordenado

O vetor `clientes_temporarios` guarda os clientes na ordem de cadastro. Ele
representa o vetor nao ordenado pedido no projeto.

Insercao no final tem custo `O(1)`. Operacoes lineares nesse vetor, como
percorrer cadastros, tem custo `O(n)`.

## Vetor ordenado e busca binaria

O vetor `clientes_por_id` guarda referencias aos mesmos clientes, mas sempre
ordenadas pelo `id`.

A busca rapida por cliente usa busca binaria recursiva. Como o vetor esta
ordenado e o id e unico, a cada chamada recursiva metade do intervalo e
descartada. A complexidade da busca e `O(log n)`.

A insercao no vetor ordenado pode deslocar elementos, por isso custa `O(n)`.
Essa troca e aceitavel porque o requisito exige busca rapida por id.

## Fila comum e fila de prioridade

O sistema usa duas filas:

- `fila_prioridade`: clientes prioritarios.
- `fila_comum`: clientes comuns.

Ao chamar o proximo atendimento, a fila de prioridade e consultada primeiro.
Se ela estiver vazia, o sistema usa a fila comum. Como cada fila e uma
estrutura FIFO, a ordem de chegada e preservada dentro da mesma prioridade.

Inserir e remover do inicio/fim da fila com `deque` tem custo `O(1)`.

## Pilha para desfazer

Quando um atendimento e finalizado, o registro vai para o historico e uma
copia da acao fica em `pilha_desfazer`.

Ao desfazer, o ultimo item inserido e removido primeiro, seguindo LIFO
(`last in, first out`). As operacoes de empilhar e desempilhar custam `O(1)`.

## Lista encadeada

A classe `ListaEncadeadaClientes` armazena nos com referencia para o proximo
cliente. Ela e usada na remocao de clientes inativos.

Para remover inativos, o sistema percorre a lista uma vez, ajustando os
ponteiros dos nos. O custo e `O(n)`.

Antes da remocao, o sistema verifica se algum cliente inativo tem atendimento
em fila ou em andamento. Se tiver, a remocao e bloqueada.

## Ordenacao com merge sort

O top 5 clientes mais atendidos usa `merge_sort`, implementado de forma
recursiva. A lista de contagens e dividida em metades, ordenada e intercalada.

A complexidade do merge sort e `O(n log n)`.

## Recursao

O projeto usa recursao em duas rotinas:

- busca binaria por cliente;
- merge sort dos relatorios.

Isso atende ao requisito de recursao e tambem se encaixa bem nos algoritmos
escolhidos.

## Persistencia

O estado completo do sistema e salvo em `dados/estado.json`, incluindo:

- clientes;
- atendentes;
- filas;
- atendimentos em andamento;
- historico;
- proximo id de atendimento.

JSON foi escolhido por ser legivel, simples e suficiente sem bibliotecas
externas.

## Regras de negocio atendidas

- Cliente prioritario e chamado antes do comum.
- Ordem de chegada e mantida dentro da mesma fila.
- Atendente nao atende dois clientes ao mesmo tempo.
- Nao e permitido finalizar atendimento sem atendimento em andamento.
- Nao e permitido desativar/remover cliente com atendimento aberto.
- Entradas invalidas sao tratadas com mensagens amigaveis.
