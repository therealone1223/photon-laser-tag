# photon-main
Main software for Photon Laser Tag
# Photon Laser Tag System
Software Engineering project for Jim Strother

## HOW-TO-RUN

### INSTALL DEPENDENCIES (IMPORTANT)

Make sure you have Python3 installed. Make sure you have updated PostgreSQL. Make sure you have psycopg2 installed. Make sure you have Tkinter installed. Make sure you have Pillow (PIL) installed.

To do the above steps, run these in your Linux terminal and enter Y when prompted (you might need to enter your password, for us, it is student):
```bash
sudo apt update
sudo apt upgrade
sudo apt install python3 python3-pip python3-tk
```

Verify Python runs by running the following in your terminal:
```bash
python3 --version
```

Next, we will update PostgreSQL and install dependencies for the application.

Run the following in your Linux terminal:
```bash
sudo apt-get update
sudo apt-get install postgresql libpq-dev
sudo apt-get install python3-psycopg2 python3-pil python3-pil.imagetk
```

REQUIRED:
```bash
pip install psycopg2
```

### Setup Database

Run these commands to set up the database:
```bash
sudo systemctl start postgresql
psql -U student -d photon
```

If the database doesn't exist, create it:
```bash
sudo -u postgres createdb photon
sudo -u postgres psql photon -c "GRANT ALL PRIVILEGES ON DATABASE photon TO student;"
```

Create the players table:
```sql
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    codename VARCHAR(255)
);
```

## TO RUN

### PRIMARY METHOD
1. Open Terminal
2. Navigate to the project directory
3. Navigate to src folder: `cd src`
4. Run: `python3 main.py`

### ALTERNATE METHOD
1. Open Terminal
2. Navigate directly to src directory: `cd /home/student/Desktop/photon-main/src/`
3. Run: `python3 main.py`

## HOW TO USE

1. Application starts with splash screen (displays for 3 seconds)
2. Player entry screen opens automatically
3. Enter EQUIPMENT ID (numeric value, ex: 42)
4. Enter CODENAME for the player
5. Assign players to RED TEAM (left side) or GREEN TEAM (right side)
6. Click "Add Players to DB" button to save all entered players to database and broadcast equipment codes via UDP
7. Click "Change Socket Settings" to configure UDP network settings (IP address, send port, receive port)
8. Click "START GAME" button to begin the game
9. Click "Clear All Players" to remove all entries from the form

### UDP Broadcasting
- Equipment codes are automatically broadcast via UDP when players are added
- Default settings: IP 127.0.0.1, Send Port 7500, Receive Port 7501
- Change settings using "Change Socket Settings" button

## Team Members

| GitHub Username | Real Name |
|-----------------|-----------|
| therealone1223  | Quinn Cornia |
| Aran23          | Alonzo Rangel |
| evionj     | Evion Jimerson |
| takoma-coleman     | Takoma Coleman |

## Project Structure
```
photon-main/
|- src/
|-  |- main.py              # Main application entry point
|   |- splash_screen.py     # Splash screen with logo
|   |- player_entry.py      # Player registration interface
|   |- udp_comm.py          # UDP communication handler
|- udp_files/               # UDP examples and documentation
|- logo.jpg                 # Application logo
|- player.sql               # Database schema
|- README.md                # This file
|- install.sh               # Installation script
```

## Features Completed (Sprint 2)

- [x] Splash screen with logo display
- [x] Player entry screen with Red/Green team setup
- [x] Database integration with PostgreSQL
- [x] UDP broadcasting of equipment codes after player addition
- [x] Network configuration options for UDP sockets
- [x] Add multiple players (up to 15 per team)
- [x] Clear all players functionality
- [x] Start game functionality

## Troubleshooting

### Database Connection Issues
If you see "could not connect to database":
```bash
sudo systemctl start postgresql
psql -U student -d photon
```

### Module Not Found Errors
If you see "No module named 'tkinter'" or similar:
```bash
sudo apt install python3-tk python3-psycopg2 python3-pil python3-pil.imagetk
```

### Permission Denied
```bash
chmod +x install.sh
chmod +x run.bash
```

## Notes

- Equipment IDs must be numeric
- Codenames can be alphanumeric
- UDP broadcasts occur automatically when players are added
- Database updates occur when "Add Players to DB" is clicked
- Each team can have up to 15 players
