# Class to manage a 2D matrix
class Matrix2D:
    def __init__(self, val, size: tuple[int, int]) -> None:
        # Initialize a 2D matrix with a given value and size
        self.matrix = [[val for _ in range(size[0])] for _ in range(size[1])]
        self.size = size  # Store the size of the matrix

    def __getitem__(self, pos):
        # Get the value at the given position (x, y)
        x, y = pos
        return self.matrix[y][x]

    def __setitem__(self, pos, value):
        # Set the value at the given position (x, y)
        x, y = pos
        self.matrix[y][x] = value

    def __repr__(self):
        # Return a string representation of the matrix
        return '\n'.join([' '.join(map(str, row)) for row in self.matrix])

    def __iter__(self):
        # Iterate over all values in the matrix
        for row in self.matrix:
            for value in row:
                yield value

# Function to clear the terminal screen
def clear():
    from os import system, name
    system('cls' if name == 'nt' else 'clear')

# Minesweeper game class
class Minesweeper:
    def __init__(self, size: tuple[int, int], mine_density: int) -> None:
        # Initialize the Minesweeper game with given size and mine density
        self.over = False  # Game over flag
        self.size = size  # Board size
        self.n_mines = max(1, size[0] * size[1] * mine_density // 100)  # Number of mines based on density
        self.unboxed = 0  # Number of revealed cells
        self.numbers = Matrix2D(0, size)  # Matrix to store mine counts
        self.chr_box = '📦'  # Character for unrevealed cells
        self.chr_flag = '\033[31m ψ\033[0m'  # Character for flagged cells
        self.chr_bomb = '💀'  # Character for bombs
        self.mine_values = Matrix2D(self.chr_box, size)  # Matrix to store the display values
        self.mine_pos: set[tuple[int, int]] = set()  # Set to store mine positions
        self.flags: set[tuple[int, int]] = set()  # Set to store flagged positions
        self.revealed: set[tuple[int, int]] = set()  # Set to store revealed positions
        self.first = True  # Flag to check if the first move has been made

    def start(self, pos: tuple[int, int]):
        # Start the game by placing mines and setting values
        self.prev = pos  # Store the initial position
        self.set_mines(pos)  # Place mines avoiding the initial position
        self.set_values()  # Calculate the number of surrounding mines for each cell
        self.reveal(pos)  # Reveal the initial cell

    def get_neighbours(self, pos: tuple[int, int], factor: int = 1) -> list[tuple[int, int]]:
        # Get all neighbouring positions within the given factor
        x, y = pos
        # Generate the list of neighbours
        res = [(x + dx, y + dy) for dx in range(-factor, factor + 1) for dy in range(-factor, factor + 1)
               if (dx, dy) != (0, 0) and 0 <= x + dx < self.size[0] and 0 <= y + dy < self.size[1]]
        return res

    def distance(self, pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
        # Calculate the Euclidean distance between two positions
        from math import sqrt
        return sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def set_mines(self, f_pos: tuple[int, int]):
        # Place mines on the board avoiding the first position and its neighbours
        from random import choice
        from math import sqrt

        # Create a list of all positions on the board
        all_positions = [(x, y) for x in range(self.size[0]) for y in range(self.size[1])]
        # Get positions to avoid (first position and its immediate neighbours)
        bad_pos = set(self.get_neighbours(f_pos, 1) + [f_pos])
        # Filter out invalid positions
        valid_positions = [pos for pos in all_positions if pos not in bad_pos]
        # Calculate spacing for mine placement
        spacing = sqrt((self.size[0] * self.size[1] / self.n_mines) - 1)

        max_attempts = 1000  # Maximum number of attempts to place mines
        attempts = 0  # Attempt counter

        # Place mines until the required number of mines are placed
        while len(self.mine_pos) < self.n_mines:
            pos = choice(valid_positions)  # Choose a random valid position
            # Check if the chosen position is sufficiently spaced from other mines
            if all(self.distance(pos, m_pos) > spacing for m_pos in self.mine_pos) or choice([False] * (self.size[0] * self.size[1]) + [True]):
                self.mine_pos.add(pos)  # Add the mine position
                self.numbers[pos] = -1  # Mark the position as a mine
                attempts = 0  # Reset attempts counter
            else:
                attempts += 1  # Increment attempts counter

            # Adjust spacing if too many attempts are made
            if attempts > max_attempts:
                spacing *= 0.9  # Reduce spacing
                attempts = 0  # Reset attempts counter

    def set_values(self):
        # Set the number of surrounding mines for each cell
        for pos in self.mine_pos:
            for n_pos in self.get_neighbours(pos):
                if self.numbers[n_pos] != -1:
                    self.numbers[n_pos] += 1  # Increment the mine count for the neighbour

    def show_mines(self):
        # Reveal all mines on the board
        for pos in self.mine_pos:
            self.mine_values[pos] = self.chr_bomb  # Display bomb character

    def reveal(self, pos: tuple[int, int]):
        # Recursive function to reveal cells
        if pos in self.revealed:
            return  # Stop if the position is already revealed

        self.revealed.add(pos)  # Mark the position as revealed
        if self.numbers[pos] == 0:
            # If the cell is empty, reveal it and its neighbours
            self.mine_values[pos] = ' 0'
            for n_pos in self.get_neighbours(pos):
                self.reveal(n_pos)  # Recursively reveal neighbours
        else:
            # Otherwise, reveal the cell with the mine count
            self.mine_values[pos] = f' {self.numbers[pos]}'
        self.unboxed += 1  # Increment the count of revealed cells

    def move(self, pos: tuple[int, int]):
        # Handle a move to a specific position
        if self.first:
            self.first = False  # Disable the first move flag
            self.start(pos)  # Start the game on the first move
            return
        if self.numbers[pos] == -1:
            # If the cell contains a mine, reveal all mines and end the game
            self.show_mines()
            self.mine_values[pos] = '☠️ '
            self.over = True  # Set game over flag
            return -1
        else:
            # Otherwise, reveal the cell
            self.reveal(pos)
            return 0

    def flag(self, pos: tuple[int, int]):
        # Place or remove a flag on a cell
        if len(self.flags) >= self.n_mines or self.mine_values[pos] != self.chr_box or pos in self.flags or not (0 <= pos[0] < self.size[0] and 0 <= pos[1] < self.size[1]):
            return -1
        self.mine_values[pos] = self.chr_flag  # Place the flag
        self.flags.add(pos)  # Add to flagged positions

# Example usage of Minesweeper class
for i in Minesweeper((2, 2), 10).mine_values:
    print(i)
