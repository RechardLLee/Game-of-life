"""
The program is a simulation of Conway's Game of Life, a popular cellular automaton game that simulates the evolution of a grid of cells. The user can input the size of each cell, the size of the grid, and the refresh time for the simulation. The user also has the option to start the simulation with a randomly generated black and white image or all white image.

The user can interact with the simulation using their mouse. Left-clicking on a cell will make it alive, right-clicking on a cell will make it dead, and middle-clicking on a cell will start the simulation. The user can also press the spacebar to stop the simulation at any time.

The program will continuously update the grid based on the rules of Conway's Game of Life and draw the updated cells on the screen, refreshing every "refresh_time" milliseconds. The user can exit the program by clicking the x button on the window or pressing the escape key.

"""
"""
Pseudocode:

Import necessary modules (pygame, numpy, sys, tkinter, threading)

Create a function "game_of_life" that takes in a grid as a parameter:
a. Create a copy of the grid to update the cell states
b. Iterate through the rows and columns of the grid
c. Count the number of living neighbors for the current cell
d. Check if the current cell is alive
e. If it has less than 2 or more than 3 living neighbors, set the cell in the new_grid to 0
f. If the current cell is dead and has exactly 3 living neighbors, set the cell in the new_grid to 1
g. Return the new_grid

Create a main function:
a. Get the size of each cell, the size of the grid, and the refresh time from the user
b. Get the user's choice for a random image
c. Set the options for a random image
d. Calculate the number of rows and columns in the grid
e. Create a grid of randomly chosen 0's and 1's
f. Set the size of the window and create it
g. Set the caption of the window
h. Set the colors for the cells (white and black)
i. Initialize the running state to false
j. Create a while loop that runs indefinitely

Inside the while loop, handle events:
a. Exit the program if the user clicks the x button or presses the escape key
b. Handle the spacebar key press event to stop the simulation
c. Handle mouse button events
i. Get the position of the mouse click and calculate the row and column of the cell that was clicked
ii. Left mouse button makes the cell alive
iii. Middle mouse button starts/stops the simulation
iv. Right mouse button makes the cell dead

Update the grid using the game_of_life function

Draw the cells on the screen using a nested for loop to iterate through the rows and columns of the grid, 
and using the color of the cell (white or black) to fill the cell on the screen

Refresh the screen every "refresh_time" milliseconds

End the while loop and the main function

Call the main function to start the program.
"""

import pygame
import numpy as np
import sys
import tkinter as tk
import threading

# Function that simulates the next generation of cells based on the rules of Conway's Game of Life
def game_of_life(grid):
    # Create a copy of the grid to update the cell states
    new_grid = grid.copy()
    # Iterate through the rows and columns of the grid
    for i in range(n):
        for j in range(m):
            # Count the number of living neighbors for the current cell
            neighbors = (grid[i-1, j-1] + grid[i-1, j] + grid[i-1, (j+1) % m] +
                         grid[i, j-1] + grid[i, (j+1) % m] +
                         grid[(i+1) % n, j-1] + grid[(i+1) % n, j] + grid[(i+1) % n, (j+1) % m])
            # Check if the current cell is alive
            if grid[i, j] == 1:
                # If it has less than 2 or more than 3 living neighbors, it dies
                if neighbors < 2 or neighbors > 3:
                    new_grid[i, j] = 0
            else:
                # If the current cell is dead and has exactly 3 living neighbors, it becomes alive
                if neighbors == 3:
                    new_grid[i, j] = 1
    return new_grid


