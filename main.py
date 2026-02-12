import tkinter as tk
from src.splash_screen import SplashScreen
from player_entry import PlayerEntryScreen

def open_player_entry():
    root = tk.Tk()
    PlayerEntryScreen(root)
    root.mainloop()

def main():
    splash_root = tk.Tk()
    SplashScreen(splash_root, duration=3000, on_close=open_player_entry)
    splash_root.mainloop()

if __name__ == "__main__":
    main()
