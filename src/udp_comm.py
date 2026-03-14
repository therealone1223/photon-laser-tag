import socket

class UDPComm:
    def __init__(self, ip="127.0.0.1", send_port=7500, recv_port=7501, enable_receive=False):
        self.ip = ip
        self.send_port = send_port
        self.recv_port = recv_port

        # UDP Socket for Sending
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # UDP Socket for Receiving
        self.recv_sock = None
        if enable_receive:
            self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.recv_sock.bind(("0.0.0.0", self.recv_port))
            # 1-second timeout so the listener thread can notice when the
            # game ends and exit cleanly instead of blocking forever
            self.recv_sock.settimeout(1.0)

    def broadcast_equipment_id(self, equipment_id):
        message = str(equipment_id).encode("utf-8")
        self.send_sock.sendto(message, (self.ip, self.send_port))
        print(f"[UDP] Broadcasted equipment ID:", equipment_id)

    def receive_message(self):
        """
        Block until a packet arrives (up to 1 second) and return the decoded
        string, or return None on timeout.
        Raises RuntimeError if the receive socket was not enabled.
        """
        if not self.recv_sock:
            raise RuntimeError("Receive socket not enabled")
        try:
            data, addr = self.recv_sock.recvfrom(1024)
            decoded = data.decode("utf-8")
            print(f"[UDP] Received from", addr, ":", decoded)
            return decoded
        except socket.timeout:
            return None   # no packet this second – caller tries again

    def close(self):
        """Release both sockets (called when the game window is destroyed)."""
        try:
            self.send_sock.close()
        except Exception:
            pass
        if self.recv_sock:
            try:
                self.recv_sock.close()
            except Exception:
                pass