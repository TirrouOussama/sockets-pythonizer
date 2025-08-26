import os
import pickle
import socket
import sqlite3
import uuid
import time
import tempfile

TEMP = tempfile.gettempdir()


class TcpAuth:
    SERVERIP = "192.168.100.3"
    PORTS = {"identity_socket": 7159, "require_passcode": 7158}

    ERROR_CODES = {
        "IE00": "Limit Retries",
        "IE02": "Couldn't Establish Connection To Server",
        "IE03": "Couldn't Send Packet",
        "IE05": "File Reception Went Wrong",
        "IE07": "Couldn't form initial token request",
    }

    def __init__(self):
        self.identity_socket = None
        self.retry_cnt = 0
        self.mac = None
        self.result = (None, None)

    def get_mac(self):
        try:
            mac_num = uuid.getnode()
            self.mac = ":".join(
                [
                    "{:02x}".format((mac_num >> ele) & 0xFF)
                    for ele in range(0, 8 * 6, 8)
                ][::-1]
            )
            return self.mac
        except:
            return False

    # --------------------
    # Passcode request
    # --------------------
    def create_passcode_request(self, email, phone, password):
        if self.get_mac() == False:
            return False
        return f"require_passcode|{self.mac}|{password}|{phone}|{email}"

    def require_passcode(self, email, phone, password, retry_delay=1, retry_limit=3):
        self.result = (None, None)
        if self.identity_socket:
            try:
                self.identity_socket.close()
            except:
                pass
        self.retry_cnt = 0
        time.sleep(retry_delay)

        req = self.create_passcode_request(email, phone, password)
        if not req:
            self.result = (None, self.ERROR_CODES["IE07"])
            return self.result

        while self.retry_cnt <= retry_limit:
            try:
                self.identity_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.identity_socket.connect(
                    (self.SERVERIP, self.PORTS["require_passcode"])
                )
                self.retry_cnt = retry_limit
                self.identity_socket.send(bytes(req, "utf-8"))
                data = self.identity_socket.recv(500)
                decoded_data = pickle.loads(data)
                self.result = (decoded_data, None)
                return self.result
            except:
                self.retry_cnt += 1
                if self.retry_cnt > retry_limit:
                    self.result = (None, self.ERROR_CODES["IE00"])
                    return self.result

    # --------------------
    # Initial token request
    # --------------------
    def form_initial_token_request(self, email, phone, password, passcode):
        if self.get_mac() == False:
            return False
        return f"{self.mac}|{email}|{phone}|{password}|{passcode}"

    def get_initial_token(
        self, email, phone, password, passcode, retry_delay=1, retry_limit=3
    ):
        self.result = (None, None)
        if self.identity_socket:
            try:
                self.identity_socket.close()
            except:
                pass
        self.retry_cnt = 0
        time.sleep(retry_delay)

        req = self.form_initial_token_request(email, phone, password, passcode)
        if not req:
            self.result = (None, self.ERROR_CODES["IE07"])
            return self.result

        while self.retry_cnt <= retry_limit:
            try:
                self.identity_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.identity_socket.connect(
                    (self.SERVERIP, self.PORTS["identity_socket"])
                )
                self.retry_cnt = retry_limit
                self.identity_socket.send(bytes(req, "utf-8"))
                data = self.identity_socket.recv(500)
                decoded_data = pickle.loads(data)
                # Store token locally if valid
                if "pythonizer_" in decoded_data:
                    self.update_token(decoded_data)
                    self.result = ("authorized", None)
                    return self.result
                else:
                    self.result = ("unauthorized", None)
                    return self.result
            except:
                self.retry_cnt += 1
                if self.retry_cnt > retry_limit:
                    self.result = (None, self.ERROR_CODES["IE00"])
                    return self.result

    # --------------------
    # Local token storage
    # --------------------
    def fetch_token(self):
        conn = sqlite3.connect("databases/local_auth.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS local_auth (token TEXT)")
        cursor.execute("SELECT token FROM local_auth LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else False

    def update_token(self, new_token):
        try:
            conn = sqlite3.connect("databases/local_auth.db")
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS local_auth (token TEXT)")
            cursor.execute("DELETE FROM local_auth")
            cursor.execute("INSERT INTO local_auth (token) VALUES (?)", (new_token,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
