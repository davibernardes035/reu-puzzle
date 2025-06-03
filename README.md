# Solucionador de Quebra-Cabeça "Reu"

![Image](https://github.com/user-attachments/assets/1f466ed0-ce7b-4e23-aca2-f90360a32190)

## 1. Descrição do Projeto

Este projeto visa encontrar a solução para um quebra-cabeça de deslizamento de peças em um tabuleiro bidimensional. O objetivo é mover uma peça específica (REU) até que ela enconste na base do tabuleiro (conforme a marcação), manipulando outras peças no tabuleiro através de movimentos de deslizamento. A solução busca o caminho ótimo (menor número de movimentos) utilizando o algoritmo A*.

## 2. O Problema do Quebra-Cabeça

### 2.1. Tabuleiro Inicial

Minha escolha para representar o tabuleiro foi uma matriz 5x4, dessa forma o estado inicial do tabuleiro  é:

``` python
[[1, 2, 2, 3],
 [1, 2, 2, 3],
 [4, 5, 5, 6],
 [4, 7, 8, 6],
 [9, 0, 0, 10]]
```


### 2.2. Definição das Peças

As peças são representadas por números inteiros no tabuleiro. Peças que ocupam múltiplas células são representadas pelo mesmo número nessas células. Suas formas (altura x largura) são:

* Peça '0': Espaço vazio
* Peça '1': 2x1
* Peça '2': 2x2 (Peça principal a ser movida)
* Peça '3': 2x1
* Peça '4': 2x1
* Peça '5': 1x2
* Peça '6': 2x1
* Peça '7': 1x1
* Peça '8': 1x1
* Peça '9': 1x1
* Peça '10': 1x1

### 2.3. Regras de Movimento

* As peças se movem como blocos inteiros, mantendo sua forma.
* Nenhuma peça pode girar.
* **Peça '2' (2x2):** Pode mover-se para cima, baixo, esquerda ou direita se as duas novas células que ela ocuparia no destino estiverem vazias (valor '0').
* **Outras Peças (1x1, 2x1, 1x2):** Podem mover-se se todas as novas células que ocupariam no destino estiverem vazias (valor '0').

### 2.4. Estado Objetivo

O objetivo é posicionar a peça '2' de forma que seu canto superior esquerdo esteja na célula `(3,1)` (linha 3, coluna 1, indexado a partir de 0). Isso significa que a peça '2' ocupará as células `(3,1)`, `(3,2)`, `(4,1)` e `(4,2)`.

## 3. Desenvolvimento da Solução

A solução para este quebra-cabeça foi desenvolvida iterativamente:

### 3.1. Abordagem Inicial: Busca em Largura (BFS)

Inicialmente, uma abordagem com Busca em Largura (BFS) foi considerada e implementada. A BFS garante a solução mais curta em número de movimentos. No entanto, para problemas com soluções que exigem muitos movimentos, a BFS pode se tornar computacionalmente inviável devido ao grande número de estados a serem explorados e armazenados.

### 3.2. Evolução para A\* (A-Estrela)

Dado que a solução esperada poderia ser longa (informações iniciais sugeriam 81 movimentos), o algoritmo A\* foi implementado. O A\* utiliza uma função heurística para guiar a busca de forma mais eficiente em direção ao objetivo, sendo mais adequado para espaços de busca maiores.

#### 3.2.1. Função Heurística (`heuristic_astar`)

A função heurística desenvolvida para o A\* calcula o custo estimado para alcançar o objetivo (`h_cost`) da seguinte forma:

1.  **Distância de Manhattan:** A distância de Manhattan entre a posição atual do canto superior esquerdo da peça '2' e sua posição objetivo `(3,1)`.
2.  **Penalidade de Bloqueio:** Uma penalidade adicional é aplicada se qualquer célula na área de destino 2x2 da peça '2' estiver ocupada por outra peça que não seja a própria peça '2' ou um espaço vazio. Cada peça bloqueadora distinta adiciona +1 à heurística, pois exigirá pelo menos um movimento para ser removida.

Essa heurística foi projetada para ser admissível, o que é um requisito para o A\* encontrar a solução ótima.

#### 3.2.2. Iterações e Resultados

O algoritmo A\* foi executado com um limite de iterações progressivamente maior. Após aproximadamente 9.6 milhões de iterações, uma solução foi encontrada:

* **Número de Movimentos da Solução Encontrada: 116 movimentos.**

Este resultado difere da informação inicial de uma solução ótima de 81 movimentos. Se a heurística é admissível e a implementação do A\* está correta, a solução de 116 movimentos é a ideal para o problema *exatamente como definido e fornecido ao algoritmo*. A discrepância sugere que a informação de 81 movimentos pode ser para uma variação do problema.

### 3.3. Análise da Solução e Replay

Para analisar a solução encontrada, foi implementada uma funcionalidade que permite:
* Aplicar sequencialmente cada movimento do caminho da solução a um tabuleiro.
* Salvar o estado do tabuleiro após cada movimento em um arquivo de texto (`.txt`), facilitando a revisão e compreensão da sequência de 116 movimentos.

## 4. Estrutura do Código (Principais Componentes)

O script Python desenvolvido inclui as seguintes funções principais:

* `solve_puzzle_astar(initial_board)`: A função principal que implementa o algoritmo A\*.
* `heuristic_astar(board_state, all_pieces_cache)`: Calcula o valor heurístico para um dado estado do tabuleiro.
* `get_possible_moves_for_piece(board, piece_id, piece_coords)`: Gera todos os movimentos válidos para uma peça específica.
* `is_goal_state(board_state)`: Verifica se o estado atual do tabuleiro é o estado objetivo.
* `get_all_pieces_coords(board)`: Identifica as coordenadas de todas as peças no tabuleiro.
* `apply_move_to_board(board, piece_id, move_name, all_pieces)`: Aplica um movimento específico a um tabuleiro (usado para replay).
* `save_replay_to_file(initial_board, solution_path, filename)`: Salva o replay da solução em um arquivo.
* Constantes como `PIECE_SHAPES`, `TARGET_PIECE_ID_GLOBAL`, `TARGET_TOP_LEFT_COORD_GLOBAL`.

## 5. Como Executar

1.  O código está contido em um único script Python.
2.  Defina o `initial_board_config` no bloco `if __name__ == "__main__":`.
3.  Execute o script. A função `solve_puzzle_astar` será chamada.
4.  Se uma solução for encontrada:
    * O número de movimentos será impresso no console.
    * Uma chamada para `save_replay_to_file` salvará o passo a passo em um arquivo de texto (por exemplo, `replay_A_star_solucao.txt`).
    * Opcionalmente, o caminho da solução pode ser impresso no console descomentando as linhas relevantes.
5.  Se o limite de iterações for atingido antes de encontrar uma solução, o tabuleiro do nó mais promissor na fila será impresso.
