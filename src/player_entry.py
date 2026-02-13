import tkinter as tk
from tkinter import messagebox, ttk
import psycopg2
from udp_comm import UDPComm
class PlayerEntry:
    def __init__(self, root):
        self.root = root
        self.root.title("Photon - Edit Current Game")
        self.root.geometry("1200x700")
        self.root.configure(bg='black')
        
        # Database connection parameters
        self.db_params = {
            'dbname': 'photon',
            'user': 'student'
        }
        
        # UDP communication using teammate's code
        self.udp_comm = UDPComm(ip="127.0.0.1", send_port=7500, recv_port=7501, enable_receive=False)
        
        # Player entry fields (storing Entry widgets)
        self.red_team_ids = []
        self.red_team_names = []
        self.green_team_ids = []
        self.green_team_names = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create the main UI layout"""
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Edit Current Game",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="black"
        )
        title_label.pack(pady=10)
        
        # Main frame for teams
        teams_frame = tk.Frame(self.root, bg='black')
        teams_frame.pack(expand=True, fill='both', padx=20, pady=10)
        
        # Red Team Frame
        red_frame = tk.Frame(teams_frame, bg='#8B0000', relief='raised', bd=3)
        red_frame.grid(row=0, column=0, padx=10, sticky='nsew')
        
        red_label = tk.Label(
            red_frame,
            text="RED TEAM",
            font=("Arial", 18, "bold"),
            fg="white",
            bg='#8B0000'
        )
        red_label.pack(pady=10)
        
        # Create 15 player slots for red team
        for i in range(15):
            self.create_player_slot(red_frame, i, 'red')
        
        # Green Team Frame
        green_frame = tk.Frame(teams_frame, bg='#006400', relief='raised', bd=3)
        green_frame.grid(row=0, column=1, padx=10, sticky='nsew')
        
        green_label = tk.Label(
            green_frame,
            text="GREEN TEAM",
            font=("Arial", 18, "bold"),
            fg="white",
            bg='#006400'
        )
        green_label.pack(pady=10)
        
        # Create 15 player slots for green team
        for i in range(15):
            self.create_player_slot(green_frame, i, 'green')
        
        # Configure grid weights
        teams_frame.columnconfigure(0, weight=1)
        teams_frame.columnconfigure(1, weight=1)
        teams_frame.rowconfigure(0, weight=1)
        
        # Button Frame
        button_frame = tk.Frame(self.root, bg='black')
        button_frame.pack(pady=20)
        
        # Add Player Button
        add_button = tk.Button(
            button_frame,
            text="Add Players to DB",
            font=("Arial", 12, "bold"),
            bg="#00FF00",
            fg="black",
            command=self.add_all_players,
            width=18,
            height=2
        )
        add_button.grid(row=0, column=0, padx=10)
        
        # Delete Players Button
        delete_button = tk.Button(
            button_frame,
            text="Clear All Players",
            font=("Arial", 12, "bold"),
            bg="#FF4444",
            fg="white",
            command=self.clear_all_players,
            width=18,
            height=2
        )
        delete_button.grid(row=0, column=1, padx=10)
        
        # Change Socket Button
        socket_button = tk.Button(
            button_frame,
            text="Change Socket Settings",
            font=("Arial", 12, "bold"),
            bg="#4444FF",
            fg="white",
            command=self.change_socket_settings,
            width=18,
            height=2
        )
        socket_button.grid(row=0, column=2, padx=10)
        
        # Start Game Button
        start_button = tk.Button(
            button_frame,
            text="START GAME",
            font=("Arial", 14, "bold"),
            bg="#FFD700",
            fg="black",
            command=self.start_game,
            width=18,
            height=2
        )
        start_button.grid(row=1, column=0, columnspan=3, pady=10)
        
    def create_player_slot(self, parent, index, team):
        """Create a player entry slot"""
        slot_frame = tk.Frame(parent, bg=parent['bg'])
        slot_frame.pack(fill='x', padx=10, pady=2)
        
        # Player number label
        num_label = tk.Label(
            slot_frame,
            text=f"{index + 1:2d}.",
            font=("Arial", 10),
            fg="white",
            bg=parent['bg'],
            width=3
        )
        num_label.pack(side='left')
        
        # ID Entry
        id_entry = tk.Entry(
            slot_frame,
            font=("Arial", 10),
            width=8,
            bg='white'
        )
        id_entry.pack(side='left', padx=5)
        
        # Codename Entry
        name_entry = tk.Entry(
            slot_frame,
            font=("Arial", 10),
            width=20,
            bg='white'
        )
        name_entry.pack(side='left', padx=5)
        
        # Store references
        if team == 'red':
            self.red_team_ids.append(id_entry)
            self.red_team_names.append(name_entry)
        else:
            self.green_team_ids.append(id_entry)
            self.green_team_names.append(name_entry)
    
    def add_all_players(self):
        """Add all entered players to database and broadcast"""
        added_count = 0
        
        # Add red team players
        for i in range(15):
            player_id = self.red_team_ids[i].get().strip()
            codename = self.red_team_names[i].get().strip()
            
            if player_id and codename:
                try:
                    player_id = int(player_id)
                    if self.add_to_database(player_id, codename):
                        self.broadcast_equipment_code(player_id)
                        added_count += 1
                except ValueError:
                    messagebox.showerror("Error", f"Red team slot {i+1}: ID must be a number")
        
        # Add green team players
        for i in range(15):
            player_id = self.green_team_ids[i].get().strip()
            codename = self.green_team_names[i].get().strip()
            
            if player_id and codename:
                try:
                    player_id = int(player_id)
                    if self.add_to_database(player_id, codename):
                        self.broadcast_equipment_code(player_id)
                        added_count += 1
                except ValueError:
                    messagebox.showerror("Error", f"Green team slot {i+1}: ID must be a number")
        
        if added_count > 0:
            messagebox.showinfo("Success", f"Added {added_count} players to database!")
        else:
            messagebox.showwarning("Warning", "No players to add")
    
    def clear_all_players(self):
        """Clear all player entries"""
        if messagebox.askyesno("Confirm", "Clear all player entries?"):
            for entry in self.red_team_ids + self.red_team_names + self.green_team_ids + self.green_team_names:
                entry.delete(0, tk.END)
            messagebox.showinfo("Cleared", "All player entries cleared")
    
    def change_socket_settings(self):
        """Open dialog to change UDP socket settings"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Socket Settings")
        dialog.geometry("400x250")
        dialog.configure(bg='#2a2a2a')
        
        # IP setting
        tk.Label(dialog, text="IP Address:", fg="white", bg='#2a2a2a', font=("Arial", 12)).pack(pady=10)
        ip_entry = tk.Entry(dialog, font=("Arial", 12))
        ip_entry.insert(0, self.udp_comm.ip)
        ip_entry.pack(pady=5)
        
        # Send Port setting
        tk.Label(dialog, text="Send Port:", fg="white", bg='#2a2a2a', font=("Arial", 12)).pack(pady=10)
        send_port_entry = tk.Entry(dialog, font=("Arial", 12))
        send_port_entry.insert(0, str(self.udp_comm.send_port))
        send_port_entry.pack(pady=5)
        
        # Receive Port setting
        tk.Label(dialog, text="Receive Port:", fg="white", bg='#2a2a2a', font=("Arial", 12)).pack(pady=10)
        recv_port_entry = tk.Entry(dialog, font=("Arial", 12))
        recv_port_entry.insert(0, str(self.udp_comm.recv_port))
        recv_port_entry.pack(pady=5)
        
        def save_settings():
            new_ip = ip_entry.get()
            new_send_port = int(send_port_entry.get())
            new_recv_port = int(recv_port_entry.get())
            
            # Recreate UDPComm with new settings
            self.udp_comm = UDPComm(ip=new_ip, send_port=new_send_port, recv_port=new_recv_port, enable_receive=False)
            
            messagebox.showinfo("Saved", f"Socket settings updated!\nIP: {new_ip}\nSend Port: {new_send_port}\nReceive Port: {new_recv_port}")
            dialog.destroy()
        
        tk.Button(dialog, text="Save", command=save_settings, bg="#00FF00", font=("Arial", 12)).pack(pady=20)
    
    def start_game(self):
        """Start the game"""
        # Count how many players are entered
        red_count = sum(1 for entry in self.red_team_ids if entry.get().strip())
        green_count = sum(1 for entry in self.green_team_ids if entry.get().strip())
        
        if red_count == 0 and green_count == 0:
            messagebox.showerror("Error", "No players entered! Add players first.")
            return
        
        if messagebox.askyesno("Start Game", f"Start game with {red_count} red and {green_count} green players?"):
            messagebox.showinfo("Game Started", "Game is starting!")
            # Here you would transition to the game screen
            print("Game started!")
    
    def add_to_database(self, player_id, codename):
        """Add player to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            cursor = conn.cursor()
            
            # Check if player already exists
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
            
            print(f"Added to database: ID={player_id}, Codename={codename}")
            return True
            
        except Exception as e:
            print(f"Database error: {e}")
            return False
    
    def broadcast_equipment_code(self, equipment_id):
        """Broadcast equipment code via UDP using teammate's UDPComm"""
        try:
            self.udp_comm.broadcast_equipment_id(equipment_id)
        except Exception as e:
            print(f"UDP broadcast error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PlayerEntry(root)
    root.mainloop()