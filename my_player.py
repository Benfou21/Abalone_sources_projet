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
        
        
        


    def compute_action(self, current_state: GameState, **kwargs) -> Action:
        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """
        best_move = None
        best_value = float('-inf')
        depth = 3
        print(f"Nombre d'actions possibles: {len(current_state.generate_possible_actions())}")
        s = 10

        list_edge = [[0, 0], [0, 1], [0, 7], [0, 8], [1, 0], [1, 7], [1, 8], [2, 0], [2, 8], [3, 8], [5, 8], [6, 0], [6, 8], [7, 0], [7, 7], [7, 8], [8, 0], [8, 1], [8, 7], [8, 8]] 

        current_rep = current_state.get_rep()
        dim = current_rep.get_dimensions()
        edge_distance_matrix = precalculate_edge_distances(current_state,dim,list_edge)
        for action in current_state.generate_possible_actions():
            if(s==0):
                return best_move
            
            move_value = minimax_alpha_beta(action.get_next_game_state(), depth, float('-inf'),float("inf"), True, self.transposition_table,edge_distance_matrix)
            #move_value =  minimax(action.get_next_game_state(), depth, True)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            s -= 1
        print(current_state.next_player)
        print(best_value)
        print(best_move)
        return best_move





def precalculate_edge_distances(game_state: GameState,dimensions, list_edge):
    #On va précalculer les distances des bords de chaque case
    max_x, max_y = dimensions
    edge_distance_matrix = [[0 for _ in range(max_y)] for _ in range(max_x)]
    string =""
    current_rep = game_state.get_rep()
    b = current_rep.get_env()
    board = BoardAbalone(b,dimensions)
    grid_data=board.get_grid() 


    for i in range(9):
            print(i)
            if i % 2 == 1:
                string += " "
            for j in range(9):
                if grid_data[i][j] == BoardAbalone.FORBIDDEN_POS or i in [0,8] or j in  [0,8]:
                    string += "-1"
                    edge_distance_matrix[i][j] = 0              
                else:
                    dist_to_edge = min(
                    min(i, max_x - 1 -i),  # Distance à l'horizontale, plus petite distance du bord gauche ou droit
                    min(j, max_y - 1 - j)   # Distance à la verticale
                    )
                    edge_distance_matrix[i][j] = dist_to_edge
                    string += str(edge_distance_matrix[i][j])+" "

            string += "\n"
    
    print(string)

    return edge_distance_matrix

def total_distance(positions):
    total_dist = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            total_dist += manhattanDist(positions[i], positions[j])
    return total_dist

def distance_to_closest_edge(position, edges):
    """Calculate the minimum Manhattan distance from a position to any edge."""
    return min(abs(position[0] - edge[0]) + abs(position[1] - edge[1]) for edge in edges)

def evaluate_state(game_state: GameState,edge_distance_matrix) -> float:
    # Logic to evaluate the state
    
    player = game_state.next_player
    score = 0


    current_rep = game_state.get_rep()
    b = current_rep.get_env()
    dim = current_rep.get_dimensions()
    
    
#  XX_ _ _ _ _ XX
#  X_ _ _ _ _ _ XX
# X_ _ _ _ _ _ _ X
#  _ _ _ _ _ _ _ _ X
# _ _ _ _ _ _ _ _ _
#  _ _ _ _ _ _ _ _ X
# X_ _ _ _ _ _ _ X
#  X_ _ _ _ _ _ XX
#   XX_ _ _ _ _ XX

    #board = BoardAbalone(b,dim)
    #grid_data=board.get_grid() 
    # for i in range(9):
    #     for j in range(9):
    #         if grid_data[i][j] == BoardAbalone.FORBIDDEN_POS:
    #             string += "  "
    #             list_edge.append([i,j])
    
    # Define the center of the board
    center = (dim[0]//2, dim[1]//2)
    #list_edge = [[0, 0], [0, 1], [0, 7], [0, 8], [1, 0], [1, 7], [1, 8], [2, 0], [2, 8], [3, 8], [5, 8], [6, 0], [6, 8], [7, 0], [7, 7], [7, 8], [8, 0], [8, 1], [8, 7], [8, 8]] 

    
    distance_factor = 0.2  # It needs to be low, under the loss of loosing a piece, otherwise it don't care about loosing a piece
   

    #Favorise une formation groupée
    list_player = [ (i,j) for i,j in list(b.keys()) ]
    score -= total_distance(list_player) *0.01
    
    
    for i, j in list(b.keys()):
            
            p = b.get((i, j), None)
            distance = manhattanDist(center,[i,j])
            #distance_edge = distance_to_closest_edge([i,j],list_edge)   #Fort cout en complexité
            #distance_edge = edge_distance_matrix[i][j]
            if p.get_owner_id() == player.get_id():

                
                #Favorise une formation en diag
                for k,l in list(b.keys()) :
                    if k!= i and j != l:
                        score += 1 if l == j else 0
                

                #Favorise position offensive --> Proche adversaire, proche bord
                
                #score += distance_edge * distance_factor  #Favorise une grande distance des bords (raproche du centre mais surtout écarte du bord)
                score -= distance_factor * distance  #Favorise un mvt qui rapproche les pieces vers le centre,  V1 
                score +=10  #count the number of piece of the player
            else:
                score -= distance * distance_factor   #V1
                #score -= distance_edge * distance_factor #Favorise un mvt qui eloigne les pieces advairse du centre
                score -=10 #Decrease for every piece of the oponent


    return  score

def manhattanDist(A, B):
            dist = abs(B[0] - A[0]) + abs(B[1] - A[1])
            return dist


def minimax_alpha_beta(game_state, depth, alpha, beta, maximizing_player,transposition_table,edge_distance_matrix):

    state_hash = hash(str(game_state.get_rep().get_env()))

    if state_hash in transposition_table:
        return transposition_table[state_hash]

    if depth == 0 or game_state.is_done():
        value =  evaluate_state(game_state,edge_distance_matrix)
        transposition_table[state_hash] = value
        return value

    if maximizing_player:
        
        max_eval = float('-inf')
        possible_actions = game_state.generate_possible_actions()
        scored_actions = [(action, evaluate_move(action.get_next_game_state(),edge_distance_matrix)) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1], reverse=True)#Descending
        s = 10
        for action in scored_actions:
            if(s==0):
                return max_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, False,transposition_table,edge_distance_matrix)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        transposition_table[state_hash] = max_eval
        return max_eval
    else:
        
        min_eval = float('inf')
        possible_actions = game_state.generate_possible_actions()

        scored_actions = [(action, evaluate_move(action.get_next_game_state(),edge_distance_matrix)) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1]) #Ascending
        s = 10
        for action in scored_actions:
            if(s==0):
                return min_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, True, transposition_table,edge_distance_matrix)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        transposition_table[state_hash] = min_eval
        return min_eval


def evaluate_move( game_state,edge_distance_matrix):
    # Ici, vous pouvez définir une heuristique rapide pour évaluer le mouvement
    # Par exemple:
    return evaluate_state(game_state,edge_distance_matrix)