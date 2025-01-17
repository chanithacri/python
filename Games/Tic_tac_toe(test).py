import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Input
from tensorflow.keras.optimizers import Adam

# Prepare the Tic-Tac-Toe board
# Board will be a 3x3 grid, encoded as a flat array of 9 elements
def preprocess_data():
    # Define all possible game states and outcomes
    X = np.random.randint(0, 3, size=(1000, 9))  # Random board states
    y = np.random.randint(0, 9, size=(1000,))  # Random moves corresponding to board states

    # Convert labels to categorical
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

# Play a game between human and AI
def play_game(model):
    def print_board(board):
        symbols = {0: " ", 1: "X", 2: "O"}
        for i in range(3):
            print(" | ".join(symbols[board[j]] for j in range(i * 3, (i + 1) * 3)))
            if i < 2:
                print("-" * 5)

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

    board = [0] * 9
    human_turn = True

    while True:
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
            input_data = np.array(board).reshape(1, -1)
            prediction = model.predict(input_data, verbose=0).flatten()
            possible_moves = [i for i in range(9) if board[i] == 0]
            ai_move = max(possible_moves, key=lambda x: prediction[x])
            board[ai_move] = 2
            human_turn = True

# Main function
def main():
    X, y = preprocess_data()
    model = build_model()
    model = train_model(model, X, y)
    evaluate_model(model, X, y)

    # Save the trained model
    model.save("tic_tac_toe_ai_v1.h5")

    # Allow human to play against AI
    play_game(model)

if __name__ == "__main__":
    main()
