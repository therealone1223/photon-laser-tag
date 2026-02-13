import socket

class UDPComm:
	def __init__(self, ip="127.0.0.1", send_port=7500, recv_port=7501, enable_receive=False):
	    self.ip = ip
	    self.send_port = send_port
	    self.recv_port = recv_port

	    # UDP Socket for Sending
	    self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	    #UDP Socket for Recieving
	    self.recv_sock = None
	    if enable_receive:
	        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	        self.recv_sock.bind(("0.0.0.0", self.recv_port))

	def broadcast_equipment_id(self, equipment_id):
	    message = str(equipment_id).encode("utf-8")
	    self.send_sock.sendto(message, (self.ip, self.send_port))
	    print(f"[UDP] Broadcasted equipment ID:", equipment_id)

	def receive_message(self):
	    if not self.recv_sock:
	        raise RuntimeError("Receieve socket not enabled")

	    data, addr = self.recv_sock.recvfrom(1024)
	    decoded = data.decode("utf-8")
	    print(f"[UDP] Received from",  addr, ":", decoded)
	    return decoded
