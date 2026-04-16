"""
music_player.py
Photon Laser Tag – Sprint 4

Handles random MP3 music selection and playback during gameplay.
Music starts when the 30-second countdown begins and stops when
the game ends.
"""

import os
import random
import threading

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("[Music] pygame not installed – music disabled.")


# Points to the photon_tracks/ folder in the repo root.
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "photon_tracks")


class MusicPlayer:
    """
    Picks a random MP3 from the music/ folder and plays it.
    Loops through all tracks in random order without repeating
    until all have played, then reshuffles.

    Usage:
        player = MusicPlayer()
        player.start()   # call when countdown begins
        player.stop()    # call when game ends
    """

    def __init__(self, music_dir: str = MUSIC_DIR):
        self.music_dir   = music_dir
        self._playing    = False
        self._thread     = None
        self._tracks     = []
        self._queue      = []

        if not PYGAME_AVAILABLE:
            return

        # Initialize pygame mixer once
        try:
            pygame.mixer.init()
            print("[Music] pygame mixer initialized.")
        except Exception as exc:
            print(f"[Music] mixer init failed: {exc}")

        self._load_tracks()

    # ─── Public API ───────────────────────────────────────────────

    def start(self):
        """Start playing music. Safe to call even if pygame is unavailable."""
        if not PYGAME_AVAILABLE or not self._tracks:
            print("[Music] No tracks found or pygame unavailable – skipping.")
            return

        self._playing = True
        self._thread  = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()
        print("[Music] Playback started.")

    def stop(self):
        """Stop playback immediately."""
        self._playing = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
                print("[Music] Playback stopped.")
            except Exception:
                pass

    # ─── Internal ─────────────────────────────────────────────────

    def _load_tracks(self):
        """Scan music_dir for .mp3 files."""
        if not os.path.isdir(self.music_dir):
            print(f"[Music] Music folder not found: {self.music_dir}")
            print("[Music] Make sure photon_tracks/ exists in your repo root.")
            return

        self._tracks = [
            os.path.join(self.music_dir, f)
            for f in os.listdir(self.music_dir)
            if f.lower().endswith(".mp3")
        ]

        if self._tracks:
            print(f"[Music] Found {len(self._tracks)} track(s) in {self.music_dir}")
        else:
            print(f"[Music] No .mp3 files found in {self.music_dir}")

    def _shuffled_queue(self):
        """Return all tracks in a new random order."""
        queue = list(self._tracks)
        random.shuffle(queue)
        return queue

    def _play_loop(self):
        """
        Background thread: plays tracks one at a time in random order.
        When all tracks have played, reshuffles and starts again.
        Stops when self._playing is set to False.
        """
        self._queue = self._shuffled_queue()

        while self._playing:
            if not self._queue:
                # All tracks played — reshuffle
                self._queue = self._shuffled_queue()

            track = self._queue.pop(0)
            print(f"[Music] Now playing: {os.path.basename(track)}")

            try:
                pygame.mixer.music.load(track)
                pygame.mixer.music.play()

                # Wait for track to finish (or stop() to be called)
                while self._playing and pygame.mixer.music.get_busy():
                    pygame.time.wait(500)

            except Exception as exc:
                print(f"[Music] Error playing {os.path.basename(track)}: {exc}")
                continue   # skip broken track, try next one

