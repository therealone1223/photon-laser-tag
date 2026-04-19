# photon-main
Main software for Photon Laser Tag
# Photon Laser Tag System
Software Engineering project for Jim Strother

## HOW-TO-RUN

## Installation

### Option 1: Automatic Install (Recommended)

```bash
cd photon-laser-tag
chmod +x install.sh
./install.sh
```

---

### Option 2: Manual Install

```bash
sudo apt update
sudo apt upgrade

sudo apt install -y \
    python3 python3-pip python3-tk \
    postgresql libpq-dev \
    python3-psycopg2 python3-pil python3-pil.imagetk \
    netcat-openbsd

pip install pillow psycopg2-binary pygame
```

Verify Python:

```bash
python3 --version
```

---

## Database

The project uses the instructor-provided PostgreSQL setup:

- Database: `photon`
- Table: `players`

Start PostgreSQL if needed:

```bash
sudo systemctl start postgresql
```

---

## How to Run

From the project root:

```bash
python3 main.py
```

---

## How to Use

### Startup Flow
1. Splash screen displays for 3 seconds  
2. Player entry screen appears automatically  

---

### Player Entry

1. Enter **Player ID**
   - If found → codename auto-fills  
   - If not → enter new codename (saved to DB)  

2. Enter **Equipment ID** (must be an integer)  

3. Assign player to:
   - Red Team (left)
   - Green Team (right)

4. Repeat for up to **15 players per team**

---

### Controls

- **F5 / Start Button** → Start game  
- **F12 / Clear Button** → Clear all players  

---

### Gameplay

After starting:

- 30-second countdown begins  
- Game automatically starts  
- Code `202` is broadcast  
- 6-minute game timer runs  
- Background music plays  

---

### Scoring Rules

| Event | Points |
|------|-------|
| Opponent hit | +10 |
| Friendly fire | -10 (both players) |
| Base capture | +100 |

---

### Base Events

- `53` → Red base scored  
- `43` → Green base scored  

Correct player receives:
- +100 points  
- Base icon displayed next to name  

---

### Game End

- Code `221` is broadcast **three times**  
- Final scores displayed  
- Button appears to return to player entry screen  

---

## UDP Networking

### Default Settings

- Address: `127.0.0.1`  
- Send Port: `7500`  
- Receive Port: `7501`  

---

### Data Formats

**Outgoing:**
```
<equipment_id>
```

**Incoming:**
```
attacker_id:target_id
```

---

### Example Test Commands

```bash
echo -n "1001:2001" | nc -u 127.0.0.1 7501
echo -n "1001:43"   | nc -u 127.0.0.1 7501
echo -n "221"       | nc -u 127.0.0.1 7501
```

---

## Testing

Monitor outgoing UDP:

```bash
nc -ul 7500
```

Simulate gameplay:

```bash
echo -n "1001:2001" | nc -u 127.0.0.1 7501
```

---

## Features

- Splash screen (3 seconds)
- Player entry with PostgreSQL integration
- Automatic database insertion for new players
- UDP communication (send + receive)
- Equipment ID broadcasting
- Countdown timer
- 6-minute gameplay timer
- Real-time play-by-play updates
- Live cumulative team scores
- Individual scores sorted highest to lowest
- Flashing leading team
- Base scoring with icon display
- Background music during gameplay
- End-of-game return button

---

## Project Structure

```
photon-laser-tag/
├── main.py
├── splash_screen.py
├── player_entry.py
├── game_display.py
├── udp_comm.py
├── music_player.py
├── logo.jpg
├── baseicon.jpg
├── install.sh
├── README.md
```

---

## Team Members

| GitHub Username | Name |
|----------------|------|
| therealone1223 | Quinn Cornia |
| Aran23         | Alonzo Rangel |
| evionj         | Evion Jimerson |
| takoma-coleman | Takoma Coleman |

---

## Troubleshooting

### PostgreSQL not running
```bash
sudo systemctl start postgresql
```

---

### Missing modules
```bash
sudo apt install python3-tk python3-psycopg2 python3-pil python3-pil.imagetk
pip install pillow pygame
```

---

### Netcat not found
```bash
sudo apt install netcat-openbsd
```

---

### Permission issues
```bash
chmod +x install.sh
```

---

## Notes

- Equipment IDs must be integers  
- Each team supports up to 15 players  
- UDP communication occurs on localhost  
- Game logic is event-driven via UDP messages 
