import tkinter as tk
from tkinter import messagebox
import psycopg2
from udp_comm import UDPComm
from game_display import GameDisplay

class PlayerEntry:
    def __init__(self, root):
        self.root = root
        self.root.title("Photon - Edit Current Game")
        self.root.geometry("1400x750")
        self.root.configure(bg='black')

        self.root.bind("<F12>", lambda event: self.clear_all_players())
        self.root.bind("<F5>", lambda event: self.start_game())

        self.db_params = {
            'dbname': 'photon',
            'user': 'student'
        }

        self.udp_comm = UDPComm(
            ip="127.0.0.1",
            send_port=7500,
            recv_port=7501,
            enable_receive=False
        )

        self.processed_equipment = set()

        # Each slot stores (hardware_id_entry, player_id_entry, name_entry)
        self.red_team_slots = []
        self.green_team_slots = []

        self.setup_ui()
        self.root.update_idletasks()

    # ------------------------------------------------------------------ #
    #  UI SETUP                                                            #
    # ------------------------------------------------------------------ #

    def setup_ui(self):
        tk.Label(
            self.root,
            text="Edit Current Game",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black"
        ).pack(pady=10)

        teams_frame = tk.Frame(self.root, bg='black')
        teams_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # --- Red team ---
        red_frame = tk.Frame(teams_frame, bg='#8B0000', relief='raised', bd=3)
        red_frame.grid(row=0, column=0, padx=10, sticky='nsew')

        tk.Label(
            red_frame, text="RED TEAM",
            font=("Arial", 18, "bold"), fg="white", bg='#8B0000'
        ).pack(pady=(10, 0))

        self._make_column_headers(red_frame, '#8B0000')

        for i in range(15):
            self.create_player_slot(red_frame, i, 'red')

        # --- Green team ---
        green_frame = tk.Frame(teams_frame, bg='#006400', relief='raised', bd=3)
        green_frame.grid(row=0, column=1, padx=10, sticky='nsew')

        tk.Label(
            green_frame, text="GREEN TEAM",
            font=("Arial", 18, "bold"), fg="white", bg='#006400'
        ).pack(pady=(10, 0))

        self._make_column_headers(green_frame, '#006400')

        for i in range(15):
            self.create_player_slot(green_frame, i, 'green')

        teams_frame.columnconfigure(0, weight=1)
        teams_frame.columnconfigure(1, weight=1)
        teams_frame.rowconfigure(0, weight=1)

        # --- Buttons ---
        button_frame = tk.Frame(self.root, bg='black')
        button_frame.pack(pady=20)

        btn_cfg = {"font": ("Arial", 12, "bold"), "width": 18, "height": 2}

        tk.Button(
            button_frame, text="Add Players to DB",
            bg="#00FF00", fg="black",
            command=self.add_all_players, **btn_cfg
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame, text="Clear All Players",
            bg="#FF4444", fg="white",
            command=self.clear_all_players, **btn_cfg
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            button_frame, text="Change Socket Settings",
            bg="#4444FF", fg="white",
            command=self.change_socket_settings, **btn_cfg
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            button_frame, text="START GAME (F5)",
            font=("Arial", 14, "bold"), bg="#FFD700", fg="black",
            command=self.start_game, width=18, height=2
        ).grid(row=1, column=0, columnspan=3, pady=10)

    def _make_column_headers(self, parent, bg):
        """Column header row: #  |  HW ID  |  Player ID  |  Codename"""
        hdr = tk.Frame(parent, bg=bg)
        hdr.pack(fill='x', padx=10, pady=(2, 0))

        for text, width in [("#", 3), ("HW ID", 8), ("Player ID", 9), ("Codename", 20)]:
            tk.Label(
                hdr, text=text,
                font=("Arial", 9, "underline"),
                fg="white", bg=bg, width=width, anchor='w'
            ).pack(side='left', padx=3)

    # ------------------------------------------------------------------ #
    #  PLAYER SLOT                                                         #
    # ------------------------------------------------------------------ #

    def create_player_slot(self, parent, index, team):
        slot_frame = tk.Frame(parent, bg=parent['bg'])
        slot_frame.pack(fill='x', padx=10, pady=1)

        tk.Label(
            slot_frame,
            text=f"{index + 1:2d}.",
            font=("Arial", 10), fg="white", bg=parent['bg'], width=3
        ).pack(side='left')

        # Hardware / Equipment ID  ← NEW field
        hw_entry = tk.Entry(slot_frame, font=("Arial", 10), width=8, bg='#ffe0e0')
        hw_entry.pack(side='left', padx=3)

        # Player ID — triggers DB lookup on <Tab> / <Return>
        pid_entry = tk.Entry(slot_frame, font=("Arial", 10), width=9, bg='white')
        pid_entry.pack(side='left', padx=3)

        # Codename
        name_entry = tk.Entry(slot_frame, font=("Arial", 10), width=20, bg='white')
        name_entry.pack(side='left', padx=3)

        # Look up codename when player ID field loses focus or Enter pressed
        def on_player_complete(event=None):
            self.lookup_player(pid_entry, name_entry)
            self.handle_single_player(hw_entry, pid_entry, name_entry)

        pid_entry.bind("<FocusOut>", on_player_complete)
        pid_entry.bind("<Return>", on_player_complete)

        slot = (hw_entry, pid_entry, name_entry)
        if team == 'red':
            self.red_team_slots.append(slot)
        else:
            self.green_team_slots.append(slot)

    # ------------------------------------------------------------------ #
    #  DATABASE OPERATIONS                                                 #
    # ------------------------------------------------------------------ #

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def lookup_player(self, pid_entry, name_entry):
        """Retrieve codename from DB when a player ID is entered."""
        raw = pid_entry.get().strip()
        if not raw:
            return

        try:
            player_id = int(raw)
        except ValueError:
            return  # not a valid ID yet; ignore silently

        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                # Auto-fill codename (only if the field is empty to avoid overwriting manual input)
                if not name_entry.get().strip():
                    name_entry.delete(0, tk.END)
                    name_entry.insert(0, row[0])
                    print(f"Loaded from DB: ID={player_id}, Codename={row[0]}")
            else:
                print(f"Player ID {player_id} not found in DB — new player")

        except Exception as e:
            print(f"DB lookup error: {e}")

    def add_to_database(self, player_id, codename):
        """Insert or update a player record."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM players WHERE id = %s", (player_id,))
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE players SET codename = %s WHERE id = %s",
                    (codename, player_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s)",
                    (player_id, codename)
                )

            conn.commit()
            cursor.close()
            conn.close()
            print(f"DB write: ID={player_id}, Codename={codename}")
            return True

        except Exception as e:
            print(f"Database error: {e}")
            return False

    # ------------------------------------------------------------------ #
    #  UDP BROADCAST                                                       #
    # ------------------------------------------------------------------ #

    def broadcast_equipment_code(self, equipment_id):
        """Broadcast the HARDWARE / equipment ID — not the player ID."""
        try:
            self.udp_comm.broadcast_equipment_id(equipment_id)
            print(f"Broadcast hardware ID: {equipment_id}")
        except Exception as e:
            print(f"UDP broadcast error: {e}")

    # ------------------------------------------------------------------ #
    #  BUTTON ACTIONS                                                      #
    # ------------------------------------------------------------------ #

    def add_all_players(self):
        added_count = 0
        errors = []

        for team_label, slots in [("Red", self.red_team_slots), ("Green", self.green_team_slots)]:
            for i, (hw_entry, pid_entry, name_entry) in enumerate(slots, start=1):
                hw_raw = hw_entry.get().strip()
                pid_raw = pid_entry.get().strip()
                name = name_entry.get().strip()

                # Skip completely empty rows
                if not hw_raw and not pid_raw and not name:
                    continue

                # Validate hardware ID
                if not hw_raw:
                    errors.append(f"{team_label} slot {i}: Hardware ID is required")
                    continue

                # Validate player ID
                if not pid_raw:
                    errors.append(f"{team_label} slot {i}: Player ID is required")
                    continue

                if not name:
                    errors.append(f"{team_label} slot {i}: Codename is required")
                    continue

                try:
                    hw_id = int(hw_raw)
                except ValueError:
                    errors.append(f"{team_label} slot {i}: Hardware ID must be a number")
                    continue

                try:
                    player_id = int(pid_raw)
                except ValueError:
                    errors.append(f"{team_label} slot {i}: Player ID must be a number")
                    continue

                if hw_id in self.processed_equipment:
                    continue

                if self.add_to_database(player_id, name):
                    self.processed_equipment.add(hw_id)
                    added_count += 1

        if errors:
            messagebox.showerror("Input Errors", "\n".join(errors))

        if added_count > 0:
            messagebox.showinfo("Success", f"Added/updated {added_count} player(s) in database.")
        elif not errors:
            messagebox.showwarning("Warning", "No players to add.")

    def handle_single_player(self, hw_entry, pid_entry, name_entry):
        hw_raw = hw_entry.get().strip()
        pid_raw = pid_entry.get().strip()
        name = name_entry.get().strip()

        if not hw_raw or not pid_raw or not name:
            return
        try:
            hw_id = int(hw_raw)
            player_id = int(pid_raw)
        except ValueError:
            return

        if self.add_to_database(player_id, name):
            self.broadcast_equipment_code(hw_id)

    def clear_all_players(self):
        if messagebox.askyesno("Confirm", "Clear all player entries? (F12)"):
            for slots in (self.red_team_slots, self.green_team_slots):
                for hw_e, pid_e, name_e in slots:
                    hw_e.delete(0, tk.END)
                    pid_e.delete(0, tk.END)
                    name_e.delete(0, tk.END)

    def start_game(self):
        red_count = sum(
            1 for _, pid_e, _ in self.red_team_slots if pid_e.get().strip()
        )
        green_count = sum(
            1 for _, pid_e, _ in self.green_team_slots if pid_e.get().strip()
        )

        if red_count == 0 and green_count == 0:
            messagebox.showerror("Error", "No players entered! Add players first.")
            return

        if messagebox.askyesno(
            "Start Game",
            f"Start game with {red_count} red and {green_count} green players?"
        ):

            red_players = []
            green_players = []

            #Collect red tam player names
            for _, _, name_e in self.red_team_slots:
                name = name_e.get().strip()
                if name:
                    red_players.append(name)

            #Collect green team player names
            for _, _, name_e in self.green_team_slots:
                name = name_e.get().strip()
                if name:
                    green_players.append(name)

            GameDisplay(self.root, red_players, green_players)

    def change_socket_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Socket Settings")
        dialog.geometry("400x280")
        dialog.configure(bg='#2a2a2a')

        fields = {}
        for label, default in [
            ("IP Address", self.udp_comm.ip),
            ("Send Port", str(self.udp_comm.send_port)),
            ("Receive Port", str(self.udp_comm.recv_port)),
        ]:
            tk.Label(dialog, text=label, fg="white", bg='#2a2a2a',
                     font=("Arial", 11)).pack(pady=(10, 0))
            e = tk.Entry(dialog, font=("Arial", 11))
            e.insert(0, default)
            e.pack(pady=3)
            fields[label] = e

        def save():
            try:
                new_ip = fields["IP Address"].get()
                new_sp = int(fields["Send Port"].get())
                new_rp = int(fields["Receive Port"].get())
                self.udp_comm = UDPComm(
                    ip=new_ip, send_port=new_sp, recv_port=new_rp,
                    enable_receive=False
                )
                messagebox.showinfo(
                    "Saved",
                    f"Socket updated\nIP: {new_ip}  Send: {new_sp}  Recv: {new_rp}"
                )
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ports must be integers.")

        tk.Button(dialog, text="Save", command=save,
                  bg="#00FF00", font=("Arial", 12), width=10).pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerEntry(root)
    root.mainloop()
