import tkinter as tk
from udp_comm import UDPComm

class GameDisplay:
    def __init__(self, parent, red_players, green_players):

        self.root = tk.Toplevel(parent)
        self.root.title("Photon - Game Action Display")
        self.root.geometry("1000x600")
        self.root.configure(bg="black")

        self.udp_comm = UDPComm(
            ip="127.0.0.1",
            send_port=7500,
            recv_port=7501,
            enable_receive=False
        )


        title = tk.Label(self.root,
                         text="GAME STARTING",
                         font=("Arial", 28, "bold"),
                         fg="white",
                         bg="black")
        title.pack(pady=20)

        main_frame = tk.Frame(self.root, bg="black")
        main_frame.pack()

        #Red Team Frame
        red_frame = tk.Frame(main_frame, bg="#8B0000", padx=50, pady=20)
        red_frame.grid(row=0, column=0, padx=50)

        tk.Label(red_frame,
                 text="RED TEAM",
                 font=("Arial", 18, "bold"),
                 fg="white",
                 bg="#8B0000").pack()

        for player in red_players:
            tk.Label(red_frame,
                     text=player,
                     font=("Arial", 12),
                     fg="white",
                     bg="#8B0000").pack()

        #Green Team Frame
        green_frame = tk.Frame(main_frame, bg="#006400", padx=50, pady=20)
        green_frame.grid(row=0, column=1, padx=50)

        tk.Label(green_frame,
                 text="GREEN TEAM",
                 font=("Arial", 18, "bold"),
                 fg="white",
                 bg="#006400").pack()

        for player in green_players:
            tk.Label(green_frame,
                     text=player,
                     font=("Arial", 12),
                     fg="white",
                     bg="#006400").pack()

        #Countdown timer label
        self.timer_label = tk.Label(self.root,
                                    text="Game starting in 30",
                                    font=("Arial", 24, "bold"),
                                    fg="yellow",
                                    bg="black")
        self.timer_label.pack(pady=30)

        self.countdown(30)


    def countdown(self, seconds):
        if seconds > 0:
            self.timer_label.config(text=f"Game starting in {seconds}")
            self.root.after(1000, self.countdown, seconds - 1)
        else:
            self.timer_label.config(text="GO!")

            #Broadcast start game code
            try:
                self.udp_comm.broadcast_equipment_id(202)
                print("Broadcasted game start code: 202")
            except Exception as e:
                print("Broadcast error:", e)