def main():
    global n, m

    # Get the size of each cell and the size of the grid from the user
    cell_size = int(entry0.get())
    x_size = int(entry1.get())
    y_size = int(entry2.get())
    # Get the refresh time from the user
    refresh_time = int(entry3.get())
    # Get the user's choice for a random image
    random_image = entry4.get()

    # Set the options for a random image
    black_white = [0, 0]
    if random_image == "y":
        black_white = [0, 1]
    elif random_image == "n":
        black_white = [0, 0]

    # Calculate the number of rows and columns in the grid
    n = x_size // cell_size
    m = y_size // cell_size

    # Create a grid of randomly chosen 0's and 1's
    grid = np.random.choice(black_white, size=(n, m))

    # Set the size of the window and create it
    size = (x_size, y_size)
    screen = pygame.display.set_mode(size)

    # Set the caption of the window
    pygame.display.set_caption("Conway's Game of Life")

    # Set the colors for the cells
    white = (255, 255, 255)
    black = (0, 0, 0)

    # Initialize the running state
    running = False

    while True:
        # Handle events
        for event in pygame.event.get():
            # Exit the program if the user clicks the x button or presses the escape key
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            # Handle the spacebar key press event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False

            # Handle mouse button events
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Get the position of the mouse click
                pos = pygame.mouse.get_pos()
                # Calculate the row and column of the cell that was clicked
                i, j = pos[0]//cell_size, pos[1]//cell_size
                if event.button == 1:
                    # Left mouse button makes the cell alive
                    grid[i, j] = 1
                elif event.button == 2:
                    # Middle mouse button starts/stops the simulation
                    running = True
                elif event.button == 3:
                    # Right mouse button makes the cell dead
                    grid[i, j] = 0
            # Handle mouse movement events
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0] == 1:
                    # Left mouse button makes the cell alive
                    pos = pygame.mouse.get_pos()
                    i, j = pos[0]//cell_size, pos[1]//cell_size
                    if  x_size > i*cell_size and y_size > j*cell_size and i>-1 and j>-1:

                        grid[i, j] = 1
                if event.buttons[2] == 1:
                    # Right mouse button makes the cell dead
                    pos = pygame.mouse.get_pos()
                    i, j = pos[0]//cell_size, pos[1]//cell_size
                    if  x_size > i*cell_size and y_size > j*cell_size and i>-1 and j>-1:
                        grid[i, j] = 0

        if running:
            # Draw the current state of the grid
            for i in range(n):
                for j in range(m):
                    if grid[i, j] == 0:
                        color = white
                    else:
                        color = black
                    pygame.draw.rect(screen, color, (i*cell_size,
                                                     j*cell_size, cell_size, cell_size))

            # Update the display
            pygame.display.flip()

            # Simulate the next generation of cells
            grid = game_of_life(grid)
            # Wait for the user-specified refresh time
            pygame.time.wait(refresh_time)

        elif not running:
            # Draw the current state of the grid
            for i in range(n):
                for j in range(m):
                    if grid[i, j] == 0:
                        color = white
                    else:
                        color = black
                    pygame.draw.rect(screen, color, (i*cell_size,
                                                     j*cell_size, cell_size, cell_size))
            # Update the display
            pygame.display.flip()
            
# Function that runs the provided function in a separate thread

def thread_it(func, *args):
    # Create a new thread
    t = threading.Thread(target=func, args=args) 
    # Set the thread as a daemon thread
    t.setDaemon(True) 
    # Start the thread
    t.start()

# Create the main window
windows = tk.Tk()
windows.geometry("1160x430")
windows.title('Conway\'s Game of Life')
windows.configure(background='grey')

# Create labels for the user input fields
LabeL0 = tk.Label(windows, text='Cell Size', width=15)
LabeL0.grid(row=1, column=0)
LabeL1 = tk.Label(windows, text='x_size', width=15)
LabeL1.grid(row=2, column=0)
LabeL2 = tk.Label(windows, text='y_size', width=15)
LabeL2.grid(row=3, column=0)
LabeL3 = tk.Label(windows, text='refresh_time(ms)', width=15)
LabeL3.grid(row=4, column=0)
LabeL4 = tk.Label(windows, text='random(y/n)', width=15)
LabeL4.grid(row=5, column=0)

# Create a label to display the rules of the simulation
text1 = '''
1.Any live cell with fewer than two live neighbours dies, as if by underpopulation.

2.Any live cell with two or three live neighbours lives on to the next generation.

3.Any live cell with more than three live neighbours dies, as if by overpopulation.

4.Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

'''
lb = tk.Label(windows, text=text1,  
			width=100,               
			height=60,       
			justify='left',         
			anchor='nw',          
			font=("Microsoft YaHei UI",15),    
			fg='white',            
			bg='grey',          
			padx=0,                
			pady=0)                
lb.grid(row=8, column=3)

# Create entry fields for the user input
entry0 = tk.Entry(windows, width=15)
entry0.grid(row=1, column=2)
entry1 = tk.Entry(windows, width=15)
entry1.grid(row=2, column=2)
entry2 = tk.Entry(windows, width=15)
entry2.grid(row=3, column=2)
entry3 = tk.Entry(windows, width=15)
entry3.grid(row=4, column=2)
entry4 = tk.Entry(windows, width=15)
entry4.grid(row=5, column=2)

# Create a button to start the simulation
button1 = tk.Button(windows, text="Start", command=lambda : thread_it(main)  , width=15)
button1.grid(row=7, column=0)

# Run the main loop of the window
windows.mainloop()