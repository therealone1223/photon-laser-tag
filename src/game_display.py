"""
game_display.py
Photon Laser Tag – Sprint 4

Play-action display window:
  • Opens as a Toplevel over the player-entry screen
  • Shows both team rosters with live score columns
  • 30-second countdown with large animated timer
  • Random MP3 music starts at 16s to sync with track's built-in countdown
  • Broadcasts equipment ID 202 when timer reaches zero ("GO!")
  • Handles hit events and base hits over UDP
  • Clean phase management: COUNTDOWN → PLAYING → GAME_OVER
  • Displays cumulative team scores
  • Displays individual scores highest-to-lowest on each team
  • Flashes the leading team during play
  • Shows a button to return to player entry after game ends
"""

import tkinter as tk
import threading

from udp_comm import UDPComm
from music_player import MusicPlayer
from PIL import Image, ImageTk


# ─── Layout constants ─────────────────────────────────────────────────────────
BG_COLOR = "black"
RED_BG = "#8B0000"
GREEN_BG = "#006400"
HEADER_FG = "white"
SCORE_FG = "#FFD700"
TIMER_FG_NORMAL = "#FFD700"
TIMER_FG_URGENT = "#FF3333"
TIMER_FG_GO = "#00FF88"

COUNTDOWN_SECONDS = 30
GAME_DURATION = 360
MUSIC_SYNC_AT = 17

GAME_START_CODE = 202
GAME_END_CODE = 221


