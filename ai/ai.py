# Import libraries
import chess
import chess.pgn
import numpy as np
from tensorflow import keras
from keras.api._v2.keras import layers
import glob

pgn_files = glob.glob("*.pgn")

games = []
for file in pgn_files:
    print(f"Currently reading: {file}")
    with open(file) as pgn:
        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            games.append(game)

def encode_board(board):
    encoding = np.zeros((12, 8, 8), dtype=np.int8)
    pieces = board.piece_map()
    for i in range(64):
        if i in pieces:
            piece = pieces[i]
            row = i // 8
            col = i % 8
            plane = piece.piece_type - 1 + (piece.color == chess.BLACK) * 6
            encoding[plane, row, col] = 1
    return encoding

def encode_move(move):
    encoding = np.zeros((3, 8, 8), dtype=np.int8)
    from_row = move.from_square // 8
    from_col = move.from_square % 8
    to_row = move.to_square // 8
    to_col = move.to_square % 8
    encoding[0, from_row, from_col] = 1
    encoding[1, to_row, to_col] = 1
    if move.promotion:
        encoding[2, to_row, to_col] = move.promotion
    return encoding

def decode_move(encoding):
    from_square = np.argmax(encoding[0])
    to_square = np.argmax(encoding[1])
    promotion = None
    if np.any(encoding[2]):
        promotion = np.argmax(encoding[2])
    return chess.Move(from_square, to_square, promotion=promotion)

X = []
y = []

for game in games:
    board = game.board()
    for move in game.mainline_moves():
        X.append(encode_board(board))
        y.append(encode_move(move))
        board.push(move)
X = np.array(X)
y = np.array(y)

import matplotlib.pyplot as plt

# Define neural network model using Keras functional API
inputs = keras.Input(shape=(12, 8, 8))
x = layers.Conv2D(64,kernel_size=2)(inputs)
x = layers.Conv2D(64,kernel_size=3)(x)
x = layers.Flatten()(x)
x = layers.Dense(512, activation="relu")(x)
x = layers.Dense(512, activation="relu")(x)
x = layers.Dense(256, activation="relu")(x)
outputs = layers.Dense(192)(x)
outputs = layers.Reshape((3, 8, 8))(outputs)

model = keras.Model(inputs=inputs, outputs=outputs)

model.compile(loss="mse", optimizer="adam")

losses = []
batches = []

def update_plot(loss, batch):
    losses.append(loss)
    batches.append(batch)
    plt.plot(batches, losses)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Loss/Epoch")
    plt.pause(0.05)

for epoch in range(5):
    history = model.fit(X, y, epochs=1, batch_size=256)
    loss = history.history["loss"][0]
    update_plot(loss, epoch)

plt.show()

model.save("model_finished.h5")