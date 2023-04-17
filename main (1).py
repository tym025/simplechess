from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys, os, re, time
from stockfish import Stockfish
import json
import xml.etree.ElementTree as ET
import sqlite3
import images_rc

class Board(QGraphicsScene):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        
        self.game = game
        self.board_size = 8
        self.cell_size = 50
        self.piecesOnBoard = []
        self.squares = [[-1 for j in range(self.board_size)] for i in range(self.board_size)]
        self.selectedPiece = 0
        self.moveRects = []
        self.enPassantSquare = (-1,-1)
        self.cells = []
        self.graphics = 0

        self.setup_cells()
        self.setup_letters_and_numbers()
        self.setup_pieces()
    
    def setup_cells(self):
        # Add cells to the board
        for i in range(self.board_size):
            for j in range(self.board_size):
                color = (i + j + 1) % 2
                self.cells.append(Cell(color, self.cell_size, i, j))
                self.addItem(self.cells[-1])

    def changeGraphics(self):
        if(self.graphics == 0):
            for i in range(self.board_size):
                for j in range(self.board_size):
                    color = (i + j + 1) % 2
                    if(color): self.cells[i*self.board_size+j].setPixmap(QPixmap(":/white_cell2"))
                    else: self.cells[i*self.board_size+j].setPixmap(QPixmap(":/black_cell2"))
            self.graphics = 1
        else:
            for i in range(self.board_size):
                for j in range(self.board_size):
                    color = (i + j + 1) % 2
                    if(color): self.cells[i*self.board_size+j].setPixmap(QPixmap(":/white_cell"))
                    else: self.cells[i*self.board_size+j].setPixmap(QPixmap(":/black_cell"))
            self.graphics = 0
        self.update()

    def setup_letters_and_numbers(self):
        # Add letters to the top and bottom rows
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

    def setup_pieces(self):
        pieces = self.get_pieces()
        id = 0
        
        pieces_info = [
            ("white", "pawn", [(i, 6) for i in range(self.board_size)]),
            ("black", "pawn", [(i, 1) for i in range(self.board_size)]),
            ("white", "rook", [(0, 7), (7, 7)]),
            ("black", "rook", [(0, 0), (7, 0)]),
            ("white", "knight", [(1, 7), (6, 7)]),
            ("black", "knight", [(1, 0), (6, 0)]),
            ("white", "bishop", [(2, 7), (5, 7)]),
            ("black", "bishop", [(2, 0), (5, 0)]),
            ("white", "queen", [(3, 7)]),
            ("black", "queen", [(3, 0)]),
            ("white", "king", [(4, 7)]),
            ("black", "king", [(4, 0)]),
        ]

        for color, piece_type, positions in pieces_info:
            for position in positions:
                piece = Piece(color, piece_type, self.cell_size, *position, self, self.squares, id)
                index = self.game.getSpriteIndex(piece)
                piece.setPixmap(pieces[index])
                self.addItem(piece)
                self.piecesOnBoard.append(piece)
                id += 1

    def get_pieces(self):
        image = QImage(':\pieces2')
        pieces = []
        for i in range(0, 600, 50):
            piece = QPixmap.fromImage(image.copy(i, 0, 50, 100))
            pieces.append(piece)
        return pieces

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

    def getMovablePieces(self, x, y, color=None):
        movable_pieces = []
        for piece in self.piecesOnBoard:
            if(color!=None and piece.color != color): continue
            if (x, y) in piece.moves():
                movable_pieces.append(piece)
        return movable_pieces

    def isInBoard(self, x, y):
        if(x >= 0 and x <= 7 and y >= 0 and y <= 7): return True
        return False
    
    def isEnemy(self, color, x, y):
        piece = self.getPieceAt(x, y)
        return piece is not None and piece.color != color

    def isEmpty(self, x, y):
        return self.squares[x][y] == -1

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.RightButton:
            self.changeGraphics()
            return
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
                print(f"{self.getPieceById(self.selectedPiece).color} {self.getPieceById(self.selectedPiece).type}")

    def mouseReleaseEvent(self, event):
        pos = event.scenePos()
        row = int(pos.y() // self.cell_size)
        col = int(pos.x() // self.cell_size)
        # Get the item at the clicked position
        if(self.isInBoard(col, row)):
            piece = self.getPieceById(self.selectedPiece)
            if(self.selectedPiece > -1): self.game.makeMove(piece, col, row)
            self.selectedPiece = -1
            self.clearMoves()

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
        self.squares[piece.x][piece.y] = -1

        # Remove the piece from the scene
        self.removeItem(piece)

        # Remove the piece from the list of pieces
        self.piecesOnBoard.remove(piece)

class Cell(QGraphicsPixmapItem):
    def __init__(self, color, size, x, y, parent=None):
        super().__init__(parent)
        
        self.color = color
        self.size = size
        self.x = x
        self.y = y
        self.occupied = -1
        
        if self.color == 0:
            self.setPixmap(QPixmap(":/black_cell"))
        else:
            self.setPixmap(QPixmap(":/white_cell"))
            
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
        self.nMoves = 0
        self.setPos(x * size, y * size )
        self.id = id
        self.squares = squares
        self.squares[self.x][self.y] = self.id

    def movePiece(self, newX, newY):
        if self.board.isInBoard(newX, newY) and self.isInMoves(newX, newY) and self.color ==  self.board.game.turn and self.color ==  self.board.game.activeClock:
            self.board.enPassantSquare = (-1,-1)
            destPiece = self.board.getPieceAt(newX, newY)
            if destPiece:
                # Remove the destination piece from the board and from the scene
                self.board.game.piecesTaken.append(destPiece)
                self.board.removePiece(destPiece.id)
                self.board.removeItem(destPiece)
            else:
                self.board.game.piecesTaken.append(0)

            if (self.type == "king" and abs(self.x-newX) > 1):
                if newX > self.x:  # castling to the right
                    rook = self.board.getPieceAt(self.board.board_size - 1, self.y)  # get the rook on the right
                    rook.board.game.makeMove(rook, self.board.board_size - 3, self.y)
                else:  # castling to the left
                    rook = self.board.getPieceAt(0, self.y)  # get the rook on the left
                    rook.board.game.makeMove(rook, 3, self.y)

            if self.type == "pawn":
                dx = abs(self.x - newX)
                dy = abs(self.y - newY)
                if dy > 1:
                    self.board.enPassantSquare = (newX,newY)
                elif dx == 1 and not destPiece:
                    enemy_pawn = self.board.getPieceAt(newX, self.y)
                    self.board.removePiece(enemy_pawn.id)
                    self.board.removeItem(enemy_pawn)
                    self.board.game.piecesTaken.append(enemy_pawn)
                elif (self.color == "black" and newY == 7) or (self.color == "white" and newY == 0):
                    dialog = PromotionDialog(self.color, self.board)
                    result = dialog.exec_()
                    if result == QDialog.Accepted:
                        promoted_piece = Piece(self.color, dialog.get_selected_piece(), 50, newX, newY, self.board, self.squares, self.id)
                        self.board.game.piecesTaken.append(self)
                        self.board.removePiece(self.id)
                        index = self.board.game.getSpriteIndex(promoted_piece)
                        pieces = self.board.get_pieces()
                        promoted_piece.setPixmap((pieces[index]))
                        self.board.addItem(promoted_piece)
                        self.board.piecesOnBoard.append(promoted_piece)
                        self.board.squares[newX][newY] = promoted_piece.id

            return True
        return False

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
        if self.color == "black":
            direction = 1
            start_row = 1
            enemy_pawn_row = 4
        else:
            direction = -1
            start_row = 6
            enemy_pawn_row = 3

        # check if pawn can move one square forward
        if self.board.isEmpty(self.x, self.y + direction):
            moves.append((self.x, self.y + direction))

        # check if pawn can move two squares forward from starting position
        if self.y == start_row and self.board.isEmpty(self.x, self.y + 2 * direction):
            moves.append((self.x, self.y + 2 * direction))

        # check if pawn can capture a piece diagonally
        left_diagonal = self.board.getPieceAt(self.x - 1, self.y + direction)
        if left_diagonal is not None and left_diagonal.color != self.color:
            moves.append((self.x - 1, self.y + direction))
        right_diagonal = self.board.getPieceAt(self.x + 1, self.y + direction)
        if right_diagonal is not None and right_diagonal.color != self.color:
            moves.append((self.x + 1, self.y + direction))

        # check for en passant
        if self.y == enemy_pawn_row:
            left_pawn = self.board.getPieceAt(self.x - 1, self.y)
            right_pawn = self.board.getPieceAt(self.x + 1, self.y)
            if left_pawn is not None and left_pawn.color != self.color and left_pawn.nMoves == 1 and self.board.enPassantSquare == ((self.x - 1, self.y)):
                moves.append((self.x - 1, self.y + direction))
            if right_pawn is not None and right_pawn.color != self.color and right_pawn.nMoves == 1 and self.board.enPassantSquare == ((self.x + 1, self.y)):
                moves.append((self.x + 1, self.y + direction))

        return moves

    def knight_moves(self):
        moves = []
        possible_moves = [(self.x + 2, self.y + 1), (self.x + 2, self.y - 1),
                        (self.x - 2, self.y + 1), (self.x - 2, self.y - 1),
                        (self.x + 1, self.y + 2), (self.x + 1, self.y - 2),
                        (self.x - 1, self.y + 2), (self.x - 1, self.y - 2)]

        for move in possible_moves:
            if self.board.isInBoard(*move) and (self.board.isEmpty(*move) or self.board.isEnemy(self.color, *move)):
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
        if self.nMoves == 0:
            if self.board.isInBoard(self.x + 3, self.y):
                rook = self.board.getPieceAt(self.x + 3, self.y)
                if rook and rook.type == "rook" and rook.nMoves == 0 and not self.board.getPieceAt(self.x + 1, self.y) and not self.board.getPieceAt(self.x + 2, self.y):
                    moves.append((self.x + 2, self.y))
            if self.board.isInBoard(self.x - 4, self.y):
                rook = self.board.getPieceAt(self.x - 4, self.y)
                if rook and rook.type == "rook" and rook.nMoves == 0 and not self.board.getPieceAt(self.x - 1, self.y) and not self.board.getPieceAt(self.x - 2, self.y) and not self.board.getPieceAt(self.x - 3, self.y):
                    moves.append((self.x - 2, self.y))

        return moves

class Clock(QWidget):
    def __init__(self, game, color, time):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.count_down)
        self.time = time*1000 # czas pozostały do odliczenia w milisekundach
        self.count = False # zmienna śledząca stan zegara
        self.setWindowTitle('Clock')
        self.setGeometry(200, 200, 300, 400)
        self.setStyleSheet("background : white;")
        self.hPointer = QPolygon([QPoint(6, 7), QPoint(-6, 7), QPoint(0, -50)])
        self.mPointer = QPolygon([QPoint(6, 7), QPoint(-6, 7), QPoint(0, -70)])
        self.sPointer = QPolygon([QPoint(1, 1), QPoint(-1, 1), QPoint(0, -90)])
        self.msPointer = QPolygon([QPoint(1, 1), QPoint(-1, 1), QPoint(0, -90)])
        self.bColor = Qt.black
        self.sColor = Qt.red
        self.msColor = Qt.blue

        self.label = QLabel(f'{color} clock', self)
        self.label.move(90, 360)
        self.label.setFont(QFont('Times New Roman', 15))

        self.color = color
        self.game = game
        self.timer.start(1)

    def count_down(self):
        if self.count:
            self.time -= 1
            if self.time <= 0:
                self.time = 0
                self.count = False
                mess = FullscreenMessage(f"{self.color} loses on time")
                proxy = QGraphicsProxyWidget()
                proxy.setWidget(mess)
                proxy.setPos(-250,-200)
                self.game.board.addItem(proxy)

        self.update()

    def paintEvent(self, event):
        rec = min(self.width(), self.height())

        painter = QPainter(self)

        def drawPointer(color, rotation, pointer):
            painter.setBrush(QBrush(color))
            painter.save()
            painter.rotate(rotation)
            painter.drawConvexPolygon(pointer)
            painter.restore()

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(rec / 200, rec / 200)
        painter.setPen(Qt.NoPen)

        drawPointer(self.bColor, (30 * (self.time / (1000*60*60) % 12 + self.time / (1000*60) % 360 / 60)), self.hPointer)
        drawPointer(self.bColor, (6 * (self.time / (1000*60) % 360 + self.time / 1000 % 60 / 60)), self.mPointer)
        drawPointer(self.sColor, (6 * (self.time / 1000) % 360), self.sPointer)
        drawPointer(self.msColor, (360 * ((self.time % 1000) / 1000)), self.msPointer)

        painter.setPen(QPen(self.bColor))
        for i in range(0, 60):
            if (i % 5) == 0:
                painter.drawLine(87, 0, 97, 0)
            painter.rotate(6)

        painter.end()

    def mousePressEvent(self, event):
        if(self.game.turn != self.color and self.game.moved): 
            self.game.activeClock = "black" if self.game.activeClock == "white" else "white"
            self.game.swapClocks()
            self.game.moved = False

class FullscreenMessage(QWidget):
    def __init__(self, message):
        super().__init__()
        
        # Create a label to display the message
        label = QLabel(message, self)
        
        # Set the label's font and alignment
        font = label.font()
        font.setPointSize(20)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        
        # Set the layout of the widget to a vertical layout
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        
        # Set the background color of the widget to white
        self.setStyleSheet("background-color: white;")
        
        # Set the widget to be fullscreen and show it
        self.showFullScreen()

class ConfigDialog(QDialog):
    def __init__(self, game):
        super().__init__()

        self.game = game
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Game Configuration")

        self.one_player_radio = QRadioButton("1 Player")
        if(self.game.players == "1player"): self.one_player_radio.setChecked(True)
        self.one_player_radio.toggled.connect(lambda:self.set_players("1player"))

        self.two_player_radio = QRadioButton("2 Players")
        if(self.game.players == "2player"): self.two_player_radio.setChecked(True)
        self.two_player_radio.toggled.connect(lambda:self.set_players("2player"))

        self.ai_game_radio = QRadioButton("AI Game")
        if(self.game.players == "aigame"): self.ai_game_radio.setChecked(True)
        self.ai_game_radio.toggled.connect(lambda:self.set_players("aigame"))

        self.ip_address_label = QLabel("IP Address (with mask):")
        self.ip_address_edit = QLineEdit()
        if(self.game.ip_address == ""): self.ip_address_edit.setPlaceholderText("e.g. 192.168.0.1/24")
        else: self.ip_address_edit.setText(self.game.ip_address)
        self.ip_address_edit.textChanged.connect(self.set_ip_address)

        self.button_save_config = QPushButton("Save Config")
        self.button_save_config.clicked.connect(self.save_config)

        self.button_save_xml = QPushButton("Save Moves as XML")
        self.button_save_xml.clicked.connect(self.save_moves_to_xml)

        self.button_save_sqlite3 = QPushButton("Save Moves as SQLITE3")
        self.button_save_sqlite3.clicked.connect(self.save_moves_to_sqlite3)

        self.button_load_moves = QPushButton("Load Moves from File")
        self.button_load_moves.clicked.connect(self.load_moves_from_file)

        button_group = QButtonGroup()
        button_group.addButton(self.one_player_radio)
        button_group.addButton(self.two_player_radio)
        button_group.addButton(self.ai_game_radio)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.one_player_radio)
        radio_layout.addWidget(self.two_player_radio)
        radio_layout.addWidget(self.ai_game_radio)

        ip_address_layout = QHBoxLayout()
        ip_address_layout.addWidget(self.ip_address_label)
        ip_address_layout.addWidget(self.ip_address_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(radio_layout)
        main_layout.addLayout(ip_address_layout)
        main_layout.addWidget(self.button_save_config)
        main_layout.addWidget(self.button_save_xml)
        main_layout.addWidget(self.button_save_sqlite3)
        main_layout.addWidget(self.button_load_moves)
        self.setLayout(main_layout)

    def set_players(self, players):
        self.game.players = players
        print(self.game.players)

    def set_ip_address(self, address):
        self.game.ip_address = address

    def save_config(self):
            # create a dictionary to store the game configuration
            config_dict = {"players": self.game.players, "ip_address": self.game.ip_address}

            # convert the dictionary to a JSON string
            config_json = json.dumps(config_dict)

            # create the JSON file and write the JSON string to it
            with open("game_config.json", "w") as f:
                f.write(config_json)

    def save_moves_to_xml(self):
        # create the root element and add the game moves as child elements
        root = ET.Element("game")
        for move in self.game.moves:
            ET.SubElement(root, "move").text = move

        # create the XML file and write the root element to it
        tree = ET.ElementTree(root)
        tree.write("game_moves.xml")

    def save_moves_to_sqlite3(self):
        # create a database connection and cursor
        self.conn = sqlite3.connect("game_moves.db")
        self.cursor = self.conn.cursor()

        # create the moves table if it does not exist
        self.cursor.execute("CREATE TABLE IF NOT EXISTS moves (id INTEGER PRIMARY KEY, moves TEXT)")

        # insert each move into the moves table
        for move in self.game.moves:
            print(f"Inserting move: {move}")
            self.cursor.execute("INSERT INTO moves (moves) VALUES (?)", (move,))

        # debug: print the number of rows affected by the INSERT statement
        print(f"Number of rows affected: {self.cursor.rowcount}")

        # commit the changes to the database
        self.conn.commit()

    def load_moves_from_file(self):
        # open a file dialog to select the file
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Database files (*.db *.sqlite *.sqlite3);;XML files (*.xml);;All files (*.*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec_() == QDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
        else:
            return

        tempmoves = []

        # read the moves from the file, depending on the file extension
        _, file_extension = os.path.splitext(file_path)
        if file_extension in [".db", ".sqlite", ".sqlite3"]:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT moves FROM moves")
            rows = cursor.fetchall()
            tempmoves = [row[0] for row in rows]
        elif file_extension == ".xml":
            tree = ET.parse(file_path)
            root = tree.getroot()
            tempmoves = [move.text for move in root.findall("move")]

        self.accept()

        movesMade = len(self.game.moves)
        self.game.moves = []
        self.game.inverseMove(movesMade)

        self.game.activeClock = "white"
        self.game.turn = "white"

        self.moves_iter = iter(tempmoves)

        self.timer = QTimer()
        self.timer.timeout.connect(self.move_piece)
        self.timer.start(300)

    def move_piece(self):
        try:
            notation = next(self.moves_iter)
            self.game.moveByChessNotation(notation)
            self.game.activeClock = "black" if self.game.activeClock is "white" else "white"
            self.game.board.update()
            self.game.swapClocks()
        except StopIteration:
            self.timer.stop()


class PromotionDialog(QDialog):
    def __init__(self, color, board):
        super().__init__()

        self.color = color
        self.piece_buttons = []
        self.selected_piece = None
        self.board = board

        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()

        pieces = ["queen", "rook", "bishop", "knight"]
        for i, piece in enumerate(pieces):
            button = QPushButton()
            button.setIcon(self.get_piece_icon(piece))
            button.setIconSize(QSize(70, 70))
            button.clicked.connect(lambda checked, piece=piece: self.on_piece_button_clicked(piece))
            layout.addWidget(button, i//2, i%2)
            self.piece_buttons.append(button)

        self.setLayout(layout)

    def get_piece_icon(self, piece):
        pieces = self.board.get_pieces()
        index = self.board.game.getSpriteIndex(color=self.color, type=piece)
        pixmap = QPixmap((pieces[index]))
        icon = QIcon(pixmap)
        return icon

    def on_piece_button_clicked(self, piece):
        self.selected_piece = piece
        self.accept()

    def get_selected_piece(self):
        return self.selected_piece

class ChessGame():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.view = QGraphicsView(self.window)
        self.board = Board(self, self.view)
        self.stockfish = Stockfish(path="stockfish_app")
        self.turn = "white"
        self.activeClock = "black"
        self.timers = [180, 180]
        self.isChecked = False
        self.moved = True
        self.moves = []
        self.piecesTaken = []
        self.turn_label = QLabel("Start", self.window)
        self.players = "2player"
        self.ip_address = ""

        self.load_config()
        self.setupLineEdit()
        self.setupClocks()
        self.setupView()
        self.showWindow()

    def setupLineEdit(self):
        self.lineEdit = QLineEdit()
        proxy = QGraphicsProxyWidget()
        self.lineEdit.textChanged.connect(self.moveByChessNotation)
        proxy.setWidget(self.lineEdit)
        proxy.setPos(100, -75)
        self.board.addItem(proxy)


    def setupClocks(self):
        cwWidget = QGraphicsProxyWidget()
        cbWidget = QGraphicsProxyWidget()
        self.clockWhite = Clock(self, "White", self.timers[0])
        self.clockBlack = Clock(self, "Black", self.timers[1])
        cwWidget.setWidget(self.clockWhite)
        cbWidget.setWidget(self.clockBlack)
        cwWidget.setPos(-425, 50)
        cbWidget.setPos(525, 50)
        self.board.addItem(cwWidget)
        self.board.addItem(cbWidget)

    def setupView(self):
        self.view.setScene(self.board)
        self.view.setFixedSize(10 * 50 + 500 + 400, 10 * 50 + 75)
        self.window.setCentralWidget(self.view)
        
        config_button = QPushButton("Config", self.window)
        config_button.move(10, 10)
        config_button.clicked.connect(self.openConfigDialog)

        best_move_button = QPushButton("Best move", self.window)
        best_move_button.move(110, 10)
        best_move_button.clicked.connect(self.bestMove)

        back_button = QPushButton("🡸", self.window)
        back_button.move(210, 10)
        back_button.clicked.connect(self.inverseMove)

        self.turn_label.move(1300, 10)
        self.turn_label.setFont(QFont('Times New Roman', 15))

    def openConfigDialog(self):
        config_dialog = ConfigDialog(self)
        config_dialog.exec_()

    def showWindow(self):
        self.window.show()
        self.window.setWindowTitle("Szachy")
        sys.exit(self.app.exec_())

    def inverseMove(self, n=1):
        if(not n): n=1
        reverse_moves = self.moves[-n:]
        reverse_removed_pieces = self.piecesTaken[-n:]
        for move in reverse_moves:
            start = move[2:]
            end = move[:2]
            start = [ord(start[0]) - 97, int(start[1]) - 1]
            piece = self.board.getPieceAt(start[0], 7-start[1])

            if(reverse_removed_pieces[0] != 0):
                self.board.piecesOnBoard.append(reverse_removed_pieces[0])
                print(f"{self.board.piecesOnBoard[-1].color} {self.board.piecesOnBoard[-1].type}")
                piece.squares[piece.x][piece.y] = reverse_removed_pieces[0].id
                self.board.piecesOnBoard[-1].setPos(self.board.piecesOnBoard[-1].x * self.board.piecesOnBoard[-1].size, self.board.piecesOnBoard[-1].y * self.board.piecesOnBoard[-1].size)
                self.board.addItem(self.board.piecesOnBoard[-1])
            else:
                piece.squares[piece.x][piece.y] = -1
            end = (ord(end[0]) - 97, int(end[1]) - 1)

            piece.x = end[0]
            piece.y = 7-end[1]
            piece.squares[piece.x][piece.y] = piece.id
            piece.setPos(piece.x * piece.size, piece.y * piece.size)

            piece.nMoves -= 1
            self.turn = "black" if self.turn == "white" else "white"
            if(not self.moved):
                self.activeClock = "black" if self.activeClock == "white" else "white"
                self.swapClocks()
                
            self.moved = False
            self.moves.pop()
            self.piecesTaken.pop()

    def makeMove(self, piece, newX, newY, recording=True):
        if(piece.movePiece(newX, newY)):
            piece.squares[piece.x][piece.y] = -1
            start = (chr(piece.x + 97) + str(7-piece.y + 1))

            piece.x = newX
            piece.y = newY
            piece.squares[piece.x][piece.y] = piece.id
            piece.setPos(piece.x * piece.size, piece.y * piece.size)
            end = (chr(newX + 97) +  str(7-newY + 1))

            piece.nMoves += 1
            piece.board.game.turn = "black" if piece.color=="white" else "white"
            piece.board.game.checkCheck()
            piece.board.game.moved = True

            moveNot = start+end
            if(moveNot == ('e1g1' or 'e8g8')): moveNot = '0-0'
            elif(moveNot == ('e1c1' or 'e8c8')): moveNot = '0-0-0'
            if(recording): self.moves.append(moveNot)
            print(self.moves)

    def bestMove(self):
        self.stockfish.set_position(self.moves)
        best_move = self.stockfish.get_best_move()
        self.moveByChessNotation(best_move)

    def swapClocks(self):
        if self.activeClock == "white":
            self.clockWhite.count = True
            self.clockBlack.count = False
        else:
            self.clockWhite.count = False
            self.clockBlack.count = True
        
        self.turn_label.setText(self.activeClock.capitalize())

    def moveByChessNotation(self, notation):
        # Check if notation is valid (e.g. "e2-e4" or "e4xf5" or "e4")

        if len(notation) < 2 or len(notation) > 6:
            return

        end = (-1,-1)
        piece = 0

        if len(notation) == 4:
            pattern = r'^[a-hA-H]\d[a-hA-H]\d$'
            if re.match(pattern, notation):
                # Get starting and ending coordinates from notation
                start = (ord(notation[0]) - 97, int(notation[1]) - 1)
                end = (ord(notation[2]) - 97, int(notation[3]) - 1)
                piece = self.board.getPieceAt(start[0], 7-start[1])
                print(f'{piece.color} {piece.type}')
        elif notation == "O-O" or notation == "o-o" or notation == "0-0":
        # Kingside castle
            if self.turn == "black":
                start = (4, 7)
                end = (6, 7)
            else:
                start = (4, 0)
                end = (6, 0)
            piece = self.board.getPieceAt(start[0], 7-start[1])
        elif notation == "O-O-O"  or notation == "o-o-o" or notation == "0-0-0":
            # Queenside castle
            if self.turn == "black":
                start = (4, 7)
                end = (2, 7)
            else:
                start = (4, 0)
                end = (2, 0)
            piece = self.board.getPieceAt(start[0], 7-start[1])
        elif len(notation) == 2:
            end = (ord(notation[0]) - 97, int(notation[1]) - 1)
            piece = None
            candidates = self.board.getMovablePieces(end[0], 7-end[1], color=self.turn)
            if len(candidates) == 1:
                piece = candidates[0]
            elif len(candidates) > 1:
                print("Ruch niejednoznaczny")
                return
            else:
                print("Brak pasującej figury")
                return
        else:
            print("Nieprawidłowa notacja")
            return

        
        self.makeMove(piece, end[0], 7-end[1])
        self.lineEdit.setText("")

    def getSpriteIndex(self, piece=None, color=None, type=None):
        if piece is not None:
            color = piece.color
            type = piece.type
        index = 0 if color == "white" else 11
        ratio = 1 if color == "white" else -1
        if type == "knight": index += ratio*1
        elif type == "rook": index += ratio*2
        elif type == "bishop": index += ratio*3
        elif type == "queen": index += ratio*4
        elif type == "king": index += ratio*5
        return index

    def checkCheck(self, mateChecking=False):
        if(self.turn == "white"):
            king = self.board.getPieceById(30)
        else:
            king = self.board.getPieceById(31)
        possibleAttackers = self.board.getMovablePieces(king.x, king.y)
        if(len(possibleAttackers) > 0):
            if(not mateChecking): 
                self.isChecked = True
                self.lineEdit.setText("SZACH")
                # self.checkMate()
            return True
        if(not mateChecking): self.isChecked = False
        return False

    def checkMate(self):
        pieces = self.board.piecesOnBoard
        print(f"Checking {self.turn} mate")
        for piece in pieces:
            if(piece.color == self.turn): continue
            moves = piece.moves()
            for move in moves:
                self.makeMove(piece, move[0], move[1])
                print(f"Checking {piece.color} {piece.type}")
                # Check if the move leads to a check
                if not self.checkCheck(mateChecking=True):
                    # The move is legal, so undo it and return False
                    self.inverseMove(1)
                    return

                # Undo the move
                self.inverseMove(1)

        # If no legal moves were found, return True
        print(f"{self.turn} wins by mate")

    def load_config(self):
        try:
            with open("game_config.json", "r") as f:
                config = json.load(f)
                self.players = config["players"]
                self.ip_address = config["ip_address"]
                print(self.ip_address)
                print("Config loaded successfully.")
        except FileNotFoundError:
            print("Config file not found.")

if __name__ == '__main__':
    game = ChessGame()