class GameDisplay:
    """
    Main play-action window.

    red_players / green_players → list of dicts:
        {"hw_id": int, "player_id": int, "name": str}
    """

    def __init__(self, parent, red_players: list, green_players: list):
        self.parent = parent
        self.red_players = red_players
        self.green_players = green_players

        # ── Score state ───────────────────────────────────────────────
        self.scores: dict[int, int] = {}
        self.players = {}
        self.team_map = {}

        self.player_name_labels = {}
        self.score_labels = {}

        self.team_frames = {}
        self.team_rows_container = {}
        self.team_total_labels = {}
        self.team_header_labels = {}

        self.back_button = None
        self.flash_state = False

        for p in red_players + green_players:
            self.scores[p["hw_id"]] = 0

        for p in red_players:
            self.players[p["hw_id"]] = {
                "name": p["name"],
                "score": 0,
                "team": "red",
                "base": False
            }
            self.team_map[p["hw_id"]] = "red"

        for p in green_players:
            self.players[p["hw_id"]] = {
                "name": p["name"],
                "score": 0,
                "team": "green",
                "base": False
            }
            self.team_map[p["hw_id"]] = "green"

        # ── Phase tracking ────────────────────────────────────────────
        self.phase = "COUNTDOWN"

        # ── Music ─────────────────────────────────────────────────────
        self.music = MusicPlayer()

        # ── UDP ───────────────────────────────────────────────────────
        self.udp_comm = UDPComm(
            ip="127.0.0.1",
            send_port=7500,
            recv_port=7501,
            enable_receive=True,
        )

        # ── Window ────────────────────────────────────────────────────
        self.root = tk.Toplevel(parent)
        self.root.title("Photon – Play Action Display")
        self.root.geometry("1200x700")
        self.root.configure(bg=BG_COLOR)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._start_countdown(COUNTDOWN_SECONDS)

        # UDP listener thread
        self._udp_thread = threading.Thread(
            target=self._udp_listener,
            daemon=True
        )
        self._udp_thread.start()

        # Base icon
        self.base_icon = None
        try:
            self.base_icon_img = Image.open("../baseicon.jpg")
            self.base_icon_img = self.base_icon_img.resize((20, 20))
            self.base_icon = ImageTk.PhotoImage(self.base_icon_img)
        except Exception as exc:
            print(f"Could not load base icon: {exc}")

    # ═══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION
    # ═══════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.title_label = tk.Label(
            self.root,
            text="GAME STARTING",
            font=("Arial", 28, "bold"),
            fg=HEADER_FG,
            bg=BG_COLOR,
        )
        self.title_label.pack(pady=(15, 5))

        panels_frame = tk.Frame(self.root, bg=BG_COLOR)
        panels_frame.pack(expand=True, fill="both", padx=30, pady=5)

        self._build_team_panel(
            panels_frame, "RED TEAM", self.red_players, RED_BG, column=0, team_key="red"
        )
        self._build_team_panel(
            panels_frame, "GREEN TEAM", self.green_players, GREEN_BG, column=1, team_key="green"
        )

        panels_frame.columnconfigure(0, weight=1)
        panels_frame.columnconfigure(1, weight=1)
        panels_frame.rowconfigure(0, weight=1)

        self.timer_label = tk.Label(
            self.root,
            text=f"Game starting in {COUNTDOWN_SECONDS}",
            font=("Arial", 26, "bold"),
            fg=TIMER_FG_NORMAL,
            bg=BG_COLOR,
        )
        self.timer_label.pack(pady=15)

    def _build_team_panel(self, parent, title, players, bg, column, team_key=None):
        frame = tk.Frame(parent, bg=bg, relief="raised", bd=3)
        frame.grid(row=0, column=column, padx=15, sticky="nsew")

        header_label = tk.Label(
            frame,
            text=title,
            font=("Arial", 20, "bold"),
            fg=HEADER_FG,
            bg=bg
        )
        header_label.pack(pady=(12, 4))

        total_label = tk.Label(
            frame,
            text="Team Score: 0",
            font=("Arial", 14, "bold"),
            fg=SCORE_FG,
            bg=bg
        )
        total_label.pack(pady=(0, 8))

        hdr_row = tk.Frame(frame, bg=bg)
        hdr_row.pack(fill="x", padx=15, pady=(0, 4))

        for txt, w, anchor in [
            ("#", 3, "e"),
            ("Codename", 22, "w"),
            ("Score", 7, "center")
        ]:
            tk.Label(
                hdr_row,
                text=txt,
                font=("Arial", 10, "underline"),
                fg=HEADER_FG,
                bg=bg,
                width=w,
                anchor=anchor
            ).pack(side="left", padx=4)

        tk.Frame(frame, bg=HEADER_FG, height=1).pack(fill="x", padx=10)

        rows_container = tk.Frame(frame, bg=bg)
        rows_container.pack(fill="both", expand=True, padx=5, pady=5)

        if team_key:
            self.team_frames[team_key] = frame
            self.team_rows_container[team_key] = rows_container
            self.team_total_labels[team_key] = total_label
            self.team_header_labels[team_key] = header_label

        if players:
            sorted_players = sorted(
                players,
                key=lambda p: self.players[p["hw_id"]]["score"],
                reverse=True
            )
            for idx, player in enumerate(sorted_players, start=1):
                self._build_player_row(rows_container, idx, player, bg)
        else:
            tk.Label(
                rows_container,
                text="(no players)",
                font=("Arial", 11, "italic"),
                fg="#aaaaaa",
                bg=bg
            ).pack(pady=20)

    def _build_player_row(self, parent, index, player, bg):
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", padx=15, pady=2)

        tk.Label(
            row,
            text=f"{index:2d}.",
            font=("Arial", 11),
            fg=HEADER_FG,
            bg=bg,
            width=3,
            anchor="e"
        ).pack(side="left", padx=4)

        name_frame = tk.Frame(row, bg=bg)
        name_frame.pack(side="left", padx=4)

        icon_label = tk.Label(name_frame, bg=bg)
        icon_label.pack(side="left")

        if self.players[player["hw_id"]]["base"] and self.base_icon is not None:
            icon_label.config(image=self.base_icon)
            icon_label.image = self.base_icon

        name_label = tk.Label(
            name_frame,
            text=player["name"],
            font=("Arial", 12, "bold"),
            fg=HEADER_FG,
            bg=bg
        )
        name_label.pack(side="left")

        score_lbl = tk.Label(
            row,
            text=str(self.players[player["hw_id"]]["score"]),
            font=("Arial", 12, "bold"),
            fg=SCORE_FG,
            bg=bg,
            width=7,
            anchor="center"
        )
        score_lbl.pack(side="left", padx=4)

        self.player_name_labels[player["hw_id"]] = (icon_label, name_label)
        self.score_labels[player["hw_id"]] = score_lbl

    # ═══════════════════════════════════════════════════════════════════
    # COUNTDOWN TIMER
    # ═══════════════════════════════════════════════════════════════════

    def _start_countdown(self, seconds: int):
        self._tick(seconds)

    def _tick(self, seconds: int):
        if seconds > 0:
            color = TIMER_FG_URGENT if seconds <= 10 else TIMER_FG_NORMAL
            self.timer_label.config(
                text=f"Game starting in  {seconds}",
                fg=color,
            )

            if seconds == MUSIC_SYNC_AT:
                self.music.start()
                print(f"[Music] Started at {seconds}s – synced to track countdown")

            self.root.after(1000, self._tick, seconds - 1)
        else:
            self._launch_game()

    def _launch_game(self):
        """Countdown hit zero — broadcast start code."""
        self.phase = "PLAYING"
        self.title_label.config(text="⚡  GAME IN PROGRESS  ⚡")
        self.timer_label.config(
            text="GO!",
            fg=TIMER_FG_GO,
            font=("Arial", 36, "bold")
        )

        try:
            self.udp_comm.broadcast_equipment_id(GAME_START_CODE)
            print(f"Broadcasted game start code: {GAME_START_CODE}")
        except Exception as exc:
            print(f"Broadcast error: {exc}")

        self._flash_leading_team()
        self.root.after(2000, self._start_game_timer, GAME_DURATION)

    def _start_game_timer(self, seconds: int):
        """6-minute game clock."""
        if self.phase != "PLAYING":
            return

        if seconds > 0:
            mins, secs = divmod(seconds, 60)
            self.timer_label.config(
                text=f"Time remaining:  {mins:02d}:{secs:02d}",
                fg=TIMER_FG_NORMAL,
                font=("Arial", 26, "bold"),
            )
            self.root.after(1000, self._start_game_timer, seconds - 1)
        else:
            self._end_game()

    def _end_game(self):
        """Game over — stop music, show scores, broadcast end code."""
        if self.phase == "GAME_OVER":
            return

        self.phase = "GAME_OVER"

        try:
            self.music.stop()
        except Exception:
            pass

        self.title_label.config(text="🏁  GAME OVER  🏁")
        self.timer_label.config(
            text="Final Scores Above",
            fg=HEADER_FG,
            font=("Arial", 22, "bold")
        )

        try:
            for _ in range(3):
                self.udp_comm.broadcast_equipment_id(GAME_END_CODE)
            print(f"Broadcasted game end code: {GAME_END_CODE} x3")
        except Exception as exc:
            print(f"Broadcast error: {exc}")

        self._refresh_scores()

        if self.back_button is None:
            self.back_button = tk.Button(
                self.root,
                text="Back to Player Entry",
                font=("Arial", 14, "bold"),
                command=self._return_to_entry,
                bg="#dddddd",
                fg="black",
                padx=12,
                pady=8
            )
            self.back_button.pack(pady=15)

    # ═══════════════════════════════════════════════════════════════════
    # SCORE UPDATES
    # ═══════════════════════════════════════════════════════════════════

    def update_score(self, hw_id: int, delta: int = 1):
        if hw_id not in self.players:
            return

        self.players[hw_id]["score"] += delta
        self._refresh_scores()

    def _rebuild_team_rows(self, team_key):
        container = self.team_rows_container.get(team_key)
        if not container:
            return

        bg = RED_BG if team_key == "red" else GREEN_BG
        team_players = self.red_players if team_key == "red" else self.green_players

        for widget in container.winfo_children():
            widget.destroy()

        sorted_players = sorted(
            team_players,
            key=lambda p: self.players[p["hw_id"]]["score"],
            reverse=True
        )

        if sorted_players:
            for idx, player in enumerate(sorted_players, start=1):
                self._build_player_row(container, idx, player, bg)
        else:
            tk.Label(
                container,
                text="(no players)",
                font=("Arial", 11, "italic"),
                fg="#aaaaaa",
                bg=bg
            ).pack(pady=20)

    def _refresh_scores(self):
        def update():
            red_total = sum(self.players[p["hw_id"]]["score"] for p in self.red_players)
            green_total = sum(self.players[p["hw_id"]]["score"] for p in self.green_players)

            if "red" in self.team_total_labels:
                self.team_total_labels["red"].config(text=f"Team Score: {red_total}")
            if "green" in self.team_total_labels:
                self.team_total_labels["green"].config(text=f"Team Score: {green_total}")

            self._rebuild_team_rows("red")
            self._rebuild_team_rows("green")

        self.root.after(0, update)

    def _flash_leading_team(self):
        if self.phase != "PLAYING":
            return

        red_total = sum(self.players[p["hw_id"]]["score"] for p in self.red_players)
        green_total = sum(self.players[p["hw_id"]]["score"] for p in self.green_players)

        self.flash_state = not self.flash_state

        red_header = self.team_header_labels.get("red")
        green_header = self.team_header_labels.get("green")
        red_total_lbl = self.team_total_labels.get("red")
        green_total_lbl = self.team_total_labels.get("green")

        if red_header:
            red_header.config(fg=HEADER_FG)
        if green_header:
            green_header.config(fg=HEADER_FG)
        if red_total_lbl:
            red_total_lbl.config(fg=SCORE_FG)
        if green_total_lbl:
            green_total_lbl.config(fg=SCORE_FG)

        if red_total > green_total:
            flash_color = "#FFFFFF" if self.flash_state else "#FFD700"
            if red_header:
                red_header.config(fg=flash_color)
            if red_total_lbl:
                red_total_lbl.config(fg=flash_color)

        elif green_total > red_total:
            flash_color = "#FFFFFF" if self.flash_state else "#FFD700"
            if green_header:
                green_header.config(fg=flash_color)
            if green_total_lbl:
                green_total_lbl.config(fg=flash_color)

        self.root.after(500, self._flash_leading_team)

    # ═══════════════════════════════════════════════════════════════════
    # UDP LISTENER
    # ═══════════════════════════════════════════════════════════════════

    def _udp_listener(self):
        while self.phase != "GAME_OVER":
            try:
                message = self.udp_comm.receive_message()
                if message:
                    self._handle_udp_message(message)
            except Exception as exc:
                print(f"UDP listener error: {exc}")

    def _handle_udp_message(self, message: str):
        print(f"UDP received: {message!r}")

        try:
            if message == "221":
                print("Game End Received")
                self._end_game()
                return

            attacker, target = message.split(":")
            attacker = int(attacker)

            if target == "43":
                self._handle_base_hit(attacker, "green")
                return

            if target == "53":
                self._handle_base_hit(attacker, "red")
                return

            target = int(target)
            self._handle_player_hit(attacker, target)

        except Exception as e:
            print("Error processing message:", e)

    def _handle_player_hit(self, attacker, target):
        if attacker not in self.players or target not in self.players:
            return

        attacker_team = self.team_map[attacker]
        target_team = self.team_map[target]

        if attacker_team == target_team:
            self.players[attacker]["score"] -= 10
            self.players[target]["score"] -= 10

            try:
                self.udp_comm.broadcast_equipment_id(attacker)
                self.udp_comm.broadcast_equipment_id(target)
            except Exception as exc:
                print(f"Broadcast error: {exc}")

            print(f"FRIENDLY FIRE: {self.players[attacker]['name']} hit teammate")

        else:
            self.players[attacker]["score"] += 10

            try:
                self.udp_comm.broadcast_equipment_id(target)
            except Exception as exc:
                print(f"Broadcast error: {exc}")

            print(f"{self.players[attacker]['name']} hit {self.players[target]['name']}")

        self._refresh_scores()

    def _handle_base_hit(self, attacker, base_team):
        if attacker not in self.players:
            return

        attacker_team = self.team_map[attacker]

        if attacker_team != base_team:
            self.players[attacker]["score"] += 100
            self.players[attacker]["base"] = True

            print(f"{self.players[attacker]['name']} captured base!")

            def update_icon():
                if attacker in self.player_name_labels and self.base_icon is not None:
                    icon_label, _ = self.player_name_labels[attacker]
                    icon_label.config(image=self.base_icon)
                    icon_label.image = self.base_icon

            self.root.after(0, update_icon)
            self._refresh_scores()

    # ═══════════════════════════════════════════════════════════════════
    # CLEANUP / RETURN
    # ═══════════════════════════════════════════════════════════════════

    def _return_to_entry(self):
        try:
            self.music.stop()
        except Exception:
            pass

        try:
            self.udp_comm.close()
        except Exception:
            pass

        if hasattr(self.parent, "game_open"):
            self.parent.game_open = False

        self.root.destroy()

    def _on_close(self):
        self.phase = "GAME_OVER"

        try:
            self.music.stop()
        except Exception:
            pass

        try:
            self.udp_comm.close()
        except Exception:
            pass

        if hasattr(self.parent, "game_open"):
            self.parent.game_open = False

        self.root.destroy()
