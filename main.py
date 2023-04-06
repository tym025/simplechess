from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QApplication, QMainWindow, QGraphicsTextItem, QGraphicsRectItem, QLineEdit
from PyQt5.QtGui import QPixmap, QImage, QTransform, QColor
import sys

class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.board_size = 8
        self.cell_size = 50
        self.piecesOnBoard = []
        self.squares = [[-1 for j in range(self.board_size)] for i in range(self.board_size)]
        self.selectedPiece = 0
        self.moveRects = []

        # Create a QLineEdit widget and add it to the scene
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter chess notation...")
        self.addWidget(self.input)
        
        # Connect a function to the textChanged signal of the QLineEdit
        self.input.textChanged.connect(self.handle_input)

    def handle_input(self, text):
        # Do something with the input text here, such as parse it and update the board accordingly
        print("Input changed:", text)

        # Add cells to the board
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = (i + j + 1) % 2
                cell = Cell(color, self.cell_size, i, j)
                self.addItem(cell)
                
        # Add numbers to the top and bottom rows
        letters = "ABCDEFGH"
        for i in range(self.board_size):
            text_item_top = QGraphicsTextItem(letters[i])
            text_item_top.setPos(i*self.cell_size + self.cell_size/2 - text_item_top.boundingRect().width()/2, -self.cell_size/2 - text_item_top.boundingRect().height()/2)
            self.addItem(text_item_top)
            
            text_item_bottom = QGraphicsTextItem(letters[i])
            text_item_bottom.setPos(i*self.cell_size + self.cell_size/2 - text_item_bottom.boundingRect().width()/2, self.board_size*self.cell_size + self.cell_size/2 - text_item_bottom.boundingRect().height()/2)
            self.addItem(text_item_bottom)
        
        # Add numbers to the left and right columns
        for i in range(self.board_size):
            text_item_left = QGraphicsTextItem(str(self.board_size-i))
            text_item_left.setPos(-self.cell_size/2 - text_item_left.boundingRect().width()/2, i*self.cell_size + self.cell_size/2 - text_item_left.boundingRect().height()/2)
            self.addItem(text_item_left)
            
            text_item_right = QGraphicsTextItem(str(self.board_size-i))
            text_item_right.setPos(self.board_size*self.cell_size + self.cell_size/2 - text_item_right.boundingRect().width()/2, i*self.cell_size + self.cell_size/2 - text_item_right.boundingRect().height()/2)
            self.addItem(text_item_right)

        self.setup_pieces()

    def get_pieces(self):
        image = QImage('pieces2.png')
        pieces = []
        for i in range(0, 600, 50):
            piece = QPixmap.fromImage(image.copy(i, 0, 50, 100))
            pieces.append(piece)
        print(len(pieces))
        return pieces
    
    def setup_pieces(self):
        pieces = self.get_pieces()

        id = 0

        for i in range(self.board_size):
            self.piecesOnBoard.append(Piece("white", "pawn", self.cell_size, i, 1, self, self.squares, id))
            id += 1
            self.piecesOnBoard.append(Piece("black", "pawn", self.cell_size, i, 6, self, self.squares, id))
            id+=1
        self.piecesOnBoard.append(Piece("white", "rook", self.cell_size, 0, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "rook", self.cell_size, 7, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "rook", self.cell_size, 0, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "rook", self.cell_size, 7, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "knight", self.cell_size, 1, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "knight", self.cell_size, 6, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "knight", self.cell_size, 1, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "knight", self.cell_size, 6, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "bishop", self.cell_size, 2, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "bishop", self.cell_size, 5, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "bishop", self.cell_size, 2, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "bishop", self.cell_size, 5, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "queen", self.cell_size, 3, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "queen", self.cell_size, 3, 7, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("white", "king", self.cell_size, 4, 0, self, self.squares, id))
        id += 1
        self.piecesOnBoard.append(Piece("black", "king", self.cell_size, 4, 7, self, self.squares, id))
        
        for piece in self.piecesOnBoard:
            index = 0 if piece.color == "white" else 11
            ratio = 1 if piece.color == "white" else -1
            if(piece.type == "knight"): index+=ratio*1
            elif(piece.type == "rook"): index+=ratio*2
            elif(piece.type == "bishop"): index+=ratio*3
            elif(piece.type == "queen"): index+=ratio*4
            elif(piece.type == "king"): index+=ratio*5
            
            piece.setPixmap((pieces[index]))
            self.addItem(piece)

    def getPieceAt(self, x: int, y: int):
        for piece in self.piecesOnBoard:
            if piece.x == x and piece.y == y:
                return piece
        return None
    
    def getPieceById(self, id):
        for piece in self.piecesOnBoard:
            if piece.id == id:
                return piece
        return None

    def isInBoard(self, x, y):
        if(x >= 0 and x <= 7 and y >= 0 and y <= 7): return True
        return False
    
    def isEnemy(self, color, x, y):
        piece = self.getPieceAt(x, y)
        return piece is not None and piece.color != color


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Get the position of the mouse click
        pos = event.scenePos()
        # Calculate the row and column of the clicked cell
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)
        # Get the item at the clicked position
        if(self.isInBoard(col, row)):
            if(self.squares[col][row] > -1):
                self.selectedPiece = self.squares[col][row] 
                self.displayPossibleMoves(self.selectedPiece)

    def mouseReleaseEvent(self, event):
        pos = event.scenePos()
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)
        # Get the item at the clicked position
        if(self.isInBoard(col, row)):
            piece = self.getPieceById(self.selectedPiece)
            print(piece)
            if(self.selectedPiece > -1): piece.movePiece(col, row)
            self.selectedPiece = -1
            self.clearMoves()

    def isEmpty(self, x, y):
        return self.squares[x][y] == -1

    def displayPossibleMoves(self, selectedPiece):
        piece = self.getPieceById(selectedPiece)
        moves = piece.moves()

        for move in moves:
            # Create a new QGraphicsRectItem at the position of the move
            rect = QGraphicsRectItem(move[0] * piece.size,
                                    move[1] * piece.size,
                                    piece.size,
                                    piece.size)

            # Set the color and transparency of the rect
            rect.setBrush(QColor(255, 0, 0, 100))

            # Add the rect to the scene
            self.moveRects.append(rect)
            self.addItem(rect)

    def clearMoves(self):
        for rect in self.moveRects:
            self.removeItem(rect)
        self.moveRects = []

    def removePiece(self, piece_id):
        # Get the piece object with the given ID
        piece = self.getPieceById(piece_id)

        # Remove the piece from the board
        self.squares[piece.x][piece.y] = None

        # Remove the piece from the scene
        self.removeItem(piece)

        # Remove the piece from the list of pieces
        self.piecesOnBoard.remove(piece)

    def moveByChessNotation(self, notation):
        # Check if notation is valid (e.g. "e2-e4" or "e4xf5")
        if len(notation) < 5 or len(notation) > 6:
            print("Invalid notation!")
            return

        # Get starting and ending coordinates from notation
        start = (ord(notation[0]) - 97, int(notation[1]) - 1)
        end = (ord(notation[3]) - 97, int(notation[4]) - 1)

        # Check if starting and ending squares are in the board
        if not self.isInBoard(start[0], start[1]) or not self.isInBoard(end[0], end[1]):
            print("Invalid move!")
            return

        # Get the piece on the starting square
        piece = self.getPieceAt(start[0], start[1])

        # Check if there is a piece on the starting square
        if not piece:
            print("Invalid move!")
            return

        # Check if the piece can move to the ending square
        if end not in piece.moves():
            print("Invalid move!")
            return

        # Check if there is a piece on the ending square
        captured_piece = self.getPieceAt(end[0], end[1])

        # Move the piece to the ending square
        piece.movePiece(end[0], end[1])

        # Remove captured piece from the board
        if captured_piece:
            self.removePiece(captured_piece)

        # Print the move
        if len(notation) == 5:
            print(piece.color.capitalize(), piece.type.capitalize(), "moves to", notation[3:])
        else:
            print(piece.color.capitalize(), piece.type.capitalize(), "takes", captured_piece.color.capitalize(), captured_piece.type.capitalize(), "on", notation[3:])

