import tkinter as tk
# Importing the custom board
import board

# Initialising the board
playWindow = tk.Tk() # Root window is created
playWindow.title("Sudoku") # Title added
side_size = 200 # This affects the amount of space on the right of the board (200 is needed)
play_area = board.GameBoard(playWindow,side_size=side_size) # Initialising the game board within the root window
play_area.pack(side="top", fill="both", expand="true", padx=0, pady=0) # Packing and displaying (in TkInter everything to be displayed in a window needs to be either "packed" or "placed"
playWindow.resizable(width=False, height=False) # This locks the size of the window so it cant be resized
playWindow.geometry(str(play_area.size*9+side_size)+"x"+str(play_area.size*9)) # This locks the geometry including side_size to encompass the visuals

# As with most GUIs the game runs out of the host object which in this case is a GameBoard called board.
# All the logic required to run a game of sudoku is included in the board class
# By calling mainloop() on the tkinter window we allow the buttons to run the game with no further code required here,
playWindow.mainloop()
