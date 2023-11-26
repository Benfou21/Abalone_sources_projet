from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from board_abalone import BoardAbalone



#Joueur qui va être loin du centre 
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
        depth = 1
        print(f"Nombre d'actions possibles: {len(current_state.generate_possible_actions())}")
        s = 5

        
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




def evaluate_state(game_state: GameState,plays) -> float:
    
    
    player = game_state.next_player
    score = 0


    current_rep = game_state.get_rep()
    b = current_rep.get_env()
    dim = current_rep.get_dimensions()
    
    
    center = (dim[0]//2, dim[1]//2)
    
    distance_factor = 0.5  
    dispersement_factor = 0.02  #if too high the player send the piece out of the board
    


    list_player = [ (i,j) for i,j in list(b.keys()) if b.get((i, j), None).get_owner_id() == player.get_id()]
    score += total_distance(list_player) *dispersement_factor

 
    for i, j in list(b.keys()):
            
            
            p = b.get((i, j), None)
            distance = manhattanDist(center,[i,j])
            
            if p.get_owner_id() == player.get_id():

                
                score += distance_factor * distance   
                score +=50  #count the number of piece of the player
                
            

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