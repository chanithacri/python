import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten, Input
from tensorflow.keras.optimizers import Adam
import os

# Prepare the Tic-Tac-Toe board
# Generate realistic training data by simulating valid games
def preprocess_data():
    X, y = [], []

    def generate_game():
        board = [0] * 9
        current_player = 1
        moves = []

        for _ in range(9):
            empty_positions = [i for i in range(9) if board[i] == 0]
            if not empty_positions:
                break

            move = np.random.choice(empty_positions)
            board[move] = current_player
            moves.append((board[:], move))

            winner = check_winner(board)
            if winner != 0:
                break

            current_player = 3 - current_player

        if check_winner(board) == 1:
            for b, m in moves:
                X.append(b)
                y.append(m)

    def check_winner(board):
        for i in range(3):
            if board[i] == board[i + 3] == board[i + 6] != 0:
                return board[i]
            if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] != 0:
                return board[i * 3]
        if board[0] == board[4] == board[8] != 0 or board[2] == board[4] == board[6] != 0:
            return board[4]
        return 0

    for _ in range(5000):
        generate_game()

    X = np.array(X)
    y = tf.keras.utils.to_categorical(y, num_classes=9)
    return X, y

# Build the model
def build_model():
    model = Sequential([
        Input(shape=(9,)),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(9, activation='softmax')  # 9 outputs corresponding to board positions
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])
    return model

# Train the model
def train_model(model, X, y):
    model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2, callbacks=[tf.keras.callbacks.EarlyStopping(patience=5)])
    return model

# Evaluate the model
def evaluate_model(model, X, y):
    results = model.evaluate(X, y)
    print(f"Test Results: {dict(zip(model.metrics_names, results))}")

# Save game data for self-training
def save_training_data(board, move):
    if not os.path.exists("training_data.npz"):
        X, y = [], []
    else:
        data = np.load("training_data.npz")
        X, y = data['X'].tolist(), data['y'].tolist()

    X.append(board)
    y.append(move)
    np.savez("training_data.npz", X=np.array(X), y=np.array(y))

# Self-train the model
def self_train_model(model, epochs=10):
    if os.path.exists("training_data.npz"):
        data = np.load("training_data.npz")
        X, y = data['X'], tf.keras.utils.to_categorical(data['y'], num_classes=9)
        print("Starting self-training...")
        model.fit(X, y, epochs=epochs, batch_size=32, validation_split=0.2, verbose=1)
        model.save("tic_tac_toe_ai_v2.h5")

# Select training mode
def training_mode():
    print("Select Training Mode:")
    print("1. Preprocessed Data Training")
    print("2. Self-Training with Saved Data")
    print("3. Combined Training")
    choice = input("Enter your choice (1/2/3): ").strip()

    return choice

# Play a game between human and AI
def play_game(model):
    def print_board(board):
        symbols = {0: " ", 1: "X", 2: "O"}
        for i in range(3):
            print(f" {symbols[board[i * 3]]} | {symbols[board[i * 3 + 1]]} | {symbols[board[i * 3 + 2]]} ")
            if i < 2:
                print("---+---+---")

    def check_winner(board):
        for i in range(3):
            if board[i] == board[i + 3] == board[i + 6] != 0:
                return board[i]
            if board[i * 3] == board[i * 3 + 1] == board[i * 3 + 2] != 0:
                return board[i * 3]
        if board[0] == board[4] == board[8] != 0 or board[2] == board[4] == board[6] != 0:
            return board[4]
        if all(cell != 0 for cell in board):
            return -1  # Draw
        return 0  # No winner yet

    while True:
        board = [0] * 9
        human_turn = True

        while True:
            if not human_turn:
                input_data = np.array(board).reshape(1, -1)
                prediction = model.predict(input_data, verbose=0).flatten()
                possible_moves = [i for i in range(9) if board[i] == 0]
                if possible_moves:
                    ai_move = max(possible_moves, key=lambda x: prediction[x])
                    board[ai_move] = 2
                    save_training_data(board[:], ai_move)  # Save the move for training
                else:
                    print_board(board)
                    print("No moves left! It's a draw!")
                    break

            print_board(board)
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
                    print("Invalid input. Please enter a number between 0 and 8.")
            else:
                human_turn = True

        replay = input("Do you want to play again? (yes/no): ").strip().lower()
        if replay != "yes":
            print("Exiting game. Thanks for playing!")
            break

# Main function
def main():
    if os.path.exists("tic_tac_toe_ai_v1.h5"):
        model = load_model("tic_tac_toe_ai_v1.h5")
    else:
        X, y = preprocess_data()
        model = build_model()
        model = train_model(model, X, y)
        model.save("tic_tac_toe_ai_v1.h5")

    choice = training_mode()

    if choice == "1":
        X, y = preprocess_data()
        model = train_model(model, X, y)
    elif choice == "2":
        self_train_model(model, epochs=20)
    elif choice == "3":
        X, y = preprocess_data()
        model = train_model(model, X, y)
        self_train_model(model, epochs=10)
    else:
        print("Invalid choice. Proceeding with current model.")

    # Allow human to play against AI
    play_game(model)

if __name__ == "__main__":
    main()
    