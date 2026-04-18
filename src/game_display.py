"""
game_display.py
Photon Laser Tag – Sprint 4

Play-action display window:
  • Opens as a Toplevel over the player-entry screen
  • Shows both team rosters with live score columns (ready for Sprint 4 events)
  • 30-second countdown with large animated timer
  • Random MP3 music starts at 16s to sync with track's built-in countdown
  • Broadcasts equipment ID 202 when timer reaches zero ("GO!")
  • UDP listener thread scaffolded for Sprint 4 hit events
  • Clean phase management: COUNTDOWN → PLAYING → GAME_OVER
"""

import tkinter as tk
from tkinter import font as tkfont
import threading

from udp_comm import UDPComm
from music_player import MusicPlayer


# ─── Layout constants ─────────────────────────────────────────────────────────
BG_COLOR        = "black"
RED_BG          = "#8B0000"
GREEN_BG        = "#006400"
HEADER_FG       = "white"
SCORE_FG        = "#FFD700"
TIMER_FG_NORMAL = "#FFD700"
TIMER_FG_URGENT = "#FF3333"   # last 10 seconds turn red
TIMER_FG_GO     = "#00FF88"

COUNTDOWN_SECONDS = 30
GAME_DURATION     = 360       # 6-minute game (Sprint 4 will use this)
MUSIC_SYNC_AT     = 17        # start music at this second to sync with track countdown

GAME_START_CODE = 202
GAME_END_CODE   = 221


class GameDisplay:
    """
    Main play-action window.

    red_players / green_players  →  list of dicts:
        {"hw_id": int, "player_id": int, "name": str}
    """

    def __init__(self, parent, red_players: list, green_players: list):
        self.parent        = parent
        self.red_players   = red_players
        self.green_players = green_players

        # ── Score state ───────────────────────────────────────────────
        self.scores: dict[int, int] = {}
        for p in red_players + green_players:
            self.scores[p["hw_id"]] = 0

        # ── Phase tracking ────────────────────────────────────────────
        self.phase = "COUNTDOWN"   # COUNTDOWN → PLAYING → GAME_OVER

        # ── Music (single instance, started at MUSIC_SYNC_AT seconds) ─
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

        # Score label references  {hw_id: tk.Label}
        self.score_labels: dict[int, tk.Label] = {}

        self._build_ui()
        self._start_countdown(COUNTDOWN_SECONDS)   # music starts inside _tick at 16s

        # UDP listener thread
        self._udp_thread = threading.Thread(
            target=self._udp_listener, daemon=True
        )
        self._udp_thread.start()

    # ═══════════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
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

        self._build_team_panel(panels_frame, "RED TEAM",
                               self.red_players, RED_BG, column=0)
        self._build_team_panel(panels_frame, "GREEN TEAM",
                               self.green_players, GREEN_BG, column=1)

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

    def _build_team_panel(self, parent, title, players, bg, column):
        frame = tk.Frame(parent, bg=bg, relief="raised", bd=3)
        frame.grid(row=0, column=column, padx=15, sticky="nsew")

        tk.Label(frame, text=title,
                 font=("Arial", 20, "bold"), fg=HEADER_FG, bg=bg).pack(pady=(12, 4))

        hdr_row = tk.Frame(frame, bg=bg)
        hdr_row.pack(fill="x", padx=15, pady=(0, 4))
        for txt, w, anchor in [("#", 3, "e"), ("Codename", 22, "w"), ("Score", 7, "center")]:
            tk.Label(hdr_row, text=txt,
                     font=("Arial", 10, "underline"),
                     fg=HEADER_FG, bg=bg, width=w, anchor=anchor).pack(side="left", padx=4)

        tk.Frame(frame, bg=HEADER_FG, height=1).pack(fill="x", padx=10)

        if players:
            for idx, player in enumerate(players, start=1):
                self._build_player_row(frame, idx, player, bg)
        else:
            tk.Label(frame, text="(no players)",
                     font=("Arial", 11, "italic"), fg="#aaaaaa", bg=bg).pack(pady=20)

    def _build_player_row(self, parent, index, player, bg):
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", padx=15, pady=2)

        tk.Label(row, text=f"{index:2d}.",
                 font=("Arial", 11), fg=HEADER_FG, bg=bg,
                 width=3, anchor="e").pack(side="left", padx=4)

        tk.Label(row, text=player["name"],
                 font=("Arial", 12, "bold"), fg=HEADER_FG, bg=bg,
                 width=22, anchor="w").pack(side="left", padx=4)

        score_lbl = tk.Label(row, text="0",
                             font=("Arial", 12, "bold"), fg=SCORE_FG, bg=bg,
                             width=7, anchor="center")
        score_lbl.pack(side="left", padx=4)
        self.score_labels[player["hw_id"]] = score_lbl

    # ═══════════════════════════════════════════════════════════════════
    #  COUNTDOWN TIMER
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
            # Start music exactly once at MUSIC_SYNC_AT to sync with track countdown
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
        self.timer_label.config(text="GO!", fg=TIMER_FG_GO,
                                font=("Arial", 36, "bold"))
        try:
            self.udp_comm.broadcast_equipment_id(GAME_START_CODE)
            print(f"Broadcasted game start code: {GAME_START_CODE}")
        except Exception as exc:
            print(f"Broadcast error: {exc}")

        # Sprint 4: 6-minute game timer
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
        self.phase = "GAME_OVER"
        self.music.stop()
        self.title_label.config(text="🏁  GAME OVER  🏁")
        self.timer_label.config(text="Final Scores Above", fg=HEADER_FG,
                                font=("Arial", 22, "bold"))
        try:
            self.udp_comm.broadcast_equipment_id(GAME_END_CODE)
            print(f"Broadcasted game end code: {GAME_END_CODE}")
        except Exception as exc:
            print(f"Broadcast error: {exc}")

    # ═══════════════════════════════════════════════════════════════════
    #  SCORE UPDATES
    # ═══════════════════════════════════════════════════════════════════

    def update_score(self, hw_id: int, delta: int = 1):
        if hw_id not in self.scores:
            return
        self.scores[hw_id] += delta

        def _refresh():
            if hw_id in self.score_labels:
                self.score_labels[hw_id].config(text=str(self.scores[hw_id]))

        self.root.after(0, _refresh)

    # ═══════════════════════════════════════════════════════════════════
    #  UDP LISTENER
    # ═══════════════════════════════════════════════════════════════════

    def _udp_listener(self):
        while self.phase != "GAME_OVER":
            try:
                message = self.udp_comm.receive_message()
                if message:
                    self._handle_udp_message(message)
            except Exception:
                pass

    def _handle_udp_message(self, message: str):
        print(f"UDP received: {message!r}")
        # Sprint 4: scoring logic goes here

    # ═══════════════════════════════════════════════════════════════════
    #  CLEANUP
    # ═══════════════════════════════════════════════════════════════════

    def _on_close(self):
        self.phase = "GAME_OVER"
        self.music.stop()
        try:
            if hasattr(self.udp_comm, "close"):
                self.udp_comm.close()
        except Exception:
            pass
        self.root.destroy()
