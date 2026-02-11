from udp_comm import UDPComm

ip = input("Enter UDP IP address (default 127.0.0.1): ") or "127.0.0.1"
udp = UDPComm(ip=ip)

print("UDP test started.")
print("Enter equipment IDs to broadcast. Type 'q' to quit.")

while True:
	user_input = input("> ")

	if user_input.lower() == "q":
	    break

	try:
	    equipment_id = int(user_input)
	    udp.broadcast_equipment_id(equipment_id)
	except ValueError:
	    print("Please enter a valid integer.")
