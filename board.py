import tkinter as tk
import pandas as pd
import numpy as np
import base64
import math

class GameBoard(tk.Frame):
    """
    The main host that is called to start the game
    """
    def __init__(self, parent, side_size, square_size=80, rows=9, columns=9, color="#D3D3D3"):
        '''
        The GameBoard object hosts the whole game. Upon iitialisation the Sudoku squares are created and pieces drawn.
        :param parent: The tk root window inside of which you want the board to be drawn
        :param side_size: Dictates the width of the side panel with the game controls
        :param square_size: The size of the chess board in pixels
        :param rows: Rows in the chess board (default = 8)
        :param columns: Columns in the chess board (defailt = 8)
        :param color: This defines the background board colour
        '''
        # There is no need to edit any of the sizes. The default for side_size is 200
        # The default colors here are pure white and a dark gray

        # ---------------- Section 1 : Assembling basic variables ----------------
        self.rows = rows
        self.columns = columns
        self.size = square_size # This is the size in pixels of each square. This is essentially limited by the size of the chess piece images which are 60x60
        # In my experience the actual size of the squares isn't 80 when drawn. This is likely an overlap issue but comes out at 77
        self.square_virtual_size = 77 # So a variable is created to allow this to be carried throughout placement calculations
        self.top_offset = 2 # This accounts for the thickness of the lines

        self.side_size = side_size # The amount of blank space to the right of the board
        self.color = color # Colour 1 is the colour in the top left of the board
        self.initiated = False # Has a game started and effects the interpretation of clicks on the canvas

        # All of the piece objects are held within a pandas DataFrame in their relative locations.
        # This variable ultimately describes the state of the game
        self.boardArrayPieces = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))

        self.desiredSquare = [] # This is the square that the player wants to move and is locked using the select piece button
        self.falseSquare = [] # Allows squares to be cleared
        self.validClick = False # This allows the board to know if a valid square to move to has been selected or not. This is stored on this level as it effects labels
        self.moveSquare = [] # This is the square that the player wants to move to

        # Adding all of the pictures from Images folder
        self.imageHolder = {} # Creating a dictionary
        pieceList = "0123456789" # These are all the different types of pieces possible
        for f in pieceList: # Cycling through the pieces
            with open("Images/"+f+".png","rb") as imageFile: # Opening the photo within the variable space
                # The images can't be stored as P or p in MacOS as they're read the same
                # So the colour is introduced by adding b or w after the piece notation
                string = base64.b64encode(imageFile.read()) # Creating a string that describes the gif in base64 format
                self.imageHolder[f] = tk.PhotoImage(data=string)

        # ---------------- Section 2 : Creating the board ----------------
        # The whole board is drawn within the window in TkInter
        # This a very long section defining a lot of stationary visuals for the GUI
        # Most of the placement is just done by eye to make sure it all looks okay
        c_width = columns * self.size # Width the canvas needs to be
        c_height = rows * self.size # Height the canvas needs to be

        # Creating the canvas for the window
        tk.Frame.__init__(self, parent)
        # This is self explanatory and provides a blank space upon which visual objects can be placed
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, width=c_width, height=c_height, background="bisque")
        self.canvas.pack(side="top", fill="both", expand=True, padx=10, pady=10) # Packed with a small amount of padding either side

        # Adding a quit button to allow the window to be terminated. This has the same effect as clicking the cross
        self.quit_button = tk.Button(self,text="Quit Game", fg="red", command=self.quit)
        self.quit_button.place(x=self.square_virtual_size*self.rows + self.side_size/2-20, y=self.square_virtual_size*self.rows-40, height=20)

        # Adding a square/piece selected tracker
        self.canvas.create_rectangle(self.square_virtual_size*self.rows + 4,2,self.square_virtual_size*self.rows + 10+192,90,width=2) # Just a hollow rectangle to denote an area
        self.selection_heading = tk.Label(self,text="Current Selection:",font=("TKDefaultFont",18),bg="bisque") # Heading
        self.selection_heading.place(x=self.square_virtual_size*self.rows + 30, y=18, height=16)
        self.square_text_x = tk.StringVar() # StringVar variables can be dynamically changed
        self.square_text_x.set("Selected Square (x) = None")
        self.selected_displaysx = tk.Label(self,textvariable=self.square_text_x, bg="bisque")
        self.selected_displaysx.place(x=self.square_virtual_size*self.rows + 15, y=40, height=16)
        self.square_text_y = tk.StringVar()
        self.square_text_y.set("Selected Square (y) = None")
        self.selected_displaysy = tk.Label(self,textvariable=self.square_text_y, bg="bisque")
        self.selected_displaysy.place(x=self.square_virtual_size*self.rows + 15, y=60, height=16)
        self.square_text_displaypiece = tk.StringVar()
        self.square_text_displaypiece.set("Selected Piece = None")
        self.selected_displaypiece = tk.Label(self,textvariable=self.square_text_displaypiece, bg="bisque")
        self.selected_displaypiece.place(x=self.square_virtual_size*self.rows + 15, y=80, height=16)

        # Adding playmode selector
        self.playmode_height = 100 # Allows the whole rectangle to be moved up and down with contents
        self.canvas.create_rectangle(self.square_virtual_size*self.rows + 4,self.playmode_height,self.square_virtual_size*self.rows + 10+192,self.playmode_height+76,width=2)
        self.mode_heading = tk.Label(self,text="Playing Modes:",font=("TKDefaultFont",18),bg="bisque")
        self.mode_heading.place(x=self.square_virtual_size*self.rows + 45, y=self.playmode_height+15, height=20)
        self.player1_label = tk.Label(self,text="White:",bg="bisque")
        self.player1_label.place(x=self.square_virtual_size*self.rows + 15, y=self.playmode_height+45, height=16)
        self.player2_label = tk.Label(self,text="Black:",bg="bisque")
        self.player2_label.place(x=self.square_virtual_size*self.rows + 15, y=self.playmode_height+65, height=16)

        self.playmode1 = tk.StringVar()
        self.playmode1.set("Person")
        self.playmode2 = tk.StringVar()
        self.playmode2.set("Computer")
        self.player1 = tk.OptionMenu(self,self.playmode1,"Person","Computer","Random")
        self.player2 = tk.OptionMenu(self,self.playmode2,"Person","Computer","Random")
        self.player1.place(x=self.square_virtual_size*self.rows + 80, y=self.playmode_height+45, height=16)
        self.player1.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown
        self.player2.place(x=self.square_virtual_size*self.rows+80,y=self.playmode_height+65,height=16)
        self.player2.config(background="bisque") # For optionmenu the bg abbreviation means in the dropdown

        # Start and reset button
        self.reset_button = tk.Button(self,text="Reset Board",bg="black", command=self.Initiate)
        self.reset_button.place(x=self.square_virtual_size*self.rows + 115, y=202, height=16)
        self.start_button = tk.Button(self,text="Start!",fg="green",background="black",font=("TKDefaultFont",30), command=self.Initiate)
        self.start_button.place(x=self.square_virtual_size * self.rows+20,y=196,height=28)

        # Adding controls section to allow the game to be played
        self.controls_height = 225
        self.controls_heading = tk.Label(self,text="Controls:",font=("TKDefaultFont",18),bg="bisque")
        self.selectbuttonstring = tk.StringVar()
        self.selectbuttonstring.set("Select Piece")
        self.square_text_displaypiece_bybutton = tk.StringVar()
        self.square_text_displaypiece_bybutton.set("None")
        self.selected_displaypiece_bybutton = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,bg="bisque")
        self.summary_heading = tk.Label(self,text="Summary:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1 = tk.Label(self,text="Move:",font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel1_piece = tk.Label(self,textvariable=self.square_text_displaypiece_bybutton,font=("TKDefaultFont",10),bg="bisque")
        self.summarylabel2 = tk.Label(self,text="From:",font=("TKDefaultFont",10),bg="bisque")
        self.oldsquare = tk.StringVar()
        self.oldsquare.set("[ , ]")
        self.summarylabel2_piece = tk.Label(self,textvariable=self.oldsquare,font=("TKDefaultFont",10),bg="bisque")
        self.newsquare = tk.StringVar()
        self.newsquare.set("[ , ]")
        self.summarylabel3_piece = tk.Label(self,textvariable=self.newsquare,font=("TKDefaultFont",10),bg="bisque")

        self.movebutton = tk.Button(self,text="Move Piece",fg="black",background="black",font=("TKDefaultFont",22), command=self.MovePiece)
        self.movebutton.config(state="disabled")

        # Binding configuration and left mouse click
        self.canvas.bind("<Button 1>",self.GetCoords) # This allows the clicking to be tracked
        # Adding all the numbers for adding values
        self.canvas.focus_set()
        self.canvas.bind("<Key>",self.Delete)  # This allows the clicking to be tracked
        self.canvas.bind("1",self.One) # This allows the clicking to be tracked
        self.canvas.bind("2",self.Two) # This allows the clicking to be tracked
        self.canvas.bind("3",self.Three) # This allows the clicking to be tracked
        self.canvas.bind("4",self.Four) # This allows the clicking to be tracked
        self.canvas.bind("5",self.Five) # This allows the clicking to be tracked
        self.canvas.bind("6",self.Six) # This allows the clicking to be tracked
        self.canvas.bind("7",self.Seven) # This allows the clicking to be tracked
        self.canvas.bind("8",self.Eight) # This allows the clicking to be tracked
        self.canvas.bind("9",self.Nine) # This allows the clicking to be tracked

        # If a the user changes the window size then the refresh call is made. This is defined below
        # This function is also used to make the board
        self.canvas.bind("<Configure>", self.refresh) # This shouldn't happen as the size has been locked

    def GetCoords(self, event):
        '''
        This function listens for a click and passes the coordinates of any clicks into SelectSquare.
        :param event: A click
        :return: None
        '''
        global x0,y0
        x0 = event.x # Event is a click
        y0 = event.y
        # This retrieves the current x and y coordinates in terms of pixels from the top left
        if self.initiated: # If the game is started....
            self.SelectSquare(x0,y0) # This information is passed into the SelectSquare method

    def SelectSquare(self, xcoords, ycoords):
        '''
        Calculates a square from the x and y coordinates
        :param xcoords: x possition of click
        :param ycoords: y possition of click
        :return: None
        '''
        offset = self.square_virtual_size  # This is the number required to make it work......
        col = math.floor(xcoords / offset) # Finding the square the player means
        row = math.floor(ycoords / offset)
        if col <= self.columns-1 and row <= self.rows-1: # Have we clicked within the bounds of the board
            self.HighlightSquare(row,col,"blue",'highlight') # Adding a blue edge around the square
            # Then checking for what piece that is
            if self.boardArrayPieces.loc[row,col] != 0:
                self.validClick = False
                self.canvas.delete("highlight")  # Clear highlighting
                self.canvas.delete("example")
                self.HighlightSquare(row,col,"red",'highlight')  # Display a red edge
                self.falseSquare = [row,col]
            else:
                self.canvas.delete("move")  # Clearing all types of highlighting currently o the board
                self.canvas.delete("highlight")
                self.canvas.delete("example")
                self.HighlightSquare(row,col,"blue",'highlight') # Adding a blue edge around the square
                self.desiredSquare = [row,col] # Saving this information in the desiredSquare variable
                self.validClick = True

    def HighlightSquare(self,row,col,colour,tag):
        '''
        Adds visuals to the board to show which square has been selected
        :param row: Row on board
        :param col: Column on board
        :param colour: Colour for the square to be placed around the square
        :param tag: When lines are created they are assigned to this label
        :return: None
        '''
        # Recieves a square to put a box around
        offset = self.square_virtual_size # Finding the sze of a square
        if colour == "green": # If the colour requested is green we use a lighter colour
            colour = "#00cc00" # This is just a lighter green than the standard "green" color to make it clearer on the board
        self.canvas.create_line(col * offset,row * offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag) # Adding in the 4 lines
        self.canvas.create_line(col * offset,row * offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset+offset,row * offset,fill=colour,width=3,tag=tag)
        self.canvas.create_line(col * offset+offset,row * offset+offset,col * offset,row * offset+offset,fill=colour,width=3,tag=tag)

    def VisualiseMoves(self,row,col,piece_code):
        '''
        Adds visuals for the possible squares to which the selected piece can move
        :param row:
        :param col:
        :param piece_code:
        :return: None
        '''
        self.canvas.delete("example") # Removes all previously highlighted possible moves
        offset = self.square_virtual_size
        target_squares = self.PossibleMoves(row,col) # Requesting possible moves for the piece in that sqaure
        for plotter in target_squares: # Cycling through all squares
            self.HighlightSquare(int(plotter[0]),int(plotter[1]),"orange","example") # Adding an orange box around them

    def AddPiece(self, name, image, row, column):
        '''
        Adds a picture of the piece to the board at the square defined by row/column
        :param name: Piece name such as r3 or K1
        :param image: An image from the imageholder dictionary
        :param row: Target row on the board
        :param column: Target column on the board
        :return: None
        '''
        # We can add a piece to the board at the requested location
        x0 = (column * self.size) + int(self.size/2) + 2 # Works out where it should be in pixels
        y0 = (row * self.size) + int(self.size/2) + 2
        tag_name = str(row)+"_"+str(column)
        self.canvas.create_image(x0,y0, image=image, tag=(tag_name, "piece"), anchor="c") # First we create the image in the top left
        self.boardArrayPieces.loc[row,column] = int(name)

    def RemovePiece(self, row, col):
        '''
        Deletes the piece image with the specified name from the board and the piece list
        :param name: r3 or K1
        :return: None
        '''
        # This is only used when a piece is taken
        # This change is purely aesthetic
        name = str(row)+"_"+str(col)
        self.canvas.delete(name) # Removes it based on its location id
        self.boardArrayPieces.loc[row,col] = 0

    def One(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("1", self.imageHolder["1"], row, col)
            self.validClick = False

    def Two(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("2", self.imageHolder["2"], row, col)
            self.validClick = False

    def Three(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("3", self.imageHolder["3"], row, col)
            self.validClick = False

    def Four(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("4", self.imageHolder["4"], row, col)
            self.validClick = False

    def Five(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("5", self.imageHolder["5"], row, col)
            self.validClick = False

    def Six(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("6", self.imageHolder["6"], row, col)
            self.validClick = False

    def Seven(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("7", self.imageHolder["7"], row, col)
            self.validClick = False

    def Eight(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("8", self.imageHolder["8"], row, col)
            self.validClick = False

    def Nine(self, event):
        if self.validClick:
            row = self.desiredSquare[0]
            col = self.desiredSquare[1]
            self.AddPiece("9", self.imageHolder["9"], row, col)
            self.validClick = False

    def Delete(self, event):
        if event.keysym == "BackSpace":
            if not self.validClick:
                row = self.falseSquare[0]
                col = self.falseSquare[1]
                self.RemovePiece(row,col)

    def Initiate(self):
        '''
        This command is run from the start button of the control pannel and starts the game
        :return: None
        '''
        # This function starts the game upon request
        self.start_button.config(state="disabled") # Make it so the start button can't be pressed again
        self.initiated = True # Indicates that the game has started
        with open('puzzles') as f:
            lines = f.readlines()
        self.DisplayBoard(lines)

    def DisplayBoard(self, board_list):
        """
        This command is run from the start button of the control panel and starts the game
        :param board_list: string list of a Sudoku board
        :return: None
        """
        for row, row_string in enumerate(board_list):
            for col, col_string in enumerate(row_string):
                if col_string == "\n":
                    continue
                if col_string != "0":
                    self.AddPiece(col_string, self.imageHolder[col_string], row, col)

    def VisualsfromBoard(self):
        """
        Draw all pieces afresh based on boardarraypieces
        :return: None
        """
        for row in range(0,8):
            for col in range(0,8):
                if self.boardArrayPieces.loc[row,col] != 0:
                    self.AddPiece(self.boardArrayPieces.loc[row,col].getid(),self.imageHolder[self.boardArrayPieces.loc[row,col].getid()[0]],row,col)

    def MovePiece(self):
        '''
        Runs most of the code to action a turn. Moves all visuals and internal variables as well as calculating new valid moves based on the move made.
        :return: None
        '''
        # First we check if their is a piece that needs to be removed
        if self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]] != 0: # Is the square full
            self.RemovePiece(self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].getid()) # If so remove it
        self.PlacePiece(self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]].getid(),self.moveSquare[0],self.moveSquare[1]) # Move the original piece
        self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]] # Update boardarray
        self.boardArrayPieces.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Set the old square to empty
        self.colourArray.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Same for colour array
        self.colourArray.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].getcolour() # Set colour array to the piece colour
        self.boardArrayPieces.loc[self.moveSquare[0],self.moveSquare[1]].iterate() # Increment a turn for the piece
        self.canvas.delete("highlight") # Remove all highlighting
        self.canvas.delete("example")
        self.canvas.delete("move")
        # Allows for the the piece valid spaces to be updated by the latest move. This also checks to see if either king is in check
        check = self.UpdatePieceMoves()
        if check:
            # Then 1 of the kings is in check. This should only ever be 1 piece
            # We know which king by the attacks array but it should also only ever be the king whos turn it currently is
            self.CheckMate()
        # Flip the turn
        if self.current_turn_check == "w":
            self.current_turn_disp.set("Black Pieces")
            self.current_turn_check = "b"
            self.current_turn_text.config(bg="black",fg="white")
            self.holderEnum += 1
        else:
            self.current_turn_disp.set("White Pieces")
            self.current_turn_check = "w"
            self.current_turn_text.config(fg="black",bg="white")
            self.fullMove += 1 # This is iterated after black has played their move
            self.holderEnum -= 1
        # Invites the computer to take a turn
        self.CalculateTurn()

    def Screenshot(self):
        '''
        Takes a screenshot of the board and saves it with a time and date stamp
        :return:
        '''
        # This is very OTT
        from Quartz import CGWindowListCopyWindowInfo,kCGNullWindowID,kCGWindowListOptionAll
        import matplotlib.pyplot as plt
        from PIL import Image
        import os
        from uuid import uuid4
        import datetime
        gen_filename = lambda:str(uuid4())[-10:]+'.jpg'
        def capture_window(window_name):
            window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionAll,kCGNullWindowID)
            for window in window_list:
                try:
                    if window_name.lower() in window['kCGWindowName'].lower():
                        filename = gen_filename()
                        os.system('screencapture -l %s %s' % (window['kCGWindowNumber'],filename))
                        Image.open(filename).save(ChessComponents.__file__[:-27]+"Saved Games/"+datetime.datetime.now().strftime('%H:%M:%S').replace(":","_")+" "+datetime.date.today().strftime("%d-%b-%Y").replace("-","_")+".png")
                        os.remove(filename)
                        break
                except:
                    pass
        capture_window("Chess Game")

    def refresh(self, event):
        '''
        The size of the window is now locked and as a result I don't think this is ever called. In theory it updates all visuals should the window be resized.
        :param event: A click
        :return: None
        '''
        xsize = int((event.width-1) / self.columns)
        ysize = int((event.height-1) / self.rows)
        offset = self.top_offset
        self.size = min(xsize, ysize)
        self.canvas.delete("square")
        self.canvas.delete("big_square")
        color = self.color
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = (col * self.size) + offset
                y1 = (row * self.size) + offset
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="square")
        for row in range(int(self.rows/3)):
            for col in range(int(self.rows/3)):
                x1 = (col * self.size * 3) + offset
                y1 = (row * self.size * 3) + offset
                x2 = x1 + self.size * 3
                y2 = y1 + self.size * 3
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=4, tags="big_square")
        self.canvas.tag_raise("big_square")
        self.canvas.tag_lower("square")