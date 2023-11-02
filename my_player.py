from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError



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
        for action in current_state.generate_possible_actions():
            if(s==0):
                return best_move
            
            move_value = minimax_alpha_beta(action.get_next_game_state(), depth, float('-inf'),float("inf"), True, self.transposition_table)
            #move_value =  minimax(action.get_next_game_state(), depth, True)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            s -= 1
        print(current_state.next_player)
        print(best_value)
        print(best_move)
        return best_move


def calculate_center(game_state: GameState):
    valid_points = [(i, j) for i, j in game_state.get_rep().get_env().keys() if game_state.in_hexa((i, j))]
    center_x = sum(x for x, _ in valid_points) / len(valid_points)
    center_y = sum(y for _, y in valid_points) / len(valid_points)
    return center_x, center_y


def evaluate_state(game_state: GameState) -> float:
    # Logic to evaluate the state
    # For simplicity, let's say the value is the difference in the number of pieces
    # between the player and the opponent.
    player = game_state.next_player
    score = 0
   
    

    current_rep = game_state.get_rep()
    b = current_rep.get_env()
    dim = current_rep.get_dimensions()
    
    # Define the center of the board
    center = (dim[0]//2, dim[1]//2)
    
    distance_factor = 0.1  # It needs to be low, under the loss of loosing a piece, otherwise it don't care about loosing a piece
    
    
    for i, j in list(b.keys()):
            
            p = b.get((i, j), None)
            distance = manhattanDist(center,[i,j])
            if p.get_owner_id() == player.get_id():

                #Favorise une formation en diag
                #score += sum(0.1 for k, l in b.keys() if k != i and j != l and (k == i or l == j))

                for k,l in list(b.keys()) :
                    if k!= i and j != l:
                        score += 0.5 if k == i else 0
                
                

                score -= distance_factor * distance  #Favorise un mvt qui rapproche les pieces vers le centre
                score +=1  #count the number of piece of the player
            else:
                score += distance * distance_factor #Favorise un mvt qui eloigne les pieces advairse du centre
                score -=1 #Decrease for every piece of the oponent

    

        
    # Calculate the score based on piece of each player
    # player_piece_count = sum(1 for piece in game_state.get_rep().get_env().values() 
    #                          if piece.get_owner_id() == player.get_id())
    # opponent_piece_count = sum(1 for piece in game_state.get_rep().get_env().values() 
    #                            if piece.get_owner_id() != player.get_id())
    
    # score += opponent_piece_count - player_piece_count 

    return  score

def manhattanDist(A, B):
            dist = abs(B[0] - A[0]) + abs(B[1] - A[1])
            return dist

def minimax(game_state: GameState, depth: int, maximizing_player: bool) -> float:


    if depth == 0 or game_state.is_done():
        
        return evaluate_state(game_state)
    
    
    if maximizing_player:
        max_eval = float('-inf')
        s = 10
        for action in game_state.generate_possible_actions() :
            if(s==0):
                return max_eval
            eval = minimax(action.get_next_game_state(), depth-1, False)
            max_eval = max(max_eval, eval)
        s += 1
        return max_eval
    
    else: # minimizing player
        min_eval = float('inf')
        s = 10
        for action in game_state.generate_possible_actions():
            if(s==0):
                return min_eval
            s -= 1
            eval = minimax(action.get_next_game_state(), depth-1, True)
            min_eval = min(min_eval, eval)
        return min_eval


def minimax_alpha_beta(game_state, depth, alpha, beta, maximizing_player,transposition_table):

    state_hash = hash(str(game_state.get_rep().get_env()))

    if state_hash in transposition_table:
        return transposition_table[state_hash]

    if depth == 0 or game_state.is_done():
        value =  evaluate_state(game_state)
        transposition_table[state_hash] = value
        return value

    if maximizing_player:
        
        max_eval = float('-inf')
        possible_actions = game_state.generate_possible_actions()
        scored_actions = [(action, evaluate_move(action.get_next_game_state())) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1], reverse=True)#Descending
        s = 10
        for action in scored_actions:
            if(s==0):
                return max_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, False,transposition_table)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        transposition_table[state_hash] = max_eval
        return max_eval
    else:
        
        min_eval = float('inf')
        possible_actions = game_state.generate_possible_actions()
        scored_actions = [(action, evaluate_move(action.get_next_game_state())) for action in possible_actions]
        scored_actions.sort(key=lambda x: x[1]) #Ascending
        s = 10
        for action in scored_actions:
            if(s==0):
                return min_eval
            s -= 1
            eval = minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, True, transposition_table)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        transposition_table[state_hash] = min_eval
        return min_eval


def evaluate_move( game_state):
    # Ici, vous pouvez définir une heuristique rapide pour évaluer le mouvement
    # Par exemple:
    return evaluate_state(game_state)