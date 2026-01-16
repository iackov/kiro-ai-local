"""
Tic-Tac-Toe Game - Created to understand AI decision-making
"""
import random

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'
    
    def print_board(self):
        print(f"\n {self.board[0]} | {self.board[1]} | {self.board[2]} ")
        print("---|---|---")
        print(f" {self.board[3]} | {self.board[4]} | {self.board[5]} ")
        print("---|---|---")
        print(f" {self.board[6]} | {self.board[7]} | {self.board[8]} \n")
    
    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']
    
    def make_move(self, position, player):
        if self.board[position] == ' ':
            self.board[position] = player
            return True
        return False
    
    def check_winner(self):
        # Check rows, columns, diagonals
        wins = [
            [0,1,2], [3,4,5], [6,7,8],  # rows
            [0,3,6], [1,4,7], [2,5,8],  # columns
            [0,4,8], [2,4,6]             # diagonals
        ]
        for combo in wins:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return self.board[combo[0]]
        return None
    
    def is_full(self):
        return ' ' not in self.board
    
    def ai_move(self):
        """Simple AI: Try to win, block opponent, or random"""
        # Try to win
        for move in self.available_moves():
            self.board[move] = 'O'
            if self.check_winner() == 'O':
                return move
            self.board[move] = ' '
        
        # Try to block
        for move in self.available_moves():
            self.board[move] = 'X'
            if self.check_winner() == 'X':
                self.board[move] = 'O'
                return move
            self.board[move] = ' '
        
        # Take center if available
        if 4 in self.available_moves():
            self.board[4] = 'O'
            return 4
        
        # Random move
        move = random.choice(self.available_moves())
        self.board[move] = 'O'
        return move

def play_game():
    game = TicTacToe()
    print("Tic-Tac-Toe: AI vs AI")
    
    moves = 0
    while True:
        game.print_board()
        
        if game.current_player == 'X':
            # AI X makes random move
            move = random.choice(game.available_moves())
            game.make_move(move, 'X')
            print(f"AI X plays position {move}")
        else:
            # AI O makes smart move
            move = game.ai_move()
            print(f"AI O plays position {move}")
        
        moves += 1
        
        winner = game.check_winner()
        if winner:
            game.print_board()
            print(f"Winner: {winner}!")
            return winner, moves
        
        if game.is_full():
            game.print_board()
            print("Draw!")
            return 'Draw', moves
        
        game.current_player = 'O' if game.current_player == 'X' else 'X'

if __name__ == "__main__":
    print("Playing 3 games...\n")
    results = {'X': 0, 'O': 0, 'Draw': 0}
    total_moves = 0
    
    for i in range(3):
        print(f"\n=== Game {i+1} ===")
        winner, moves = play_game()
        results[winner] += 1
        total_moves += moves
    
    print("\n=== Results ===")
    print(f"X wins: {results['X']}")
    print(f"O wins: {results['O']}")
    print(f"Draws: {results['Draw']}")
    print(f"Average moves: {total_moves/3:.1f}")
