import tkinter as tk
import pandas as pd
import numpy as np
import base64
import math
import time

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
        self.boardArray = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        self.bigSquares = pd.DataFrame(np.empty((3,3),dtype=np.str),index=range(0,3),columns=range(0,3))
        self.columnTrack = pd.DataFrame(np.empty((1,9),dtype=np.str),columns=range(0,9))
        self.rowTrack = pd.DataFrame(np.empty((9,1),dtype=np.str),index=range(0,9))
        self.basicMoves = pd.DataFrame(np.zeros((self.rows,self.columns)),index=range(0,self.rows),columns=range(0,self.columns))
        self.manualPencils = pd.DataFrame(np.empty((9,9),dtype=np.str),index=range(0,9),columns=range(0,9))

        self.desiredSquare = [] # This is the square that the player wants to move and is locked using the select piece button
        self.falseSquare = [] # Allows squares to be cleared
        self.validClick = False # This allows the board to know if a valid square to move to has been selected or not. This is stored on this level as it effects labels
        self.moveSquare = [] # This is the square that the player wants to move to

        # Adding all of the pictures from Images folder
        self.imageHolder = {} # Creating a dictionary
        pieceList = "0123456789" # These are all the different types of pieces possible
        for f in pieceList: # Cycling through the pieces
            for add in ["","_mini"]:
                with open("Images/"+f+add+".png","rb") as imageFile: # Opening the photo within the variable space
                    # The images can't be stored as P or p in MacOS as they're read the same
                    # So the colour is introduced by adding b or w after the piece notation
                    string = base64.b64encode(imageFile.read()) # Creating a string that describes the gif in base64 format
                    self.imageHolder[f+add] = tk.PhotoImage(data=string)
        with open("Images/pencil.png","rb") as imageFile:
            string = base64.b64encode(imageFile.read())
            self.imageHolder["pencil"] = tk.PhotoImage(data=string)
        # List that is used to control the location of pencil values
        self.shift = [[0,0],[-5,-5],[0,-5],[5,-5],[-5,0],[0,0],[5,0],[-5,5],[0,5],[5,5]]

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

        def PencilToggle(self):
            t = 1

        # Start and reset button
        self.reset_button = tk.Button(self,text="Reset Board",bg="black", command=self.Initiate)
        self.reset_button.place(x=self.square_virtual_size*self.rows + 115, y=110, height=16)
        self.start_button = tk.Button(self,text="Start!",fg="green",background="black",font=("TKDefaultFont",30), command=self.Initiate)
        self.start_button.place(x=self.square_virtual_size * self.rows+20,y=104,height=28)
        self.canvas.create_rectangle(self.square_virtual_size*9 + 6,232,self.square_virtual_size*9 + 10+192,302,width=2) # Just a hollow rectangle to denote an area
        self.pencil_mode = tk.Label(self,text="Pencil Mode:", bg="bisque")
        self.pencil_mode.place(x=self.square_virtual_size * self.rows+20,y=250,height=28)
        self.pencil_indicator = tk.StringVar()
        self.pencil_indicator.set("Off")
        self.pencil_button = tk.Radiobutton(self,textvariable=self.pencil_indicator,bg="red",indicatoron=False,width=8,command=self.PencilToggle)
        self.pencil_button.place(x=self.square_virtual_size * self.rows+130,y=250,height=28)
        self.clear_pencil_button = tk.Button(self,text="Clear Pencil",fg="orange",background="black",font=("TKDefaultFont",15), command=self.ClearAllPencil)
        self.clear_pencil_button.place(x=self.square_virtual_size * self.rows+115,y=285,height=20)
        self.canvas.create_image(self.square_virtual_size * self.rows+105,252,image=self.imageHolder["pencil"],tags="pencil_icon",anchor="c")
        self.pencilled = False
        self.auto_pencil_button = tk.Button(self,text="Auto Pencil",fg="green",background="black",font=("TKDefaultFont",15), command=self.PencilValues)
        self.auto_pencil_button.place(x=self.square_virtual_size * self.rows+25,y=285,height=20)
        self.auto_complete_button = tk.Button(self,text="Auto Complete",fg="green",background="black",font=("TKDefaultFont",20), command=self.AutoComplete)
        self.auto_complete_button.place(x=self.square_virtual_size * self.rows+50,y=325,height=20)

        # Adding information about the game
        self.canvas.create_rectangle(self.square_virtual_size*9 + 6,2,self.square_virtual_size*9 + 10+192,90,width=2) # Just a hollow rectangle to denote an area
        self.selection_heading = tk.Label(self,text="Current Game:",font=("TKDefaultFont",18),bg="bisque") # Heading
        self.selection_heading.place(x=self.square_virtual_size*9 + 36, y=18, height=16)
        self.square_text_x = tk.StringVar() # StringVar variables can be dynamically changed
        self.square_text_x.set("Selected Square (x) = None")
        self.selected_displaysx = tk.Label(self,textvariable=self.square_text_x, bg="bisque")
        self.selected_displaysx.place(x=self.square_virtual_size*9+17, y=40, height=16)
        self.square_text_y = tk.StringVar()
        self.square_text_y.set("Selected Square (y) = None")
        self.selected_displaysy = tk.Label(self,textvariable=self.square_text_y, bg="bisque")
        self.selected_displaysy.place(x=self.square_virtual_size*9 + 17, y=60, height=16)
        self.square_text_displaypiece = tk.StringVar()
        self.square_text_displaypiece.set("Selected Piece = None")
        self.selected_displaypiece = tk.Label(self,textvariable=self.square_text_displaypiece, bg="bisque")
        self.selected_displaypiece.place(x=self.square_virtual_size*9 + 17, y=80, height=16)

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
        # Checking if the game has ended. This is done here as there is no good place to perform it
        if self.EndCheck():
            exit()

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
            if self.boardArray.loc[row,col] != 0:
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

    def AddNum(self, name, image, row, column):
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
        self.boardArray.loc[row,column] = int(name)
        self.bigSquares.loc[math.floor(row/3), math.floor(column/3)] += name
        self.columnTrack.loc[0,column] += name
        self.rowTrack.loc[row,0] += name
        self.basicMoves.loc[row,column] = 0

    def RemoveNum(self, row, col):
        '''
        Deletes the piece image with the specified name from the board and the piece list
        :param row: Row to remove
        :param col: Colum to remove
        :return: None
        '''
        name = str(row)+"_"+str(col)
        self.canvas.delete(name) # Removes it based on its location id
        self.bigSquares.loc[math.floor(row / 3),math.floor(col / 3)] = self.bigSquares.loc[math.floor(row / 3),math.floor(col / 3)].strip(str(self.boardArray.loc[row,col]))
        self.boardArray.loc[row,col] = 0

    def PencilToggle(self):
        if self.pencil_indicator.get() == "On":
            self.pencil_indicator.set("Off")
            self.pencil_button.destroy()
            self.pencil_button = tk.Radiobutton(self,textvariable=self.pencil_indicator,bg="red",indicatoron=False,width=8,command=self.PencilToggle)
            self.pencil_button.place(x=self.square_virtual_size * self.rows+130,y=250,height=28)
            self.pencilled = False
        else:
            self.pencil_indicator.set("On")
            self.pencil_button.destroy()
            self.pencil_button = tk.Radiobutton(self,textvariable=self.pencil_indicator,bg="green",indicatoron=False,width=8,command=self.PencilToggle)
            self.pencil_button.place(x=self.square_virtual_size * self.rows+130,y=250,height=28)
            self.pencilled = True
        
    def PencilValues(self):
        '''
        Pencils in all values that are possibilities
        :return: None
        '''
        self.BasicCheck()
        self.canvas.delete("pencil")
        for row_check in range(0,self.rows):
            for col_check in range(0,self.columns):
                options = self.basicPossibles.loc[row_check,col_check]
                if len(options) > 0:
                    for x in options:
                        self.AddPencil(x,self.imageHolder[x+"_mini"],row_check,col_check)
        self.manualPencils = self.basicPossibles

    def ClearAllPencil(self):
        '''
        Clear all pencil marks
        :return: None
        '''
        self.canvas.delete("pencil")
        self.manualPencils = pd.DataFrame(np.empty((9,9),dtype=np.str),index=range(0,9),columns=range(0,9))

    def AddPencil(self, name, image, row, column):
        '''
        Adds in a penciled value
        :param name: Piece name such as r3 or K1
        :param image: An image from the imageholder dictionary
        :param row: Target row on the board
        :param column: Target column on the board
        :return: None
        '''
        # We can add a piece to the board at the requested location
        x0 = (column * self.size) + int(self.size/2) + 2 # Works out where it should be in pixels
        y0 = (row * self.size) + int(self.size/2) + 2
        tag_name = str(row)+"_"+str(column)+"p"+name
        x0 += self.shift[int(name)][0]*5
        y0 += self.shift[int(name)][1]*5
        self.canvas.create_image(x0,y0, image=image, tag=(tag_name, "pencil"), anchor="c") # First we create the image in the top left

    def RemovePencil(self, row, col, value):
        '''
        Removes a penciled value
        :param row: Row to remove
        :param col: Colum to remove
        :return: None
        '''
        if value == "All":
            for num in self.manualPencils.loc[row,col]:
                name = str(row)+"_"+str(col)+"p"+num
                self.canvas.delete(name) # Removes it based on its location id
                self.manualPencils.loc[row,col] = self.manualPencils.loc[row,col].split(num)[1]
        else:
            name = str(row)+"_"+str(col)+"p"+value
            self.canvas.delete(name)  # Removes it based on its location id
            self.manualPencils.loc[row,col] = self.manualPencils.loc[row,col].split(value)[1]

    def CalculateMoves(self):
        '''
        Updates all of the checks after a move has been made (this might have to be streamlined if it takes too long
        :return: None
        '''
        # Checking if basic Sudoku logic can be used
        self.BasicCheck()
        
    def BasicCheck(self):
        '''
        Checks using base Sudoku rules
        :return: None
        '''
        self.basicPossibles = pd.DataFrame(np.empty((9,9),dtype=np.str),index=range(0,9),columns=range(0,9))
        for row_scan in range(0, self.rows):
            for col_scan in range(0,self.columns):
                for num in range(1, 10):
                    if self.boardArray.loc[row_scan,col_scan] == 0:
                        if str(num) not in self.bigSquares.loc[math.floor(row_scan/3), math.floor((col_scan/3))]:
                            if str(num) not in self.columnTrack.loc[0,col_scan]:
                                if str(num) not in self.rowTrack.loc[row_scan,0]:
                                    self.basicPossibles.loc[row_scan,col_scan] += str(num)
        if not self.basicPossibles.all().all() == "":
            for row_scan in range(0,3):
                for col_scan in range(0,3):
                    for num in range(1, 10):
                        num_place = 0
                        num_loc = [10,10]
                        for row_add in range(0,3):
                            for col_add in range(0,3):
                                if self.boardArray.loc[row_scan*3+row_add,col_scan*3+col_add] == 0:
                                    if str(num) in self.basicPossibles.loc[row_scan*3+row_add,col_scan*3+col_add]:
                                        num_place += 1
                                        num_loc = [row_scan*3+row_add,col_scan*3+col_add]
                        if num_place == 1:
                            print("Row: "+str(num_loc[0])+" and Col: "+str(num_loc[1])+" = "+str(num))

    def HiddenCheck(self):
        '''
        Checks if any of the possible values can be eliminated by simple logic
        :return: None
        '''
        for row_scan in range(0,3):
            for col_scan in range(0,3):
                for num in range(1, 10):
                    for row_add in range(0,3):
                        for col_add in range(0,3):
                            if self.boardArray.loc[row_scan*3+row_add,col_scan*3+col_add] == 0:
                                if row_scan*3+row_add ==  2 and col_scan*3+col_add == 2:
                                    t = 1
                                if str(num) in self.basicPossibles.loc[row_scan*3+row_add,col_scan*3+col_add]:
                                    num_place += 1
                                    num_loc = [row_scan*3+row_add,col_scan*3+col_add]
                    if num_place == 1:
                        print("Row: "+str(num_loc[0])+" and Col: "+str(num_loc[1])+" = "+str(num))

    def AutoComplete(self):
        '''
        Completed the board
        :return: None
        '''
        self.BasicCheck()
        for row_check in range(0,self.rows):
            for col_check in range(0,self.columns):
                options = self.basicPossibles.loc[row_check,col_check]
                if len(options) == 1:
                    self.AddNum(options,self.imageHolder[options],row_check,col_check)
                    self.update()
                    self.AutoComplete()
                    return

    def EndCheck(self):
        """
        Checks the state of the board to detect them all being full
        :return: bool: True for the game is over, false if not
        """
        if self.boardArray.where(self.boardArray==0,1).sum().sum() == 81:
            return True
        else:
            return False

    def One(self, event):
        if self.validClick:
            self.PlacePiece("1")

    def Two(self, event):
        if self.validClick:
            self.PlacePiece("2")

    def Three(self, event):
        if self.validClick:
            self.PlacePiece("3")

    def Four(self, event):
        if self.validClick:
            self.PlacePiece("4")

    def Five(self, event):
        if self.validClick:
            self.PlacePiece("5")

    def Six(self, event):
        if self.validClick:
            self.PlacePiece("6")

    def Seven(self, event):
        if self.validClick:
            self.PlacePiece("7")

    def Eight(self, event):
        if self.validClick:
            self.PlacePiece("8")

    def Nine(self, event):
        if self.validClick:
            self.PlacePiece("9")

    def PlacePiece(self, number):
        '''
        Called by the keybind functions
        :param number: The number to be places
        :return: None
        '''
        row = self.desiredSquare[0]
        col = self.desiredSquare[1]
        if self.pencilled:
            if self.manualPencils.loc[row,col] == 0:
                self.AddPencil(number,self.imageHolder[number+"_mini"],row,col)
                self.manualPencils.loc[row,col] = number
            else:
                if number not in self.manualPencils.loc[row,col]:
                    self.AddPencil(number,self.imageHolder[number+"_mini"],row,col)
                    self.manualPencils.loc[row,col] += number
                else:
                    self.RemovePencil(row,col,number)

        else:
            self.AddNum(number,self.imageHolder[number],row,col)
            self.RemovePencil(row,col,"All")
            self.CalculateMoves()
            self.validClick = False
            self.falseSquare = self.desiredSquare
            self.canvas.delete("highlight")  # Clear highlighting
            self.canvas.delete("example")
            self.HighlightSquare(row,col,"orange",'highlight')  # Adding a blue edge around the square

    def Delete(self, event):
        if event.keysym == "BackSpace":
            if not self.validClick:
                row = self.falseSquare[0]
                col = self.falseSquare[1]
                self.RemoveNum(row,col)
                self.canvas.delete("highlight")  # Clear highlighting
                self.canvas.delete("example")
                self.HighlightSquare(row,col,"orange",'highlight')  # Adding a blue edge around the square

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
        self.CalculateMoves()

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
                    self.AddNum(col_string, self.imageHolder[col_string], row, col)

    def VisualsfromBoard(self):
        """
        Draw all pieces afresh based on boardarraypieces
        :return: None
        """
        for row in range(0,8):
            for col in range(0,8):
                if self.boardArray.loc[row,col] != 0:
                    self.AddNum(self.boardArray.loc[row,col].getid(),self.imageHolder[self.boardArray.loc[row,col].getid()[0]],row,col)

    def MovePiece(self):
        '''
        Runs most of the code to action a turn. Moves all visuals and internal variables as well as calculating new valid moves based on the move made.
        :return: None
        '''
        # First we check if their is a piece that needs to be removed
        if self.boardArray.loc[self.moveSquare[0],self.moveSquare[1]] != 0: # Is the square full
            self.RemoveNum(self.boardArray.loc[self.moveSquare[0],self.moveSquare[1]].getid()) # If so remove it
        self.PlacePiece(self.boardArray.loc[self.desiredSquare[0],self.desiredSquare[1]].getid(),self.moveSquare[0],self.moveSquare[1]) # Move the original piece
        self.boardArray.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArray.loc[self.desiredSquare[0],self.desiredSquare[1]] # Update boardarray
        self.boardArray.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Set the old square to empty
        self.colourArray.loc[self.desiredSquare[0],self.desiredSquare[1]] = 0 # Same for colour array
        self.colourArray.loc[self.moveSquare[0],self.moveSquare[1]] = self.boardArray.loc[self.moveSquare[0],self.moveSquare[1]].getcolour() # Set colour array to the piece colour
        self.boardArray.loc[self.moveSquare[0],self.moveSquare[1]].iterate() # Increment a turn for the piece
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