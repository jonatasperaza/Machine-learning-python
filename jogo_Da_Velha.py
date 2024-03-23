import random
import json
import ast

class JogoDaVelha:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # Tabuleiro 3x3
        self.game_over = False
        self.winner = None

    def make_move(self, position, player):
        if self.board[position] == ' ' and not self.game_over:
            self.board[position] = player
            self.check_winner(player)
            return True
        return False

    def check_winner(self, player):
        winning_combinations = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                                (0, 3, 6), (1, 4, 7), (2, 5, 8),
                                (0, 4, 8), (2, 4, 6)]
        for combo in winning_combinations:
            if all(self.board[i] == player for i in combo):
                self.game_over = True
                self.winner = player

        if ' ' not in self.board:
            self.game_over = True  # Empate

    def reset(self):
        self.board = [' ' for _ in range(9)]
        self.game_over = False
        self.winner = None

    def get_state(self):
        return ''.join(self.board)

    def available_moves(self):
        return [i for i, x in enumerate(self.board) if x == ' ']

class QLearningPlayer:
    def __init__(self, player, epsilon=0.1, alpha=0.5, gamma=0.9):
        self.player = player
        self.Q = {}  # Tabela Q
        self.epsilon = epsilon  # Taxa de exploração
        self.alpha = alpha  # Taxa de aprendizado
        self.gamma = gamma  # Fator de desconto
        self.load_Q()

    def choose_action(self, available_moves, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_moves)  # Exploração
        qs = [self.Q.get((state, str(move)), 0) for move in available_moves]
        max_q = max(qs)
        if qs.count(max_q) > 1:
            best_moves = [available_moves[i] for i in range(len(available_moves)) if qs[i] == max_q]
            return random.choice(best_moves)
        return available_moves[qs.index(max_q)]

    def update_Q(self, state, next_state, action, reward):
        current_q = self.Q.get((state, action), 0)
        max_future_q = max([self.Q.get((next_state, a), 0) for a in range(9)])
        self.Q[(state, action)] = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)

    def save_Q(self):
        # Carrega os dados existentes do arquivo
        try:
            with open("qtable.json", "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        # Converte as chaves da tabela Q para strings
        str_keys_Q = {str(k): v for k, v in self.Q.items()}

        # Mescla os dados existentes com os novos dados
        combined_data = {**existing_data, **str_keys_Q}

        # Salva a tabela Q completa no arquivo
        with open("qtable.json", "w") as f:
            json.dump(combined_data, f)

    def load_Q(self):
        try:
            with open("qtable.json", "r") as f:
                data = f.read()
                if data:
                    Q_str_keys = json.loads(data)
                    self.Q = {ast.literal_eval(k): v for k, v in Q_str_keys.items()}
                else:
                    self.Q = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.Q = {}

def human_move(game):
    while True:
        try:
            move = int(input("Digite a posição para jogar (0-8): "))
            if move in game.available_moves():
                return move
            else:
                print("Posição inválida. Por favor, escolha uma posição válida.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número de 0 a 8.")

def play_game_with_human(ai_player):
    game = JogoDaVelha()
    current_player = 'X'
    while not game.game_over:
        if current_player == ai_player.player:
            action = ai_player.choose_action(game.available_moves(), game.get_state())
            print("IA joga:", action)
            game.make_move(action, ai_player.player)
        else:
            print("Tabuleiro atual:")
            print(game.board[0:3])
            print(game.board[3:6])
            print(game.board[6:9])
            action = human_move(game)
            game.make_move(action, 'O')
        current_player = 'O' if current_player == 'X' else 'X'
    print("Jogo acabou!")
    if game.winner:
        print("Vencedor:", game.winner)
    else:
        print("Empate!")

def play_game(ai_player, opponent):
    game = JogoDaVelha()
    current_player = ai_player.player
    
    while not game.game_over:
        state_before = game.get_state()
        if current_player == ai_player.player:
            action = ai_player.choose_action(game.available_moves(), state_before)
            game.make_move(action, ai_player.player)
            next_state = game.get_state()
            if game.game_over:
                if game.winner == ai_player.player:
                    reward = 1  # Vitória
                elif game.winner is None:
                    reward = 0.5  # Empate
                else:
                    reward = -1  # Derrota
                ai_player.update_Q(state_before, next_state, action, reward)
        else:
            action = random.choice(game.available_moves())
            game.make_move(action, opponent)
        
        current_player = ai_player.player if current_player != ai_player.player else opponent
    
    ai_player.save_Q()

# Exemplo de como treinar a IA
if __name__ == "__main__":
    ai = QLearningPlayer(player='X')
    for _ in range(1000):  # Número de jogos para treinamento
        play_game(ai, 'O')

    # Após o treinamento, você pode jogar contra a IA treinada
    play_game_with_human(ai)