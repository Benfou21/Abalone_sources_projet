from player_abalone import PlayerAbalone
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from seahorse.utils.custom_exceptions import MethodNotImplementedError
from board_abalone import BoardAbalone
import time

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
        self.plays_count = 0
        self.nb_action = 20
        self.center = (0,0)
        self.deph = 3
        self.list_edge= [(0, 0),(0, 1), (0, 7), (0, 8), (1, 0), (1, 7), (1, 8), (2, 0), (2, 8), (3, 8), (5, 8), (6, 0), (6, 8), (7, 0), (7, 7), (7, 8), (8, 0), (8, 1), (8, 7), (8, 8)] 
        self.timing_max = 45
        
        
        
        


    def compute_action(self, current_state: GameState, **kwargs) -> Action:

        """
        Function to implement the logic of the player.

        Args:
            current_state (GameState): Current game state representation
            **kwargs: Additional keyword arguments

        Returns:
            Action: selected feasible action
        """

        start_time = time.time()
        
        print("plays" + str(self.plays_count))
        best_move = None
        best_value = float('-inf')
        
        print(f"Nombre d'actions possibles: {len(current_state.generate_possible_actions())}")
        
        #Depth
        d = self.deph

        current_rep = current_state.get_rep()
        dim = current_rep.get_dimensions()
        self.center =(dim[0]//2, dim[1]//2)
        
        
        possible_actions = current_state.generate_possible_actions()
        

        selected_actions = self.select_move(current_state, possible_actions)

        

        if( self.plays_count < 6): #Jusqu'à 5 coûts on souhaite des coûts qui dépasse un mvt d'une pièce 
            #Plus petite profondeur pour les premiers coups
            d = 1
            selected_actions = self.select_move_on_moves(current_state, selected_actions)
            
        print(f"Nombre d'actions selectionnées: {len(selected_actions)}")

        # scored_actions = [(action, self.evaluate_move(action.get_next_game_state(),edge_distance_matrix,0)) for action in selected_actions]
        # scored_actions.sort(key=lambda x: x[1], reverse=True)#Descending
        
        s = self.nb_action
        for action in selected_actions:

            if time.time() - start_time > 42:  #On laisse un temps max de 42sec par coup    : [ 15*60 temps max / 20 coups ] (25 - 5 coups de départ)
                print("Time exceed")
                return best_move
            
            depth = d
            if(s==0):
                self.plays_count += 1
                return best_move
            s -= 1

            #Si la situation est avantageuse augmenter la profondeur de 2   // Penser plus loin 
                
            if (self.is_strategic_move(action.get_next_game_state()) ):
                print("---------AUGMENTED-------------")
                depth += 1
            
            move_value = self.minimax_alpha_beta(action.get_next_game_state(), depth, float('-inf'),float("inf"), True, self.transposition_table,self.plays_count)
            #move_value =  minimax(action.get_next_game_state(), depth, True)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            

        print(best_move)
        print("return")
        self.plays_count += 1
        return best_move






    def total_distance(self,positions):
        total_dist = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                total_dist += self.manhattanDist(positions[i], positions[j])
        return total_dist
    
    def total_distance_center(self,positions):
        total_dist = 0
        for i in range(len(positions)):    
            total_dist += self.manhattanDist(positions[i], self.center)
        return total_dist

    def distance_to_closest_edge(self,position, edges):
        """Calculate the minimum Manhattan distance from a position to any edge."""
        return min(abs(position[0] - edge[0]) + abs(position[1] - edge[1]) for edge in edges)


    def get_adjacent_positions(self, position):
        i, j = position
        # Les directions changent en fonction de la ligne sur laquelle vous vous trouvez
        if i % 2 == 0:  # Ajustez en fonction de votre représentation du plateau
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
        else:
            directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        return [(i + di, j + dj) for di, dj in directions]

    # Fonction pour compter les pièces ennemies adjacentes
    def count_adjacent_enemies(self,position, board, player_id):
        adjacent_positions = self.get_adjacent_positions(position)
        count = 0
        for adj_position in adjacent_positions:
            if adj_position in board:
                p = board[adj_position]
                if p is not None and p.get_owner_id() != player_id:
                    count += 1
        return count

    # Fonction pour compter les pièces ennemies adjacentes sachant que les pieces sont en formation
    def count_adjacent_enemies_in_formation(self,position, board, player_id):
        adjacent_positions = self.get_adjacent_positions(position)
        count = 0
        for adj_position in adjacent_positions:
            if adj_position in board:
                p = board[adj_position]
                if p is not None and p.get_owner_id() != player_id and self.is_in_formation(position, board, player_id):
                    count += 1
        return count
    
    def count_adjacent_enemies_near_edge(self,position, board, player_id):
        adjacent_positions = self.get_adjacent_positions(position)
        count = 0
        for adj_position in adjacent_positions:
            if adj_position in board:
                p = board[adj_position]
                if p is not None and p.get_owner_id() != player_id:
                    e_adjacent_positions = self.get_adjacent_positions(adj_position)
                    
                    if any(elem in self.list_edge for elem in e_adjacent_positions): #Si un des voisins est le bord
                        print("YESS")
                        count += 1
        return count


   
    def is_in_formation(self,position, board, player_id):
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
                    if self.is_in_line(position, pos, board, player_id):
                        return True

        return False


    def is_in_line(self,pos1, pos2, board, player_id): #for two position 
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
    

    def is_strategic_move(self,game_state: GameState):

        current_rep = game_state.get_rep()
        b = current_rep.get_env()

        for i, j in list(b.keys()):
 
                p = b.get((i, j), None)
              
                if p.get_owner_id() == self.get_id():

                    if(self.count_adjacent_enemies_near_edge((i, j), b, self.get_id()) > 0) :
                        return True

        return False




   
    def evaluate_state(self,game_state: GameState,plays) -> float:
        # Logic to evaluate the state
        
        
        score = 0


        current_rep = game_state.get_rep()
        b = current_rep.get_env()
        dim = current_rep.get_dimensions()
        
        
        center = (dim[0]//2, dim[1]//2)
        
        
        distance_factor = 0.5  
        distance_factor_e = 2
        enemies_factor = 2
        dispersement_factor = 0.02  #if too high the player send the piece out of the board
        dispersement_factor_e = 0.1

        #Amélioation : distance_factor diminue au fur et à mesure de la game
        distance_factor -= plays *0.02
        if(distance_factor < 0) : distance_factor = 0.1
        #distance_factor_e augmante pour rendre le joueur plus aggresif 
        distance_factor_e += plays *0.04
        

        #Favorise une formation groupée, diminiue au cours de la game 
        dispersement_factor -= plays *0.001
        if(dispersement_factor < 0) : dispersement_factor = 0.005
        list_player = [ (i,j) for i,j in list(b.keys()) if b.get((i, j), None).get_owner_id() == self.get_id()]
        score -= self.total_distance(list_player) *dispersement_factor

    

        #Favorise un dispersement de l'ennemi
        list_not_player = [ (i,j) for i,j in list(b.keys()) if b.get((i, j), None).get_owner_id() != self.get_id()]
        score += self.total_distance(list_not_player) *dispersement_factor_e
        
        
        for i, j in list(b.keys()):
                
                
                p = b.get((i, j), None)
                distance = self.manhattanDist(center,[i,j])
                
                if p.get_owner_id() == self.get_id():

                    #Favorise un rapprochement vers l'ennemie
                    adjacent_enemies = self.count_adjacent_enemies_in_formation((i, j), b, self.get_id())
                    score += adjacent_enemies* enemies_factor

                    #Favorise une formation en diag
                    for k,l in list(b.keys()) :
                        if k!= i and j != l:
                            score += 1 if l == j else 0

                
                    score -= distance_factor * distance   #Favorise un mvt qui rapproche les pieces vers le centre,  V1 
                    score +=50  #count the number of piece of the player
                else:

                    
                    score += distance * distance_factor_e   #Favorise un mvt qui eloigne les pieces advairse du centre

                    score -=50 #Decrease for every piece of the oponent

        return  score

    def manhattanDist(self,A, B):
                dist = abs(B[0] - A[0]) + abs(B[1] - A[1])
                return dist


    def minimax_alpha_beta(self,game_state, depth, alpha, beta, maximizing_player,transposition_table,plays):

        state_hash = hash(str(game_state.get_rep().get_env()))

        if state_hash in transposition_table:
            return transposition_table[state_hash]

        if depth == 0 or game_state.is_done():
            value =  self.evaluate_state(game_state,plays)
            transposition_table[state_hash] = value
            return value

        if maximizing_player:
            
            max_eval = float('-inf')
            possible_actions = game_state.generate_possible_actions()
            #print(len(possible_actions))
            selected_actions = self.select_move(game_state, possible_actions)
            
        
            scored_actions = [(action, self.evaluate_move(action.get_next_game_state(),plays)) for action in selected_actions]
            scored_actions.sort(key=lambda x: x[1], reverse=True)#Descending
        
            s = self.nb_action
            for action in scored_actions:
                if(s==0):
                    return max_eval
                s -= 1

                


                eval = self.minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, False,transposition_table,plays)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cut-off
            transposition_table[state_hash] = max_eval
            return max_eval
        else:
            
            min_eval = float('inf')
            possible_actions = game_state.generate_possible_actions()
        
            selected_actions = self.select_move(game_state, possible_actions)
            
            scored_actions = [(action, self.evaluate_move(action.get_next_game_state(),plays)) for action in possible_actions]
            scored_actions.sort(key=lambda x: x[1]) #Ascending

            s = self.nb_action
            for action in scored_actions:
                if(s==0):
                    return min_eval
                s -= 1

                

                eval = self.minimax_alpha_beta(action[0].get_next_game_state(), depth-1, alpha, beta, True, transposition_table,plays)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cut-off
            transposition_table[state_hash] = min_eval
            return min_eval


    #Compte le nombre de piece du joueur 
    def count_piece(self,game_state):
        
        
        current_rep = game_state.get_rep()
        b = current_rep.get_env()
        new_count = 0

        for i, j in list(b.keys()):
            p = b.get((i, j), None)
                
            if p.get_owner_id() == self.get_id():
                new_count +=1
    
        return new_count

    def nb_pieces_moved(self,game_state1, game_state2):
        board1 = game_state1.get_rep().get_env()
        board2 = game_state2.get_rep().get_env()

        moved_pieces_count = 0

        for i in range(9):

            for j in range(9):
                p = board1.get((i, j))
                pstr = str(p)
                p2 = board2.get((i,j))
                p2str = str(p2)

                # Vérifier si la pièce à cette position est différente dans le deuxième état
                if pstr[49:-1] != p2str[49:-1]:
                    
                    moved_pieces_count += 1
        
        return moved_pieces_count
    
   
  

    #Fonctionn de selection des actions valides 
    #On supprime les mouvements qui jettent une piece
    def select_move(self,game_state, actions):
        
        #count=count_piece(game_state)
        count = game_state.get_player_score(self)
        
        selected = []
        for action in actions :

            new_game_state = action.get_next_game_state()
            #new_count= count_piece(new_game_state)
            new_count = new_game_state.get_player_score(self)
            
            
            if count == new_count :
                selected.append(action)

        return selected  

    def select_move_on_moves(self,game_state, actions):
        
        selected = []
        for action in actions :

            new_game_state = action.get_next_game_state()
            
            nb_pieces_moved = self.nb_pieces_moved(game_state,new_game_state)
            
            if  nb_pieces_moved > 2 :

                selected.append(action)
                

        return selected  
            

            




    def evaluate_move(self,game_state,plays):
        # Ici, vous pouvez définir une heuristique rapide pour évaluer le mouvement
        # Par exemple:
        return self.evaluate_state(game_state,plays)