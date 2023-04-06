from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap
import sys

class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.board_size = 8
        self.cell_size = 50
        
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = (i + j) % 2
                cell = Cell(color, self.cell_size, i, j)
                self.addItem(cell)

    # def place_pieces(self):
    #     # Place pawns
    #     for i in range(self.board_size):
    #         self.place_piece(Piece("white", "pawn", self.cell_size, i, 1))
    #         self.place_piece(Piece("black", "pawn", self.cell_size, i, 6))
            
    #     # Place rooks
    #     self.place_piece(Piece("white", "rook", self.cell_size, 0, 0))
    #     self.place_piece(Piece("white", "rook", self.cell_size, 7, 0))
    #     self.place_piece(Piece("black", "rook", self.cell_size, 0, 7))
    #     self.place_piece(Piece("black", "rook", self.cell_size, 7, 7))
        
    #     # Place knights
    #     self.place_piece(Piece("white", "knight", self.cell_size, 1, 0))
    #     self.place_piece(Piece("white", "knight", self.cell_size, 6, 0))
    #     self.place_piece(Piece("black", "knight", self.cell_size, 1, 7))
    #     self.place_piece(Piece("black", "knight", self.cell_size, 6, 7))
        
    #     # Place bishops
    #     self.place_piece(Piece("white", "bishop", self.cell_size, 2, 0))
    #     self.place_piece(Piece("white", "bishop", self.cell_size, 5, 0))
    #     self.place_piece(Piece("black", "bishop", self.cell_size, 2, 7))
    #     self.place_piece(Piece("black", "bishop", self.cell_size, 5, 7))
        
    #     # Place kings and queens
    #     self.place_piece(Piece("white", "king", self.cell_size, 4, 0))
    #     self.place_piece(Piece("white", "queen", self.cell_size, 3, 0))
    #     self.place_piece(Piece("black", "king", self.cell_size, 4, 7))
    #     self.place_piece(Piece("black", "queen", self.cell_size, 3, 7))
                
    # def place_piece(self, piece):
    #     self.addItem(piece)
    #     self.cells[piece.y][piece.x].occupied = True
    #     self.cells[piece.y][piece.x].piece = piece

    # def move_piece(self, piece, x, y):
    #     if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
    #         return False
        
    #     if not self.cells[y][x].occupied:
    #         self.cells[piece.y][piece.x].occupied = False
    #         self.cells[piece.y][piece.x].piece = None
            
    #         piece.x = x
    #         piece.y = y
    #         piece.setPos(x * self.cell_size, y * self.cell_size)
            
    #         self.cells[y][x].occupied = True
    #         self.cells[y][x].piece = piece
            
    #         return True
        
    #     return False

class Cell(QGraphicsPixmapItem):
    def __init__(self, color, size, x, y, parent=None):
        super().__init__(parent)
        
        self.color = color
        self.size = size
        self.x = x
        self.y = y
        
        if self.color == 0:
            self.setPixmap(QPixmap("black_cell.jpg"))
        else:
            self.setPixmap(QPixmap("white_cell.jpg"))
            
        self.setPos(x * self.size, y * self.size)
        
# class Piece(QGraphicsPixmapItem):
#     def __init__(self, color, piece_type, size, x, y, board):
#         super().__init__()
#         self.color = color
#         self.type = piece_type
#         self.size = size
#         self.x = x
#         self.y = y
#         self.board = board
#         self.occupied = True
#         self.setPixmap(QPixmap(f"{self.color}_{piece_type}.png").scaled(self.size, self.size))
#         self.setPos(x * size, y * size)

        
#     def moves(self):
#         if self.piece_type == "pawn":
#             return self.pawn_moves()
#         elif self.piece_type == "rook":
#             return self.rook_moves()
#         elif self.piece_type == "knight":
#             return self.knight_moves()
#         elif self.piece_type == "bishop":
#             return self.bishop_moves()
#         elif self.piece_type == "queen":
#             return self.rook_moves() + self.bishop_moves()
#         elif self.piece_type == "king":
#             return self.king_moves()
        
#     def pawn_moves(self):
#         moves = []
#         if self.color == "white":
#             if self.y > 0:
#                 if not self.board.cells[self.y-1][self.x].occupied:
#                     moves.append((self.x, self.y-1))
#                 if self.x > 0 and self.board.cells[self.y-1][self.x-1].occupied:
#                     moves.append((self.x-1, self.y-1))
#                 if self.x < self.board.self.board_size-1 and self.board.cells[self.y-1][self.x+1].occupied:
#                     moves.append((self.x+1, self.y-1))
#         else:
#             if self.y < self.board.self.board_size-1:
#                 if not self.board.cells[self.y+1][self.x].occupied:
#                     moves.append((self.x, self.y+1))
#                 if self.x > 0 and self.board.cells[self.y+1][self.x-1].occupied:
#                     moves.append((self.x-1, self.y+1))
#                 if self.x < self.board.self.board_size-1 and self.board.cells[self.y+1][self.x+1].occupied:
#                     moves.append((self.x+1, self.y+1))
#         return moves
    
#     def rook_moves(self):
#         moves = []
#         for i in range(self.x-1, -1, -1):
#             if self.board.cells[self.y][i].occupied:
#                 if self.board.cells[self.y][i].piece.color != self.color:
#                     moves.append((i, self.y))
#                 break
#             moves.append((i, self.y))
#         for i in range(self.x+1, self.board.self.board_size):
#             if self.board.cells[self.y][i].occupied:
#                 if self.board.cells[self.y][i].piece.color != self.color:
#                     moves.append((i, self.y))
#                 break
#             moves.append((i, self.y))
#         for i in range(self.y-1, -1, -1):
#             if self.board.cells[i][self.x].occupied:
#                 if self.board.cells[i][self.x].piece.color != self.color:
#                     moves.append((self.x, i))
#                 break
#             moves.append((self.x, i))
#         for i in range(self.y+1, self.board.self.board_size):
#             if self.board.cells[i][self.x].occupied:
#                 if self.board.cells[i][self.x].piece.color != self.color:
#                     moves.append((self.x, i))
#                 break
#             moves.append((self.x, i))
#         return moves
    
