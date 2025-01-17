import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import os

# Disable GPU and reduce TensorFlow logging
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def check_winner(board):
    # Check rows, columns and diagonals
    for i in range(3):
        if board[i] == board[i + 3] == board[i + 6] != 0:
            return board[i]
        if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] != 0:
            return board[i * 3]
    if board[0] == board[4] == board[8] != 0 or board[2] == board[4] == board[6] != 0:
        return board[4]
    if all(cell != 0 for cell in board):
        return -1  # Draw
    return 0  # Game continues

def build_model():
    model = Sequential([
        Dense(64, activation='relu', input_shape=(9,)),
        Dense(32, activation='relu'),
        Dense(9, activation='softmax')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001),
                 loss='categorical_crossentropy',
                 metrics=['accuracy'])
    return model

def self_train(model, num_games=1000):
    print(f"Starting self-training for {num_games} games...")
    
    states = []
    moves = []
    wins = {1: 0, 2: 0, -1: 0}
    
    for game in range(num_games):
        board = [0] * 9
        game_states = []
        game_moves = []
        current_player = 1
        
        while True:
            winner = check_winner(board)
            if winner != 0:
                break
                
            # Get model's prediction
            board_input = np.array(board).reshape(1, -1)
            prediction = model.predict(board_input, verbose=0)[0]
            
            # Find valid moves
            valid_moves = [i for i in range(9) if board[i] == 0]
            
            # Choose move (with exploration)
            if np.random.random() < 0.1:  # 10% random moves
                move = np.random.choice(valid_moves)
            else:
                # Filter predictions for only valid moves
                valid_predictions = [prediction[i] if i in valid_moves else -np.inf for i in range(9)]
                move = np.argmax(valid_predictions)
            
            # Store the move
            game_states.append(list(board))
            move_onehot = np.zeros(9)
            move_onehot[move] = 1
            game_moves.append(move_onehot)
            
            # Make the move
            board[move] = current_player
            current_player = 3 - current_player
        
        # Store winning moves
        wins[winner] = wins.get(winner, 0) + 1
        if winner > 0:  # Don't learn from draws
            player_states = game_states[::2] if winner == 1 else game_states[1::2]
            player_moves = game_moves[::2] if winner == 1 else game_moves[1::2]
            states.extend(player_states)
            moves.extend(player_moves)
        
        # Train in batches
        if len(states) >= 32:
            model.fit(np.array(states), np.array(moves),
                     batch_size=32, epochs=1, verbose=0)
            states = []
            moves = []
        
        if (game + 1) % 100 == 0:
            print(f"Completed {game + 1} games. Wins - Player 1: {wins[1]}, Player 2: {wins[2]}, Draws: {wins[-1]}")
    
    # Train on remaining data
    if states:
        model.fit(np.array(states), np.array(moves),
                 batch_size=32, epochs=1, verbose=0)
    
    print("\nSelf-training complete!")
    print(f"Final statistics - Player 1: {wins[1]}, Player 2: {wins[2]}, Draws: {wins[-1]}")
    return model

def play_game(model):
    while True:
        board = [0] * 9
        human_turn = True
        
        print("\nNew game starting!")
        print("Board positions are numbered 0-8, left to right, top to bottom:")
        print(" 0 | 1 | 2 ")
        print("---+---+---")
        print(" 3 | 4 | 5 ")
        print("---+---+---")
        print(" 6 | 7 | 8 \n")
        
        while True:
            # Print current board
            symbols = {0: " ", 1: "X", 2: "O"}
            print("\nCurrent board:")
            for i in range(3):
                print(f" {symbols[board[i*3]]} | {symbols[board[i*3+1]]} | {symbols[board[i*3+2]]} ")
                if i < 2:
                    print("---+---+---")
            print()
            
            # Check for winner
            winner = check_winner(board)
            if winner == 1:
                print("Human wins!")
                break
            elif winner == 2:
                print("AI wins!")
                break
            elif winner == -1:
                print("It's a draw!")
                break
            
            if human_turn:
                try:
                    move = int(input("Enter your move (0-8): "))
                    if 0 <= move < 9 and board[move] == 0:
                        board[move] = 1
                        human_turn = False
                    else:
                        print("Invalid move. Try again.")
                except ValueError:
                    print("Invalid input. Please enter a number between 0-8.")
            else:
                print("AI is making its move...")
                board_input = np.array(board).reshape(1, -1)
                prediction = model.predict(board_input, verbose=0)[0]
                valid_moves = [i for i in range(9) if board[i] == 0]
                valid_predictions = [prediction[i] if i in valid_moves else -np.inf for i in range(9)]
                move = np.argmax(valid_predictions)
                board[move] = 2
                human_turn = True
        
        if input("\nPlay again? (yes/no): ").lower().strip() != 'yes':
            break

def main():
    if os.path.exists("tic_tac_toe_ai_v1.h5"):
        try:
            model = load_model("tic_tac_toe_ai_v1.h5")
            print("Loaded existing model.")
        except:
            print("Error loading model. Creating new one...")
            model = build_model()
    else:
        print("Creating new model...")
        model = build_model()
    
    while True:
        print("\nSelect an option:")
        print("1. Play against AI")
        print("2. Train AI through self-play")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            play_game(model)
        elif choice == "2":
            try:
                num_games = int(input("Enter number of self-training games (recommended 1000+): "))
                model = self_train(model, num_games)
                model.save("tic_tac_toe_ai_v1.h5")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        elif choice == "3":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()