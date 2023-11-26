from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from board_abalone import BoardAbalone



#Table de début 
#Optimisation :
#-Solution acceptable
#-Structure de données plus rapide
# etc...
class MyPlayer(PlayerAbalone):
    """
    Player class for Abalone game.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "bob", time_limit: float=60*15,*args) -> None:
        """
        Initialize the PlayerAbalone instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob")
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type,name,time_limit,*args)
        self.transposition_table = {}
        self.plays = 0
        
        
        


    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        
        print("plays" + str(self.plays))
        best_move = None
        best_value = float('-inf')
        depth = 3
        print(f"Nombre d'actions possibles: {len(current_state.generate_possible_actions())}")
        s = 10

        
        for action in current_state.generate_possible_actions():
            if(s==0):
                self.plays += 1
                return best_move
            
            move_value = minimax_alpha_beta(action.get_next_game_state(), depth, float('-inf'),float("inf"), True, self.transposition_table,self.plays)
            #move_value =  minimax(action.get_next_game_state(), depth, True)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            s -= 1
        
        self.plays += 1
        return best_move





def total_distance(positions):
    total_dist = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            total_dist += manhattanDist(positions[i], positions[j])
    return total_dist

def distance_to_closest_edge(position, edges):
    """Calculate the minimum Manhattan distance from a position to any edge."""
    return min(abs(position[0] - edge[0]) + abs(position[1] - edge[1]) for edge in edges)


def get_adjacent_positions(position):
    i, j = position
    # Les directions changent en fonction de la ligne sur laquelle vous vous trouvez
    if i % 2 == 0:  # Ajustez en fonction de votre représentation du plateau
        directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
    else:
        directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
    return [(i + di, j + dj) for di, dj in directions]

# Fonction pour compter les pièces ennemies adjacentes
def count_adjacent_enemies(position, board, player_id):
    adjacent_positions = get_adjacent_positions(position)
    count = 0
    for adj_position in adjacent_positions:
        if adj_position in board:
            p = board[adj_position]
            if p is not None and p.get_owner_id() != player_id:
                count += 1
    return count

# Fonction pour compter les pièces ennemies adjacentes sachant que les pieces sont en formation
def count_adjacent_enemies_in_formation(position, board, player_id):
    adjacent_positions = get_adjacent_positions(position)
    count = 0
    for adj_position in adjacent_positions:
        if adj_position in board:
            p = board[adj_position]
            if p is not None and p.get_owner_id() != player_id and is_in_formation(position, board, player_id):
                count += 1
    return count




def is_in_formation(position, board, player_id):
    i, j = position
    # Diagonales pour les lignes paires et impaires
    if i % 2 == 0:
        diag_directions = [(-1, 0), (1, 0), (0, 1), (1, 1), (0, -1), (-1, -1)]
    else:
        diag_directions = [(-1, -1), (1, -1), (0, 1), (1, 0), (0, -1), (-1, 0)]

    # Vérifier les formations de trois billes
    for k in range(0, len(diag_directions), 2):
        pos1 = (i + diag_directions[k][0], j + diag_directions[k][1])
        pos2 = (i + diag_directions[k+1][0], j + diag_directions[k+1][1])
        if pos1 in board and pos2 in board:
            p1 = board.get(pos1)
            p2 = board.get(pos2)
            if p1 and p2 and p1.get_owner_id() == player_id and p2.get_owner_id() == player_id:
                return True  # La bille est au centre d'une formation de trois billes.

    # Vérifier les formations de deux billes (en tant que milieu ou extrémité)
    for dir in diag_directions:
        pos = (i + dir[0], j + dir[1])
        if pos in board:
            p = board.get(pos)
            if p and p.get_owner_id() == player_id:
                # Vérifier si la bille actuelle et la bille adjacente forment une ligne de deux billes
                if is_in_line(position, pos, board, player_id):
                    return True

    return False

def is_in_line(pos1, pos2, board, player_id):
    # Calcule la direction de la ligne
    dir_line = (pos2[0] - pos1[0], pos2[1] - pos1[1])

    # Vérifier dans les deux directions pour une ligne de deux billes
    pos_before = (pos1[0] - dir_line[0], pos1[1] - dir_line[1])
    pos_after = (pos2[0] + dir_line[0], pos2[1] + dir_line[1])

    # Vérifier si la position avant ou après appartient également au même joueur
    if pos_before in board:
        p_before = board.get(pos_before)
        if p_before and p_before.get_owner_id() == player_id:
            return True
    if pos_after in board:
        p_after = board.get(pos_after)
        if p_after and p_after.get_owner_id() == player_id:
            return True

    return False


