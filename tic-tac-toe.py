import random


class TicTacToe:
    def __init__(self):
        self.cells = [' ' for _ in range(9)]

    def print_board(self):
        print("---------")
        for i in range(0, 9, 3):
            print(f"| {self.cells[i]} {self.cells[i+1]} {self.cells[i+2]} |")
        print("---------")

    def make_move(self, mark, player):
        if player == "user":
            while True:
                coords = input("Enter the coordinates: ").split()
                if not all(coord.isdigit() for coord in coords):
                    print("You should enter numbers!")
                    continue
                row, col = map(int, coords)
                if not (1 <= row <= 3) or not (1 <= col <= 3):
                    print("Coordinates should be from 1 to 3!")
                    continue
                index = (row - 1) * 3 + (col - 1)
                if self.cells[index] != ' ':
                    print("This cell is occupied! Choose another one!")
                    continue
                self.cells[index] = mark
                break
        elif player == "easy":
            print(f'Making move level "{player}"')
            self.make_random_move(mark)
        elif player == "medium":
            print(f'Making move level "{player}"')
            if self.make_winning_move(mark):
                return
            if self.make_blocking_move(mark):
                return
            self.make_random_move(mark)
        elif player == "hard":
            print(f'Making move level "{player}"')
            _, best_move = self.minimax(mark, mark, True)
            self.cells[best_move] = mark

    def make_random_move(self, mark):
        available_cells = [i for i, cell in enumerate(self.cells) if cell == ' ']
        index = random.choice(available_cells)
        self.cells[index] = mark

    def make_winning_move(self, mark):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for condition in win_conditions:
            count = sum(self.cells[i] == mark for i in condition)
            empty_cell_index = [i for i in condition if self.cells[i] == ' ']
            if count == 2 and len(empty_cell_index) == 1:
                self.cells[empty_cell_index[0]] = mark
                return True
            return False

    def make_blocking_move(self, mark):
        opponent_mark = 'O' if mark == 'X' else 'X'
        return self.make_winning_move(opponent_mark)

    def minimax(self, player_mark, current_mark, is_maximizing):
        if self.check_winner(player_mark):
            return 1, None
        elif self.check_winner('O' if player_mark == 'X' else 'X'):
            return -1, None
        elif self.is_board_full():
            return 0, None

        best_score = float('-inf') if is_maximizing else float('inf')
        best_move = None

        for i in range(len(self.cells)):
            if self.cells[i] == ' ':
                self.cells[i] = current_mark
                score, _ = self.minimax(player_mark, 'O' if current_mark == 'X' else 'X', not is_maximizing)
                self.cells[i] = ' '

                if is_maximizing and score > best_score:
                    best_score = score
                    best_move = i
                elif not is_maximizing and score < best_score:
                    best_score = score
                    best_move = i

        return best_score, best_move

    def check_winner(self, mark):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for condition in win_conditions:
            if all(self.cells[i] == mark for i in condition):
                return True
            return False

    def is_board_full(self):
        return all(cell != ' ' for cell in self.cells)


class PlayGame(TicTacToe):
    def start_game(self):
        self.cells = [' ' for _ in range(9)]
        while True:
            command = input("Input command: ")
            if command == "exit":
                break
            elif command.startswith("start"):
                try:
                    _, player1, player2 = command.split()
                    if player1 not in ["user", "easy", "medium", "hard"] or player2 not in ["user", "easy", "medium", "hard"]:
                        print("Bad parameters!")
                        continue
                    self.play_game(player1, player2)
                except ValueError:
                    print("Bad parameters!")
                    continue
            else:
                print("Bad command!")
                continue

    def play_game(self, player1, player2):
        while True:
            self.print_board()
            self.make_move('X', player1)
            if self.check_winner('X'):
                self.print_board()
                print("X wins")
                break
            if self.is_board_full():
                self.print_board()
                print("Draw")
                break
            self.print_board()
            self.make_move('O', player2)
            if self.check_winner('O'):
                self.print_board()
                print("O wins")
                break
            if self.is_board_full():
                self.print_board()
                print("Draw")
                break


if __name__ == "__main__":
    game = PlayGame()
    game.start_game()