#     def knight_moves(x, y, board):
#         moves = []
#         offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
#         for dx, dy in offsets:
#             new_x, new_y = x + dx, y + dy
#             if 0 <= new_x < board.board_size and 0 <= new_y < board.board_size:
#                 if not board.cells[new_y][new_x].occupied or board.cells[new_y][new_x].piece.color != board.cells[y][x].piece.color:
#                     moves.append((new_x, new_y))
#         return moves

#     def bishop_moves(x, y, board):
#         moves = []
#         for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
#             new_x, new_y = x + dx, y + dy
#             while 0 <= new_x < board.board_size and 0 <= new_y < board.board_size:
#                 if not board.cells[new_y][new_x].occupied:
#                     moves.append((new_x, new_y))
#                 elif board.cells[new_y][new_x].piece.color != board.cells[y][x].piece.color:
#                     moves.append((new_x, new_y))
#                     break
#                 else:
#                     break
#                 new_x, new_y = new_x + dx, new_y + dy
#         return moves
    
#     def king_moves(self):
#         moves = []
#         for i in range(self.x-1, self.x+2):
#             if i < 0 or i >= self.board.board_size:
#                 continue
#             for j in range(self.y-1, self.y+2):
#                 if j < 0 or j >= self.board.board_size:
#                     continue
#                 if i == self.x and j == self.y:
#                     continue
#                 if not self.board.cells[j][i].occupied or self.board.cells[j][i].piece.color != self.color:
#                     moves.append((i, j))
#         return moves

# class ChessGame():
#     def __init__(self):
#         pass

# class Utilities():
#     def __init__(self):
#         pass

class Window(QMainWindow):
    def __init__(self, board):
        super().__init__()

        self.setWindowTitle("Szachy")
        self.setGeometry(100,100, 1000,1000)

        self.scene = board
        self.view = QGraphicsView(self.scene, self)
        self.view.geometry()
        self.view.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    view = QGraphicsView(window)
    board = Board()
    view.setScene(board)
    window.setCentralWidget(view)
    window.show()
    sys.exit(app.exec_())

        def pawn_moves(self):
        moves = []
        if self.color == "white":
            if self.y > 0:
                if not self.board.cells[self.y-1][self.x].occupied:
                    moves.append((self.x, self.y-1))
                if self.x > 0 and self.board.cells[self.y-1][self.x-1].occupied:
                    moves.append((self.x-1, self.y-1))
                if self.x < self.board.self.board_size-1 and self.board.cells[self.y-1][self.x+1].occupied:
                    moves.append((self.x+1, self.y-1))
        else:
            if self.y < self.board.self.board_size-1:
                if not self.board.cells[self.y+1][self.x].occupied:
                    moves.append((self.x, self.y+1))
                if self.x > 0 and self.board.cells[self.y+1][self.x-1].occupied:
                    moves.append((self.x-1, self.y+1))
                if self.x < self.board.self.board_size-1 and self.board.cells[self.y+1][self.x+1].occupied:
                    moves.append((self.x+1, self.y+1))
        return moves
    
    def rook_moves(self):
        moves = []
        for i in range(self.x-1, -1, -1):
            if self.board.cells[self.y][i].occupied:
                if self.board.cells[self.y][i].piece.color != self.color:
                    moves.append((i, self.y))
                break
            moves.append((i, self.y))
        for i in range(self.x+1, self.board.self.board_size):
            if self.board.cells[self.y][i].occupied:
                if self.board.cells[self.y][i].piece.color != self.color:
                    moves.append((i, self.y))
                break
            moves.append((i, self.y))
        for i in range(self.y-1, -1, -1):
            if self.board.cells[i][self.x].occupied:
                if self.board.cells[i][self.x].piece.color != self.color:
                    moves.append((self.x, i))
                break
            moves.append((self.x, i))
        for i in range(self.y+1, self.board.self.board_size):
            if self.board.cells[i][self.x].occupied:
                if self.board.cells[i][self.x].piece.color != self.color:
                    moves.append((self.x, i))
                break
            moves.append((self.x, i))
        return moves
    
    def knight_moves(x, y, board):
        moves = []
        offsets = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dx, dy in offsets:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < board.board_size and 0 <= new_y < board.board_size:
                if not board.cells[new_y][new_x].occupied or board.cells[new_y][new_x].piece.color != board.cells[y][x].piece.color:
                    moves.append((new_x, new_y))
        return moves

    def bishop_moves(x, y, board):
        moves = []
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < board.board_size and 0 <= new_y < board.board_size:
                if not board.cells[new_y][new_x].occupied:
                    moves.append((new_x, new_y))
                elif board.cells[new_y][new_x].piece.color != board.cells[y][x].piece.color:
                    moves.append((new_x, new_y))
                    break
                else:
                    break
                new_x, new_y = new_x + dx, new_y + dy
        return moves
    
    def king_moves(self):
        moves = []
        for i in range(self.x-1, self.x+2):
            if i < 0 or i >= self.board.board_size:
                continue
            for j in range(self.y-1, self.y+2):
                if j < 0 or j >= self.board.board_size:
                    continue
                if i == self.x and j == self.y:
                    continue
                if not self.board.cells[j][i].occupied or self.board.cells[j][i].piece.color != self.color:
                    moves.append((i, j))
        return moves