# Le but serait maintenant de faire varier les h selon l'état du jeu 
# 1) Rush le centre + dispersement
# 2)Rush ennemi en formation

def evaluate_state(game_state: GameState,plays) -> float:
    # Logic to evaluate the state
    
    player = game_state.next_player
    score = 0


    current_rep = game_state.get_rep()
    b = current_rep.get_env()
    dim = current_rep.get_dimensions()
    
    
    center = (dim[0]//2, dim[1]//2)
    
    distance_factor = 0.5  
    distance_factor_e = 1
    enemies_factor = 2
    dispersement_factor = 0.02  #if too high the player send the piece out of the board
    dispersement_factor_e = 0.05

    #Amélioation : distance_factor diminue au fur et à mesure de la game
    distance_factor -= plays *0.02
    if(distance_factor < 0) : distance_factor = 0.2
    #distance_factor_e augmante pour rendre le joueur plus aggresif 
    distance_factor_e += plays *0.04
    

    #Favorise une formation groupée
    dispersement_factor -= plays *0.001
    if(dispersement_factor < 0) : dispersement_factor = 0.01
    list_player = [ (i,j) for i,j in list(b.keys()) if b.get((i, j), None).get_owner_id() == player.get_id()]
    score -= total_distance(list_player) *dispersement_factor

   

    #Favorise un dispersement de l'ennemi
    list_not_player = [ (i,j) for i,j in list(b.keys()) if b.get((i, j), None).get_owner_id() != player.get_id()]
    score += total_distance(list_not_player) *dispersement_factor_e
    
    
    for i, j in list(b.keys()):
            
            
            p = b.get((i, j), None)
            distance = manhattanDist(center,[i,j])
            
            if p.get_owner_id() == player.get_id():

                adjacent_enemies = count_adjacent_enemies((i, j), b, player.get_id())
                #adjacent_enemies = count_adjacent_enemies_in_formation((i, j), b, player.get_id())
                score += adjacent_enemies* enemies_factor

                #Favorise une formation en diag
                
                for k,l in list(b.keys()) :
                    if k!= i and j != l:
                        score += 1 if l == j else 0

                #Favorise position offensive --> Proche adversaire, proche bord
                
                
                
                score -= distance_factor * distance   #Favorise un mvt qui rapproche les pieces vers le centre,  V1 
                score +=50  #count the number of piece of the player
                
            else:
                score += distance * distance_factor_e   #Favorise un mvt qui eloigne les pieces advairse du centre

                #score -= distance_edge * distance_factor #Favorise un mvt qui eloigne les pieces advairse du centre
                score -=50 #Decrease for every piece of the oponent


    return  score

def manhattanDist(A, B):
            dist = abs(B[0] - A[0]) + abs(B[1] - A[1])
            return dist


def minimax_alpha_beta(game_state, depth, alpha, beta, maximizing_player,transposition_table,plays):

    state_hash = hash(str(game_state.get_rep().get_env()))

    if state_hash in transposition_table:
        return transposition_table[state_hash]

    if depth == 0 or game_state.is_done():
        value =  evaluate_state(game_state,plays=plays)
        transposition_table[state_hash] = value
        return value

    if maximizing_player:
        
        max_eval = float('-inf')
        possible_actions = game_state.generate_possible_actions()
        scored_actions = [(action, evaluate_move(action.get_next_game_state(),plays=plays)) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1], reverse=True)#Descending
        s = 10
        for action in scored_actions:
            if(s==0):
                return max_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, False,transposition_table,plays)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        transposition_table[state_hash] = max_eval
        return max_eval
    else:
        
        min_eval = float('inf')
        possible_actions = game_state.generate_possible_actions()

        scored_actions = [(action, evaluate_move(action.get_next_game_state(),plays=plays)) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1]) #Ascending
        s = 10
        for action in scored_actions:
            if(s==0):
                return min_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, True, transposition_table,plays)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        transposition_table[state_hash] = min_eval
        return min_eval


def evaluate_move( game_state,plays):
    # Ici, vous pouvez définir une heuristique rapide pour évaluer le mouvement
    # Par exemple:
    return evaluate_state(game_state,plays)