# By Sajjad - Spring 2026

import tkinter as tk
import time

# --- Algorithm State ---
memo_table = {}
board_state = "........." # 9 chars: '.' empty, 'X' user, 'O' agent
cache_hits_this_turn = 0
evals_this_turn = 0

# --- Core Algorithm (Modified for Logging) ---
def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Cols
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for condition in win_conditions:
        if board[condition[0]] != '.' and board[condition[0]] == board[condition[1]] == board[condition[2]]:
            return 1 if board[condition[0]] == 'X' else -1
    if '.' not in board:
        return 0
    return None

def evaluate_state(board, is_maximizing):
    global cache_hits_this_turn, evals_this_turn
    
    # 1. Check Cache
    if board in memo_table:
        cache_hits_this_turn += 1
        return memo_table[board]
        
    # 2. Count this as a new node evaluation
    evals_this_turn += 1
    
    winner = check_winner(board)
    if winner is not None:
        memo_table[board] = winner
        return winner
        
    # 3. Simulate and Recurse
    if is_maximizing:
        best_value = -float('inf')
        for i in range(9):
            if board[i] == '.':
                next_board = board[:i] + 'X' + board[i+1:]
                best_value = max(best_value, evaluate_state(next_board, False))
        memo_table[board] = best_value
        return best_value
    else:
        best_value = float('inf')
        for i in range(9):
            if board[i] == '.':
                next_board = board[:i] + 'O' + board[i+1:]
                best_value = min(best_value, evaluate_state(next_board, True))
        memo_table[board] = best_value
        return best_value

# --- GUI Application ----
class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Tic-Tac-Toe: Memoization Visualizer")
        
        # Main frames
        self.left_frame = tk.Frame(root, padx=20, pady=20)
        self.left_frame.pack(side=tk.LEFT)
        
        self.right_frame = tk.Frame(root, padx=20, pady=20)
        self.right_frame.pack(side=tk.RIGHT)
        
        # Grid Buttons
        self.buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            btn = tk.Button(self.left_frame, text="", font=('Helvetica', 24, 'bold'), 
                            width=5, height=2, command=lambda i=i: self.user_move(i))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(btn)
            
        # Reset Button
        self.reset_btn = tk.Button(self.left_frame, text="Reset Game (Keep Cache)", 
                                   command=self.reset_board, font=('Helvetica', 12))
        self.reset_btn.grid(row=3, column=0, columnspan=3, pady=10)
        
        # AI Log Text Area
        tk.Label(self.right_frame, text="🧠 AI Brain Log", font=('Helvetica', 14, 'bold')).pack()
        self.log_text = tk.Text(self.right_frame, height=25, width=45, bg="black", fg="lime green", font=('Consolas', 10))
        self.log_text.pack()
        
        self.log("System Ready. You play as 'X'.\nCache is completely empty.")

    def log(self, message):
        """Appends a message to the scrolling log."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) # Auto-scroll to bottom
        self.root.update()        # Force UI refresh

    def user_move(self, index):
        global board_state
        if board_state[index] == '.' and check_winner(board_state) is None:
            # Update Board String
            board_state = board_state[:index] + 'X' + board_state[index+1:]
            self.buttons[index].config(text="X", fg="blue")
            self.log(f"\n[USER] Plays at position {index}.")
            
            if check_winner(board_state) is None:
                # Trigger AI Turn
                self.root.after(100, self.agent_move)
            else:
                self.end_game()

    def agent_move(self):
        global board_state, cache_hits_this_turn, evals_this_turn
        self.log("\n[AGENT] My turn. Analyzing possible moves...")
        
        best_score = float('inf') # Agent is 'O' (Minimizing player)
        best_move = -1
        
        # Test every possible move
        for i in range(9):
            if board_state[i] == '.':
                # Reset counters for this specific branch
                cache_hits_this_turn = 0
                evals_this_turn = 0
                
                # Create hypothetical board
                next_board = board_state[:i] + 'O' + board_state[i+1:]
                self.log(f"-> Exploring move at pos {i}...")
                
                # Check if this top-level move is ALREADY in cache
                if next_board in memo_table:
                    score = memo_table[next_board]
                    self.log(f"   [MEMORY] I've seen this exact board! Score: {score}")
                else:
                    # Run Minimax
                    score = evaluate_state(next_board, True) # True because it will be X's turn next
                    self.log(f"   [COMPUTED] Score: {score}. (New nodes: {evals_this_turn} | Cache hits: {cache_hits_this_turn})")
                
                # Find the minimum score (best for 'O')
                if score < best_score:
                    best_score = score
                    best_move = i
                    
        # Make the optimal move
        if best_move != -1:
            board_state = board_state[:best_move] + 'O' + board_state[best_move+1:]
            self.buttons[best_move].config(text="O", fg="red")
            self.log(f"[AGENT] Chose position {best_move} (Target score: {best_score}).")
            
            if check_winner(board_state) is not None:
                self.end_game()

    def end_game(self):
        winner = check_winner(board_state)
        if winner == 1:
            self.log("\n*** GAME OVER: User (X) Wins! ***") # Should never happen
        elif winner == -1:
            self.log("\n*** GAME OVER: Agent (O) Wins! ***")
        else:
            self.log("\n*** GAME OVER: Draw! ***")
        self.log(f"Total entries now stored in Agent's memory: {len(memo_table)}")

    def reset_board(self):
        global board_state
        board_state = "........."
        for btn in self.buttons:
            btn.config(text="")
        self.log("\n--- NEW GAME ---")
        self.log("Note: Agent's memory was NOT erased. Watch how fast it thinks now!")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    print("SUCCESS: The code finished running and is opening the window now.") # Add this
    root.mainloop()
    
