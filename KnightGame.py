import tkinter as tk
from PIL import Image, ImageTk

class KnightGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Knight's Problem Game")

        # Default game settings
        self.mode = "Easy"          # Game mode: Easy or Expert
        self.grid_size = 5          # Board size (5x5 to 8x8)

        # Load and resize the knight image for display on the board
        self.knight_img = ImageTk.PhotoImage(
            Image.open("./images/black-chess-knight.png").resize((40, 40), Image.Resampling.LANCZOS)
        )
        self.knight_label = None    # Label to show the knight image on the board
        self.knight_placed = False  # Flag to check if knight is placed on the board

        # Title label at the top
        self.title = tk.Label(master, text="Knight's Problem", font=("Arial", 24))
        self.title.pack(pady=20)

        # Main menu buttons
        self.play_button = tk.Button(master, text="PLAY", font=("Arial", 16), command=self.play_game)
        self.play_button.pack(pady=10)

        self.mode_button = tk.Button(master, text=f"MODE: {self.mode}", font=("Arial", 16), command=self.toggle_mode)
        self.mode_button.pack(pady=10)

        self.grid_button = tk.Button(master, text=f"GRID: {self.grid_size}", font=("Arial", 16), command=self.toggle_grid)
        self.grid_button.pack(pady=10)

        self.rules_button = tk.Button(master, text="RULES", font=("Arial", 16), command=self.show_rules)
        self.rules_button.pack(pady=10)

        # Frame to hold the game grid (the board)
        self.grid_frame = tk.Frame(master)
        self.master.geometry("400x350")  # Initial window size
        self.grid_frame.pack(pady=20)

        # Label to show messages (not used currently)
        self.message_label = tk.Label(master, text="", font=("Arial", 14))

        # Bottom frame holds exit button and timer display
        self.bottom_frame = tk.Frame(master)
        self.exit_button = tk.Button(self.bottom_frame, text="EXIT", font=("Arial", 16), command=self.show_menu)
        self.timer_label = tk.Label(self.bottom_frame, text="", font=("Arial", 14))

        # Timer control variables
        self.timer_running = False
        self.elapsed_seconds = 0

        # Button for showing rules during gameplay (small button)
        self.small_rules_button = None

        # Game state variables
        self.current_knight_pos = None  # Current knight position (row, col)
        self.valid_moves = []           # List of valid moves from current position
        self.visited_cells = []         # Cells already visited by the knight

        self.turn = 0                   # Keep track of the number of moves made
        self.turn_label = tk.Label(master, text="Turn 0", font=("Arial", 14, "bold"), fg="black")

    def toggle_mode(self):
        # Switch between Easy and Expert mode, update button label accordingly
        self.mode = "Expert" if self.mode == "Easy" else "Easy"
        self.mode_button.config(text=f"MODE: {self.mode}")

    def toggle_grid(self):
        # Change grid size from 5 to 8, then cycle back to 5
        self.grid_size = 5 if self.grid_size == 8 else self.grid_size + 1
        self.grid_button.config(text=f"GRID: {self.grid_size}")

    def hide_menu(self):
        # Hide all main menu buttons when starting the game
        self.play_button.pack_forget()
        self.mode_button.pack_forget()
        self.grid_button.pack_forget()
        self.rules_button.pack_forget()

    def show_menu(self):
        # Show the main menu buttons and reset game interface
        self.timer_running = False     # Stop timer if running
        self.timer_label.pack_forget()
        self.grid_frame.pack_forget()
        self.exit_button.pack_forget()
        self.bottom_frame.pack_forget()
        self.message_label.pack_forget()
        self.turn_label.pack_forget()

        # Remove small rules button if it exists
        if self.small_rules_button and self.small_rules_button.winfo_exists():
            self.small_rules_button.destroy()
            self.small_rules_button = None

        # Show main menu buttons again
        self.play_button.pack(pady=10)
        self.mode_button.pack(pady=10)
        self.grid_button.pack(pady=10)
        self.rules_button.pack(pady=10)

        self.knight_placed = False
        self.master.geometry("400x350")  # Reset window size

        # Remove knight image if present
        if self.knight_label:
            self.knight_label.place_forget()
            self.knight_label.destroy()
            self.knight_label = None

    def update_timer(self):
        # Update the timer label every second if timer is running
        if self.timer_running:
            self.elapsed_seconds += 1
            h = self.elapsed_seconds // 3600
            m = (self.elapsed_seconds % 3600) // 60
            s = self.elapsed_seconds % 60
            self.timer_label.config(text=f"{h}h {m}min {s}sec")
            self.master.after(1000, self.update_timer)

    def show_rules(self):
        # Display game rules in a new window, bring to front if already open
        if hasattr(self, 'rules_window') and self.rules_window.winfo_exists():
            self.rules_window.lift()
            return

        self.rules_window = tk.Toplevel(self.master)
        self.rules_window.title("Game Rules")
        self.rules_window.resizable(False, False)

        # Game rules text with emojis for clarity
        rules_text = (
            "🆕 Starting Position:\n"
            "- You must place the knight on any cell to start the game.\n\n"
            "♞ Knight's Movement:\n"
            "- The knight moves in an 'L' shape:\n"
            "  • Two squares in one direction (horizontal or vertical), then\n"
            "  • One square perpendicular to that.\n"
            "- The knight jumps over other cells.\n\n"
            "🏁 How to Win:\n"
            "- Successfully move the knight to cover all cells **exactly once**.\n\n"
            "❌ How to Lose:\n"
            "- If the knight has no valid moves left **before visiting all cells**.\n\n"
            "🟢 Easy Mode:\n"
            "- Possible moves are **highlighted in blue**.\n\n"
            "⚫ Expert Mode:\n"
            "- No possible moves are shown. Think before each step!"
        )

        label = tk.Label(self.rules_window, text=rules_text, justify="left", font=("Arial", 12), padx=10, pady=10)
        label.pack()

        close_btn = tk.Button(self.rules_window, text="Close", command=self.rules_window.destroy)
        close_btn.pack(pady=10)

        # Clean up rules window reference when closed
        self.rules_window.protocol("WM_DELETE_WINDOW", self.on_rules_close)

    def on_rules_close(self):
        # Remove reference to rules window when it is closed
        if hasattr(self, 'rules_window'):
            self.rules_window.destroy()
            del self.rules_window

    def play_game(self):
        # Start a new game: hide menu, reset state, create the grid and start timer
        self.hide_menu()
        self.turn = 0
        self.visited_cells = []
        self.elapsed_seconds = 0
        self.timer_running = True
        self.timer_label.config(text="0h 0min 0sec")

        # Clear any existing grid cells
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        # Create label for knight image on board
        self.knight_label = tk.Label(self.master, image=self.knight_img, borderwidth=0)

        # Create grid cells (labels), bind click to place knight
        cell_size_px = 50
        self.cells = []
        for row in range(self.grid_size):
            self.grid_frame.grid_rowconfigure(row, minsize=cell_size_px)
            row_cells = []
            for col in range(self.grid_size):
                self.grid_frame.grid_columnconfigure(col, minsize=cell_size_px)
                cell = tk.Label(
                    self.grid_frame,
                    text="",
                    borderwidth=1,
                    relief="solid",
                    bg="light gray",
                    font=("Arial", 10)
                )
                cell.grid(row=row, column=col, sticky="nsew")  # Expand to fill 50px cell
                cell.bind("<Button-1>", self.make_place_knight_handler(row, col))
                row_cells.append(cell)
            self.cells.append(row_cells)
        # Set fixed size for grid frame and pack it
        self.grid_frame.config(width=self.grid_size * 50, height=self.grid_size * 50)
        self.grid_frame.pack_propagate(False)
        self.grid_frame.pack(pady=20)
        

        # Show the turn label under the grid
        self.turn_label.config(text="Turn 0", font=("Arial", 14, "bold"), fg="black")
        self.turn_label.pack(pady=(0, 5))

        self.message_label.pack_forget()

        # Pack exit button and timer label in the bottom frame
        self.exit_button.pack(side="left", padx=10)
        self.timer_label.pack(side="left", padx=10)
        self.bottom_frame.pack(pady=10)

        # Remove old small rules button if present
        if self.small_rules_button and self.small_rules_button.winfo_exists():
            self.small_rules_button.destroy()

        self.master.update_idletasks()  # Update window size info

        # Adjust window size to fit the grid nicely
        grid_width = self.grid_frame.winfo_width()
        window_width = grid_width + 50
        window_height = self.grid_size * 50 + 200
        self.master.geometry(f"{window_width}x{window_height}")

        # Create and place a small "RULES" button above the grid for quick access
        self.small_rules_button = tk.Button(self.master, text="RULES", font=("Arial", 10, "bold"), width=10, command=self.show_rules)
        button_width_px = 105
        button_x = (window_width - button_width_px) // 2
        self.small_rules_button.place(x=button_x, y=self.grid_frame.winfo_y() - 35)

        self.knight_placed = False

        # Start the timer update loop
        self.update_timer()

    def make_place_knight_handler(self, row, col):
        # Return a handler function that calls place_knight with given row and col
        def handler(event):
            self.place_knight(row, col)
        return handler

    def place_knight(self, row, col):
        # Handle placing or moving the knight on the board

        # If knight is placed, only allow moves to valid next positions
        if self.knight_placed and (row, col) not in self.valid_moves:
            return

        # If first move, mark knight as placed and set turn to 1
        if not self.knight_placed:
            self.knight_placed = True
            self.turn = 1
        else:
            # For subsequent moves, increase turn and add previous position to visited
            self.turn += 1
            self.visited_cells.append((self.knight_row, self.knight_col))

        # Update knight's current position
        self.knight_row = row
        self.knight_col = col

        # Update turn label
        self.turn_label.config(text=f"Turn {self.turn}", font=("Arial", 14, "bold"), fg="black")

        # Reset all cell backgrounds, mark visited cells red
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) in self.visited_cells:
                    self.cells[r][c].config(bg="#FF0000")  # red = visited
                else:
                    self.cells[r][c].config(bg="light gray")  # default

        # Highlight knight's current cell red too
        self.cells[row][col].config(bg="#FF0000")

        # Show turn number inside knight's cell if Easy mode
        if self.mode == "Easy":
            self.cells[row][col].config(text=str(self.turn), font=("Arial", 9, "bold"), fg="black")
        
        # Ensure geometry is fully computed before placing the knight image
        self.master.update_idletasks()

        # Place knight image centered in the current cell
        cell = self.cells[row][col]
        cell_x = cell.winfo_x()
        cell_y = cell.winfo_y()
        cell_width = cell.winfo_width()
        cell_height = cell.winfo_height()
        x = self.grid_frame.winfo_x() + cell_x + (cell_width // 2) - (40 // 2)
        y = self.grid_frame.winfo_y() + cell_y + (cell_height // 2) - (40 // 2)
        self.knight_label.place(x=x, y=y)

        # Calculate valid moves for next step
        self.valid_moves = self.get_knight_moves(row, col)

        # Highlight valid moves in Easy mode with light blue 
        if self.mode == "Easy":
            for (r, c) in self.valid_moves:
                self.cells[r][c].config(bg="#ADD8E6")  # light blue for valid move
                self.cells[r][c].bind("<Button-1>", self.make_place_knight_handler(r, c))
        else:
            # Expert mode: no highlighting
            for (r, c) in self.valid_moves:
                self.cells[r][c].bind("<Button-1>", self.make_place_knight_handler(r, c))

        # Remove click bindings from invalid cells so only valid moves can be clicked
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if (r, c) not in self.valid_moves and (r, c) != (row, col):
                    self.cells[r][c].unbind("<Button-1>")

        # Check if game is over (no valid moves left)
        total_cells = self.grid_size * self.grid_size
        visited_count = len(self.visited_cells) + 1  # Count current cell too

        if not self.valid_moves:
            # Stop the timer as game ended
            self.timer_running = False
 
            if visited_count == total_cells:
                # Player visited all cells, they win
                self.turn_label.config(text="YOU WIN", font=("Arial", 14, "bold"), fg="green")
            else:
                # No moves left but not all cells visited, game over
                self.turn_label.config(text="GAME OVER", font=("Arial", 14, "bold"), fg="red")
        else:
            # Normal turn display during the game
            self.turn_label.config(text=f"Turn {self.turn}", font=("Arial", 14, "bold"), fg="black")

    def get_knight_moves(self, row, col):
        # Calculate all possible knight moves from the current position
        moves = [
            (row + 2, col + 1),
            (row + 2, col - 1),
            (row - 2, col + 1),
            (row - 2, col - 1),
            (row + 1, col + 2),
            (row + 1, col - 2),
            (row - 1, col + 2),
            (row - 1, col - 2),
        ]

        # Keep only moves inside the board and not yet visited
        valid = [
            (r, c) for r, c in moves
            if 0 <= r < self.grid_size and 0 <= c < self.grid_size and (r, c) not in self.visited_cells and (r, c) != (self.knight_row, self.knight_col)
        ]

        return valid