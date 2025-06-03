import heapq
import copy # Para cópias de listas/objetos, se necessário

# --- DEFINIÇÕES GLOBAIS E CONSTANTES ---
PIECE_SHAPES = {
    1: (2, 1), 2: (2, 2), 3: (2, 1), 4: (2, 1),
    5: (1, 2), 6: (2, 1), 7: (1, 1), 8: (1, 1),
    9: (1, 1), 10: (1, 1)
}
TARGET_PIECE_ID_GLOBAL = 2
TARGET_TOP_LEFT_COORD_GLOBAL = (3, 1)

# --- FUNÇÕES AUXILIARES BÁSICAS ---
def board_to_tuple(b):
    return tuple(map(tuple, b))

def get_all_pieces_coords(board):
    pieces = {}
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            val = board[r][c]
            if val != 0:
                if val not in pieces:
                    pieces[val] = []
                pieces[val].append((r, c))
    for val in pieces:
        pieces[val].sort()
    return pieces

# --- FUNÇÃO PARA GERAR MOVIMENTOS POSSÍVEIS ---
def get_possible_moves_for_piece(board, piece_id, piece_coords):
    moves = []
    rows, cols = len(board), len(board[0])
    if piece_id not in PIECE_SHAPES: return []
    shape = PIECE_SHAPES[piece_id]
    h, w = shape
    if not piece_coords: return []
    r_anchor, c_anchor = piece_coords[0]

    for dr, dc, move_name in [(0, 1, "direita"), (0, -1, "esquerda"),
                               (1, 0, "baixo"), (-1, 0, "cima")]:
        nr_anchor, nc_anchor = r_anchor + dr, c_anchor + dc
        if not (0 <= nr_anchor < rows and 0 <= nc_anchor < cols and \
                0 <= nr_anchor + h - 1 < rows and 0 <= nc_anchor + w - 1 < cols):
            continue

        target_empty_cells_coords = []
        if dc == 1:
            for i in range(h): target_empty_cells_coords.append((r_anchor + i, c_anchor + w))
        elif dc == -1:
            for i in range(h): target_empty_cells_coords.append((r_anchor + i, c_anchor - 1))
        elif dr == 1:
            for i in range(w): target_empty_cells_coords.append((r_anchor + h, c_anchor + i))
        elif dr == -1:
            for i in range(w): target_empty_cells_coords.append((r_anchor - 1, c_anchor + i))
        
        valid_target_coords = True
        for tr, tc in target_empty_cells_coords:
            if not (0 <= tr < rows and 0 <= tc < cols):
                valid_target_coords = False; break
        if not valid_target_coords: continue

        move_is_valid = True
        if piece_id == TARGET_PIECE_ID_GLOBAL: # Peça '2'
            if len(target_empty_cells_coords) != 2: move_is_valid = False
            else:
                for tr, tc in target_empty_cells_coords:
                    if board[tr][tc] != 0: move_is_valid = False; break
        else: # Outras peças
            if not target_empty_cells_coords: move_is_valid = False
            else:
                for tr, tc in target_empty_cells_coords:
                    if board[tr][tc] != 0: move_is_valid = False; break
        
        if move_is_valid:
            new_board = [row[:] for row in board]
            for pr, pc in piece_coords: new_board[pr][pc] = 0
            for i in range(h):
                for j in range(w): new_board[nr_anchor + i][nc_anchor + j] = piece_id
            moves.append(((piece_id, move_name), new_board))
    return moves

# --- FUNÇÃO DE VERIFICAÇÃO DO ESTADO OBJETIVO ---
def is_goal_state(board_state):
    r_target, c_target = TARGET_TOP_LEFT_COORD_GLOBAL
    h_target, w_target = PIECE_SHAPES[TARGET_PIECE_ID_GLOBAL]
    rows, cols = len(board_state), len(board_state[0])

    for r_offset in range(h_target):
        for c_offset in range(w_target):
            check_r, check_c = r_target + r_offset, c_target + c_offset
            if not (0 <= check_r < rows and 0 <= check_c < cols and \
                    board_state[check_r][check_c] == TARGET_PIECE_ID_GLOBAL):
                return False
    
    count_target_piece_cells = 0
    for r in range(rows):
        for c in range(cols):
            if board_state[r][c] == TARGET_PIECE_ID_GLOBAL:
                count_target_piece_cells +=1
    return count_target_piece_cells == (h_target * w_target)

