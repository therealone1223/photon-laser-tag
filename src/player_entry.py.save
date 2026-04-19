"""
player_entry.py
Photon Laser Tag – Sprint 3
Player entry screen:
  • Hardware ID column for every player slot
  • F5  → validate & launch play-action display (GameDisplay)
  • F12 → clear all player entries (with confirmation)
  • DB lookup / insert-or-update
  • UDP broadcast of equipment codes on player add
"""

import tkinter as tk
from tkinter import messagebox
import psycopg2

from udp_comm import UDPComm
from game_display import GameDisplay


class PlayerEntry:
    def __init__(self, root):
        self.root = root
        self.root.title("Photon – Edit Current Game")
        self.root.geometry("1400x750")
        self.root.configure(bg="black")

        # ── Key bindings ─────────────────────────────────────────
        self.root.bind("<F12>", lambda e: self.clear_all_players())
        self.root.bind("<F5>",  lambda e: self.start_game())

        # ── Database ─────────────────────────────────────────────
        self.db_params = {"dbname": "photon", "user": "student"}

        # ── UDP ──────────────────────────────────────────────────
        self.udp_comm = UDPComm(
            ip="127.0.0.1",
            send_port=7500,
            recv_port=7501,
            enable_receive=False,
        )

        self.processed_equipment = set()

        # Each slot stores (hardware_id_entry, player_id_entry, name_entry)
        self.red_team_slots   = []
        self.green_team_slots = []

        self.setup_ui()
        self.root.update_idletasks()

    # ═══════════════════════════════════════════════════════════════
    #  UI SETUP
    # ═══════════════════════════════════════════════════════════════

    def setup_ui(self):
        tk.Label(
            self.root,
            text="Edit Current Game",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black",
        ).pack(pady=10)

        teams_frame = tk.Frame(self.root, bg="black")
        teams_frame.pack(expand=True, fill="both", padx=20, pady=10)

        # Red Team
        red_frame = tk.Frame(teams_frame, bg="#8B0000", relief="raised", bd=3)
        red_frame.grid(row=0, column=0, padx=10, sticky="nsew")
        tk.Label(red_frame, text="RED TEAM",
                 font=("Arial", 18, "bold"), fg="white", bg="#8B0000").pack(pady=(10, 0))
        self._make_column_headers(red_frame, "#8B0000")
        for i in range(15):
            self.create_player_slot(red_frame, i, "red")

        # Green Team
        green_frame = tk.Frame(teams_frame, bg="#006400", relief="raised", bd=3)
        green_frame.grid(row=0, column=1, padx=10, sticky="nsew")
        tk.Label(green_frame, text="GREEN TEAM",
                 font=("Arial", 18, "bold"), fg="white", bg="#006400").pack(pady=(10, 0))
        self._make_column_headers(green_frame, "#006400")
        for i in range(15):
            self.create_player_slot(green_frame, i, "green")

        teams_frame.columnconfigure(0, weight=1)
        teams_frame.columnconfigure(1, weight=1)
        teams_frame.rowconfigure(0, weight=1)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="black")
        btn_frame.pack(pady=20)
        std = {"font": ("Arial", 12, "bold"), "width": 20, "height": 2}

        tk.Button(btn_frame, text="Add Players to DB",
                  bg="#00FF00", fg="black",
                  command=self.add_all_players, **std).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="Clear All Players  (F12)",
                  bg="#FF4444", fg="white",
                  command=self.clear_all_players, **std).grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Change Socket Settings",
                  bg="#4444FF", fg="white",
                  command=self.change_socket_settings, **std).grid(row=0, column=2, padx=10)

        tk.Button(btn_frame, text="▶  START GAME  (F5)",
                  font=("Arial", 14, "bold"), bg="#FFD700", fg="black",
                  command=self.start_game, width=22, height=2
                  ).grid(row=1, column=0, columnspan=3, pady=10)

    def _make_column_headers(self, parent, bg):
        hdr = tk.Frame(parent, bg=bg)
        hdr.pack(fill="x", padx=10, pady=(2, 0))
        for text, width in [("#", 3), ("HW ID", 8), ("Player ID", 9), ("Codename", 20)]:
            tk.Label(hdr, text=text,
                     font=("Arial", 9, "underline"),
                     fg="white", bg=bg, width=width, anchor="w").pack(side="left", padx=3)

    # ═══════════════════════════════════════════════════════════════
    #  PLAYER SLOTS
    # ═══════════════════════════════════════════════════════════════

    def create_player_slot(self, parent, index, team):
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(fill="x", padx=10, pady=1)

        tk.Label(row, text=f"{index + 1:2d}.",
                 font=("Arial", 10), fg="white", bg=parent["bg"], width=3).pack(side="left")

        # Hardware ID  (pink bg – visually distinct from player ID)
        hw_entry = tk.Entry(row, font=("Arial", 10), width=8, bg="#ffe0e0")
        hw_entry.pack(side="left", padx=3)

        # Player ID
        pid_entry = tk.Entry(row, font=("Arial", 10), width=9, bg="white")
        pid_entry.pack(side="left", padx=3)

        # Codename
        name_entry = tk.Entry(row, font=("Arial", 10), width=20, bg="white")
        name_entry.pack(side="left", padx=3)

        # Look up codename when player ID field loses focus or Enter pressed
        def on_player_complete(event=None):
            self.lookup_player(pid_entry, name_entry)
            self.handle_single_player(hw_entry, pid_entry, name_entry)

        pid_entry.bind("<FocusOut>", on_player_complete)
        pid_entry.bind("<Return>", on_player_complete)

        slot = (hw_entry, pid_entry, name_entry)
        if team == "red":
            self.red_team_slots.append(slot)
        else:
            self.green_team_slots.append(slot)

    # ═══════════════════════════════════════════════════════════════
    #  DATABASE
    # ═══════════════════════════════════════════════════════════════

    def _get_connection(self):
        return psycopg2.connect(**self.db_params)

    def lookup_player(self, pid_entry, name_entry):
        raw = pid_entry.get().strip()
        if not raw:
            return
        try:
            player_id = int(raw)
        except ValueError:
            return

        try:
            conn = self._get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            if row and not name_entry.get().strip():
                name_entry.delete(0, tk.END)
                name_entry.insert(0, row[0])
                print(f"DB lookup → ID={player_id}  Codename={row[0]}")
            elif not row:
                print(f"Player ID {player_id} not in DB – will be added on save")
        except Exception as exc:
            print(f"DB lookup error: {exc}")

    def add_to_database(self, player_id, codename):
        try:
            conn = self._get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM players WHERE id = %s", (player_id,))
            if cur.fetchone():
                cur.execute("UPDATE players SET codename = %s WHERE id = %s",
                            (codename, player_id))
            else:
                cur.execute("INSERT INTO players (id, codename) VALUES (%s, %s)",
                            (player_id, codename))
            conn.commit()
            cur.close()
            conn.close()
            print(f"DB write → ID={player_id}  Codename={codename}")
            return True
        except Exception as exc:
            print(f"DB error: {exc}")
            return False

    # ═══════════════════════════════════════════════════════════════
    #  UDP
    # ═══════════════════════════════════════════════════════════════

    def broadcast_equipment_code(self, equipment_id):
        try:
            self.udp_comm.broadcast_equipment_id(equipment_id)
            print(f"UDP broadcast – HW ID: {equipment_id}")
        except Exception as exc:
            print(f"UDP error: {exc}")

    # ═══════════════════════════════════════════════════════════════
    #  BUTTON / KEY ACTIONS
    # ═══════════════════════════════════════════════════════════════

    def add_all_players(self):
        """Validate all filled slots, write to DB, broadcast equipment IDs."""
        added  = 0
        errors = []

        for team_label, slots in [("Red",   self.red_team_slots),
                                   ("Green", self.green_team_slots)]:
            for i, (hw_e, pid_e, name_e) in enumerate(slots, start=1):
                hw_raw  = hw_e.get().strip()
                pid_raw = pid_e.get().strip()
                name    = name_e.get().strip()

                # Skipe completely empty rows
                if not hw_raw and not pid_raw and not name:
                    continue

                if not hw_raw:
                    errors.append(f"{team_label} slot {i}: Hardware ID required")
                    continue
                if not pid_raw:
                    errors.append(f"{team_label} slot {i}: Player ID required")
                    continue

                if not name:
                    errors.append(f"{team_label} slot {i}: Codename required")
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
                    added += 1

        if errors:
            messagebox.showerror("Input Errors", "\n".join(errors))

        if added > 0:
            messagebox.showinfo("Success", f"Added / updated {added} player(s).")
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
        """F12 – wipe every entry field after confirmation."""
        if messagebox.askyesno("Confirm Clear",
                               "Clear ALL player entries?\n(F12)"):
            for slots in (self.red_team_slots, self.green_team_slots):
                for hw_e, pid_e, name_e in slots:
                    hw_e.delete(0, tk.END)
                    pid_e.delete(0, tk.END)
                    name_e.delete(0, tk.END)
            print("All player entries cleared.")

    def start_game(self):
        """
        F5 – collect player data and open GameDisplay.
        Players are passed as list of dicts:
            {"hw_id": int, "player_id": int, "name": str}
        """
        red_players   = []
        green_players = []

        for hw_e, pid_e, name_e in self.red_team_slots:
            name = name_e.get().strip()
            if not name:
                continue
            try:
                hw_id     = int(hw_e.get().strip())
                player_id = int(pid_e.get().strip())
            except ValueError:
                hw_id, player_id = 0, 0
            red_players.append({"hw_id": hw_id, "player_id": player_id, "name": name})

        for hw_e, pid_e, name_e in self.green_team_slots:
            name = name_e.get().strip()
            if not name:
                continue
            try:
                hw_id     = int(hw_e.get().strip())
                player_id = int(pid_e.get().strip())
            except ValueError:
                hw_id, player_id = 0, 0
            green_players.append({"hw_id": hw_id, "player_id": player_id, "name": name})

        if not red_players and not green_players:
            messagebox.showerror("Error", "No players entered!\nAdd players first.")
            return

        if messagebox.askyesno(
            "Start Game",
            f"Start game?\n\n"
            f"  Red team:   {len(red_players)} player(s)\n"
            f"  Green team: {len(green_players)} player(s)",
        ):
            GameDisplay(self.root, red_players, green_players)

    def change_socket_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Socket Settings")
        dialog.geometry("400x280")
        dialog.configure(bg="#2a2a2a")

        fields = {}
        for label, default in [
            ("IP Address",   self.udp_comm.ip),
            ("Send Port",    str(self.udp_comm.send_port)),
            ("Receive Port", str(self.udp_comm.recv_port)),
        ]:
            tk.Label(dialog, text=label, fg="white", bg="#2a2a2a",
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
                    enable_receive=False,
                )
                messagebox.showinfo(
                    "Saved",
                    f"Socket updated\nIP: {new_ip}  Send: {new_sp}  Recv: {new_rp}",
                )
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ports must be integers.")

        tk.Button(dialog, text="Save", command=save,
                  bg="#00FF00", font=("Arial", 12), width=10).pack(pady=20)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    PlayerEntry(root)
    root.mainloop()