class Cell(QGraphicsPixmapItem):
    def __init__(self, color, size, x, y, parent=None):
        super().__init__(parent)
        
        self.color = color
        self.size = size
        self.x = x
        self.y = y
        self.occupied = -1
        
        if self.color == 0:
            self.setPixmap(QPixmap("black_cell.png"))
        else:
            self.setPixmap(QPixmap("white_cell.png"))
            
        self.setPos(x * self.size, y * self.size)

    
class Piece(QGraphicsPixmapItem):
    def __init__(self, color, piece_type, size, x, y, board, squares, id):
        super().__init__()
        self.color = color
        self.type = piece_type
        self.size = size
        self.x = x
        self.y = y
        self.board = board
        self.startPosition = True
        self.setPos(x * size, y * size )
        self.id = id
        self.squares = squares
        self.squares[self.x][self.y] = self.id

    def movePiece(self, newX, newY):
        if self.board.isInBoard(newX, newY) and self.isInMoves(newX, newY):
            destPiece = self.board.getPieceAt(newX, newY)
            if destPiece:
                # Remove the destination piece from the board and from the scene
                self.board.removePiece(destPiece.id)
                self.board.removeItem(destPiece)

            self.squares[self.x][self.y] = -1
            self.x = newX
            self.y = newY
            self.squares[self.x][self.y] = self.id
            self.setPos(self.x * self.size, self.y * self.size)
            self.startPosition = False

    def moves(self):
        if self.type == "pawn":
            return self.pawn_moves()
        elif self.type == "rook":
            return self.rook_moves()
        elif self.type == "knight":
            return self.knight_moves()
        elif self.type == "bishop":
            return self.bishop_moves()
        elif self.type == "queen":
            return self.rook_moves() + self.bishop_moves()
        elif self.type == "king":
            return self.king_moves()

    def isInMoves(self, x, y):
        moves = self.moves()
        for move in moves:
            if move == (x, y):
                return True
        return False   

    def pawn_moves(self):
        moves = []
        if self.color == "white":
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6

        # check if pawn can move one square forward
        if self.board.isEmpty(self.x, self.y + direction):
            moves.append((self.x, self.y + direction))

            # check if pawn can move two squares forward from starting position
            if self.y == start_row and self.board.isEmpty(self.x, self.y + 2 * direction):
                moves.append((self.x, self.y + 2 * direction))

        # check if pawn can capture a piece diagonally
        if self.board.isEnemy(self.color, self.x - 1, self.y + direction):
            moves.append((self.x - 1, self.y + direction))
        if self.board.isEnemy(self.color, self.x + 1, self.y + direction):
            moves.append((self.x + 1, self.y + direction))

        return moves

    def knight_moves(self):
        moves = []
        possible_moves = [(self.x + 2, self.y + 1), (self.x + 2, self.y - 1),
                        (self.x - 2, self.y + 1), (self.x - 2, self.y - 1),
                        (self.x + 1, self.y + 2), (self.x + 1, self.y - 2),
                        (self.x - 1, self.y + 2), (self.x - 1, self.y - 2)]

        for move in possible_moves:
            if self.board.isInBoard(*move) and (self.board.isEmpty(*move)):# or self.board.isEnemy(self.color, *move)):
                moves.append(move)

        return moves

    def bishop_moves(self):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for direction in directions:
            for i in range(1, 8):
                x = self.x + i * direction[0]
                y = self.y + i * direction[1]
                if self.board.isInBoard(x, y):
                    if self.board.isEmpty(x, y):
                        moves.append((x, y))
                    else:
                        if self.board.isEnemy(self.color, x, y):
                            moves.append((x, y))
                        break
                else:
                    break
        return moves

    def rook_moves(self):
        moves = []
        
        # check moves to the right
        for x in range(self.x + 1, 8):
            if self.board.isEmpty(x, self.y):
                moves.append((x, self.y))
            elif self.board.isEnemy(self.color, x, self.y):
                moves.append((x, self.y))
                break
            else:
                break
        
        # check moves to the left
        for x in range(self.x - 1, -1, -1):
            if self.board.isEmpty(x, self.y):
                moves.append((x, self.y))
            elif self.board.isEnemy(self.color, x, self.y):
                moves.append((x, self.y))
                break
            else:
                break
        
        # check moves up
        for y in range(self.y - 1, -1, -1):
            if self.board.isEmpty(self.x, y):
                moves.append((self.x, y))
            elif self.board.isEnemy(self.color, self.x, y):
                moves.append((self.x, y))
                break
            else:
                break
        
        # check moves down
        for y in range(self.y + 1, 8):
            if self.board.isEmpty(self.x, y):
                moves.append((self.x, y))
            elif self.board.isEnemy(self.color, self.x, y):
                moves.append((self.x, y))
                break
            else:
                break
        
        return moves

    def king_moves(self):
        moves = []

        # Check all squares around the king
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                # Skip the square the king is currently on
                if i == self.x and j == self.y:
                    continue
                # If the square is on the board and is either empty or contains an enemy piece, add it to the list of moves
                if self.board.isInBoard(i, j):
                    piece = self.board.getPieceAt(i, j)
                    if not piece or self.board.isEnemy(self.color, i, j):
                        moves.append((i, j))

        # Check if castling is possible
        if self.startPosition:
            if self.board.isInBoard(self.x + 3, self.y):
                rook = self.board.getPieceAt(self.x + 3, self.y)
                if rook and rook.type == "rook" and rook.startPosition and not self.board.getPieceAt(self.x + 1, self.y) and not self.board.getPieceAt(self.x + 2, self.y):
                    moves.append((self.x + 2, self.y))
            if self.board.isInBoard(self.x - 4, self.y):
                rook = self.board.getPieceAt(self.x - 4, self.y)
                if rook and rook.type == "rook" and rook.startPosition and not self.board.getPieceAt(self.x - 1, self.y) and not self.board.getPieceAt(self.x - 2, self.y) and not self.board.getPieceAt(self.x - 3, self.y):
                    moves.append((self.x - 2, self.y))

        return moves

class ChessGame():
    def __init__(self):
        self.turn = 1
        self.timers = [180,180]
    
    def checkCheck(self):
        pass
    
    def checkMate(self):
        pass

    def checkDraw(self):
        pass

class Utilities():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("Szachy")
        self.view = QGraphicsView(self.window)
        scene = Board(self.view)
        self.view.setScene(scene)
        self.view.setFixedSize(10*50+500, 10*50)
        self.window.setCentralWidget(self.view)
        self.window.show()
        sys.exit(self.app.exec_())

if __name__ == '__main__':
    game = Utilities()