# --- FUNÇÃO HEURÍSTICA PARA A* ---
def heuristic_astar(board_state, all_pieces_cache=None):
    target_piece_id = TARGET_PIECE_ID_GLOBAL
    target_coord_top_left = TARGET_TOP_LEFT_COORD_GLOBAL
    rows, cols = len(board_state), len(board_state[0])
    h_cost = 0

    if all_pieces_cache is None:
        all_pieces_cache = get_all_pieces_coords(board_state)
    
    target_piece_current_coords_list = all_pieces_cache.get(target_piece_id)
    if not target_piece_current_coords_list: return float('inf') 
    current_r_anchor, current_c_anchor = target_piece_current_coords_list[0]

    target_r_goal, target_c_goal = target_coord_top_left
    h_cost += abs(current_r_anchor - target_r_goal) + abs(current_c_anchor - target_c_goal)

    if target_piece_id == TARGET_PIECE_ID_GLOBAL:
        blocking_penalty = 0
        piece_h_target, piece_w_target = PIECE_SHAPES[target_piece_id]
        for r_offset in range(piece_h_target):
            for c_offset in range(piece_w_target):
                r_cell = target_r_goal + r_offset
                c_cell = target_c_goal + c_offset
                if 0 <= r_cell < rows and 0 <= c_cell < cols:
                    cell_content = board_state[r_cell][c_cell]
                    if cell_content != 0 and cell_content != target_piece_id:
                        blocking_penalty += 1
                else: return float('inf') 
        h_cost += blocking_penalty
    return h_cost

# --- FUNÇÃO SOLUCIONADORA A* ---
def solve_puzzle_astar(initial_board):
    open_set_pq = []
    entry_count = 0
    initial_board_tuple = board_to_tuple(initial_board)
    g_costs = {initial_board_tuple: 0}
    initial_all_pieces = get_all_pieces_coords(initial_board)
    h_initial = heuristic_astar(initial_board, initial_all_pieces)
    f_initial = 0 + h_initial

    heapq.heappush(open_set_pq, (f_initial, 0, entry_count, initial_board, [])) # f, g, count, state, path
    entry_count += 1
    
    max_iterations = 20000000 # Exemplo: 20 milhões de iterações
    iterations = 0
    solution_found = False
    print(f"Iniciando A* com heurística revisada... (limite de {max_iterations} iterações)")

    while open_set_pq:
        iterations += 1
        if iterations % 500000 == 0: # Log de progresso
            f_min_val = open_set_pq[0][0] if open_set_pq else 'N/A'
            print(f"A*: Iteração {iterations}, Tamanho da Fila: {len(open_set_pq)}, f_min: {f_min_val}")
        
        if iterations > max_iterations:
            print(f"A*: Limite de iterações ({max_iterations}) atingido.")
            if open_set_pq:
                best_f, best_g, _, best_board_list, best_path = open_set_pq[0]
                print("\nTabuleiro do nó mais promissor na fila ao atingir o limite de iterações:")
                print(f"(f_cost={best_f}, g_cost={best_g}, profundidade do caminho={len(best_path)})")
                for row in best_board_list: print(row)
            else: print("\nA fila de prioridade estava vazia ao atingir o limite de iterações.")
            return None

        f_cost_curr, g_cost_curr, _, current_board_list, current_path = heapq.heappop(open_set_pq)
        current_board_tuple = board_to_tuple(current_board_list)

        if g_cost_curr > g_costs.get(current_board_tuple, float('inf')): continue

        if is_goal_state(current_board_list):
            print(f"A*: Solução encontrada após {iterations} iterações.")
            solution_found = True
            return current_path 

        current_all_pieces = get_all_pieces_coords(current_board_list)
        sorted_piece_ids = sorted(current_all_pieces.keys())

        for piece_id_to_move in sorted_piece_ids:
            if piece_id_to_move == 0: continue
            piece_current_coords = current_all_pieces[piece_id_to_move]
            possible_next_moves = get_possible_moves_for_piece(current_board_list, piece_id_to_move, piece_current_coords)

            for (move_info, next_board_state_list) in possible_next_moves:
                next_board_tuple = board_to_tuple(next_board_state_list)
                tentative_g_cost = g_cost_curr + 1

                if tentative_g_cost < g_costs.get(next_board_tuple, float('inf')):
                    g_costs[next_board_tuple] = tentative_g_cost
                    next_all_pieces = get_all_pieces_coords(next_board_state_list)
                    h_cost_next = heuristic_astar(next_board_state_list, next_all_pieces)
                    f_cost_next = tentative_g_cost + h_cost_next
                    new_path = current_path + [move_info]
                    heapq.heappush(open_set_pq, (f_cost_next, tentative_g_cost, entry_count, next_board_state_list, new_path))
                    entry_count += 1
    
    if not solution_found:
        print(f"A*: Nenhuma solução encontrada após {iterations} iterações (fila vazia).")
    return None

