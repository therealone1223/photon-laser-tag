import tkinter as tk

class PlayerEntryScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Player Entry")

        self.root.geometry("800x600")

        label = tk.Label(root, text="Player Entry Screen", font=("Arial", 24))
        label.pack(pady=50)