# --- FUNÇÕES PARA REPLAY DA SOLUÇÃO ---
def apply_move_to_board(board, piece_id_to_move, move_name, all_pieces_on_board):
    if piece_id_to_move not in PIECE_SHAPES: return None
    piece_current_coords = all_pieces_on_board.get(piece_id_to_move)
    if not piece_current_coords: return None
    shape = PIECE_SHAPES[piece_id_to_move]
    h, w = shape
    r_anchor, c_anchor = piece_current_coords[0]
    dr, dc = 0, 0
    if move_name == "direita": dc = 1
    elif move_name == "esquerda": dc = -1
    elif move_name == "baixo": dr = 1
    elif move_name == "cima": dr = -1
    else: return None
    nr_anchor, nc_anchor = r_anchor + dr, c_anchor + dc
    new_board = [row[:] for row in board]
    for pr, pc in piece_current_coords: new_board[pr][pc] = 0
    rows, cols = len(board), len(board[0])
    if not (0 <= nr_anchor < rows and 0 <= nc_anchor < cols and \
            0 <= nr_anchor + h - 1 < rows and 0 <= nc_anchor + w - 1 < cols):
        return None
    for i in range(h):
        for j in range(w): new_board[nr_anchor + i][nc_anchor + j] = piece_id_to_move
    return new_board

def save_replay_to_file(initial_board, solution_path, filename="solution_replay.txt"):
    if not solution_path:
        print("Caminho da solução está vazio. Nada para salvar.")
        return
    try:
        with open(filename, "w", encoding="utf-8") as log_file:
            current_board_for_replay = [row[:] for row in initial_board]
            log_file.write("--- Tabuleiro Inicial ---\n")
            for r_idx, row_val in enumerate(current_board_for_replay):
                log_file.write(" ".join(map(lambda x: f"{x:2}", row_val)) + "\n")
            log_file.write("-" * (len(current_board_for_replay[0]) * 3) + "\n\n")

            for i, (piece_id, move_direction) in enumerate(solution_path):
                log_file.write(f"--- Movimento {i+1}: Peça {piece_id} -> {move_direction} ---\n")
                all_pieces_in_current_board = get_all_pieces_coords(current_board_for_replay)
                next_board_state = apply_move_to_board(current_board_for_replay, piece_id, move_direction, all_pieces_in_current_board)
                if next_board_state is None:
                    error_message = (f"ERRO ao aplicar o movimento {i+1} (Peça {piece_id} -> {move_direction}). Replay interrompido.\n")
                    print(error_message)
                    log_file.write(error_message)
                    log_file.write("Tabuleiro antes do erro:\n")
                    for r_idx, row_val in enumerate(current_board_for_replay):
                         log_file.write(" ".join(map(lambda x: f"{x:2}", row_val)) + "\n")
                    break
                current_board_for_replay = next_board_state
                for r_idx, row_val in enumerate(current_board_for_replay):
                    log_file.write(" ".join(map(lambda x: f"{x:2}", row_val)) + "\n")
                log_file.write("-" * (len(current_board_for_replay[0]) * 3) + "\n\n")
            print(f"Replay da solução salvo em: {filename}")
    except IOError: print(f"Erro: Não foi possível escrever no arquivo {filename}")
    except Exception as e: print(f"Ocorreu um erro inesperado durante o salvamento do replay: {e}")

# --- BLOCO PRINCIPAL DE EXECUÇÃO ---
if __name__ == "__main__":
    initial_board_config = [
        [1, 2, 2, 3], [1, 2, 2, 3], [4, 5, 5, 6],
        [4, 7, 8, 6], [9, 0, 0, 10]
    ]

    print("Tabuleiro Inicial:")
    for row in initial_board_config:
        print(row)
    print(f"\nObjetivo: Peça {TARGET_PIECE_ID_GLOBAL} no canto superior esquerdo em {TARGET_TOP_LEFT_COORD_GLOBAL}")
    
    # 1. Executa o A* e armazena o caminho da solução
    # Esta chamada pode demorar MUITO se a solução for longa.
    returned_solution_path = solve_puzzle_astar(initial_board_config) 

    # 2. Verifica se uma solução foi encontrada
    if returned_solution_path:
        print("\nSolução encontrada pelo A*!")
        print(f"Número de movimentos: {len(returned_solution_path)}")
        
        # Opção: Imprimir o caminho da solução no console 
        # print("\nSequência de movimentos (Peça, Direção):")
        # for i, move in enumerate(returned_solution_path):
        #     print(f"{i+1}. Peça {move[0]} -> {move[1]}")

        # 3. Salva o replay da solução em um arquivo de texto
        print("\nSalvando o replay da solução em arquivo...")
        save_replay_to_file(initial_board_config, returned_solution_path, "replay_A_star_solucao81moves.txt")
        
    else:
        # A função solve_puzzle_astar já imprime sua própria mensagem se não encontrar solução
        # ou atingir o limite de iterações.
        print("\nNenhuma solução foi encontrada ou o limite de iterações foi atingido (conforme log acima).")