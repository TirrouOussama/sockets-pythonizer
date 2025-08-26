#!/usr/bin/env python3
# identity_operator_server.py

import sqlite3
import time
import threading
import socket
import pickle
import hashlib
import random
import string
from datetime import datetime, timedelta
import uuid
import smtplib
import ssl
from email.message import EmailMessage

# ---------------------------
# Configuration
# ---------------------------
SERVERIP = "0.0.0.0"  # Change to your server IP if needed


# ---------------------------
# Database initialization
# ---------------------------
def create_creds_db():
    conn = sqlite3.connect("op_creds.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS op_creds (
            mac TEXT,
            password TEXT,
            email TEXT,
            phone TEXT,
            token TEXT,
            expiry TEXT
        )
    """
    )
    conn.commit()
    conn.close()


create_creds_db()


def create_passcode_db():
    conn = sqlite3.connect("op_passcodes.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS passcode_table (
            mac TEXT,
            ip TEXT,
            phone TEXT,
            email TEXT,
            passcode TEXT,
            expiry TEXT
        )
    """
    )
    conn.commit()
    conn.close()


create_passcode_db()


# ---------------------------
# Utility functions
# ---------------------------
def check_blank_creds(email, password):
    conn = sqlite3.connect("op_creds.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM op_creds WHERE email = ? AND password = ?", (email, password)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None


def random_generate_op_passcode():
    try:
        chars = string.ascii_uppercase + string.digits
        s = "".join(random.choices(chars, k=6))
        return s
    except:
        return False


def send_email(body, email_receiver):
    try:
        email_sender = "example@gmail.com"  # Replace with your email
        email_password = "xxxx xxxx xxxx xxxx"  # Replace with your app password
        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = "Validation"
        em.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        return True
    except Exception as e:
        print(f"[ERROR] send_email failed: {e}")
        return False


# ---------------------------
# Credential & Token Management
# ---------------------------
def insert_creds(password, email, phone, mac="", token="", expiry="None"):
    try:
        conn = sqlite3.connect("op_creds.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO op_creds (mac, password, email, phone, token, expiry)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (mac, password, email, phone, token, expiry),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] insert_creds failed: {e}")
        return False


def check_passcode_validity(mac, ip, email, passcode):
    try:
        conn = sqlite3.connect("op_passcodes.db")
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT passcode, expiry FROM passcode_table
            WHERE mac = ? AND ip = ? AND email = ?
        """,
            (mac, ip, email),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return False
        stored_passcode, expiry_str = row
        if stored_passcode != passcode:
            return False
        expiry_time = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
        return datetime.now() <= expiry_time + timedelta(minutes=3)
    except:
        return False


def create_base_token(mac, ip, email, password):
    try:
        chars = string.ascii_uppercase + string.digits
        s = "".join(random.choices(chars, k=12))
        s_hash = hashlib.sha256(s.encode("utf-8")).hexdigest()
        mac_hash = hashlib.sha256(mac.encode("utf-8")).hexdigest()
        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()
        email_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        conca = (
            mac_hash + s_hash + ip_hash + s_hash + email_hash + s_hash + password_hash
        )
        return hashlib.sha256(conca.encode("utf-8")).hexdigest()
    except:
        return False


def create_master_token(mac, ip, b_token):
    try:
        mac_hash = hashlib.sha256(mac.encode("utf-8")).hexdigest()
        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()
        conca = mac_hash + b_token + ip_hash
        return hashlib.sha256(conca.encode("utf-8")).hexdigest()
    except:
        return False


def insert_master_token_expiry(mac, ip, email, password, token):
    try:
        conn = sqlite3.connect("op_creds.db")
        cursor = conn.cursor()
        phone = "None"
        cursor.execute(
            """
            SELECT 1 FROM op_creds
            WHERE mac = ? AND phone = ? AND email = ? AND password = ?
        """,
            (mac, phone, email, password),
        )
        expiry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if cursor.fetchone():
            cursor.execute(
                """
                UPDATE op_creds SET token = ?, expiry = ?
                WHERE mac = ? AND phone = ? AND email = ? AND password = ?
            """,
                (token, expiry, mac, phone, email, password),
            )
        else:
            cursor.execute(
                """
                INSERT INTO op_creds (mac, password, email, phone, token, expiry)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (mac, password, email, phone, token, expiry),
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] insert_master_token_expiry: {e}")
        return False


def delete_op_passcode(email):
    try:
        conn = sqlite3.connect("op_passcodes.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passcode_table WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return True
    except:
        return False


# ---------------------------
# Server Minion Functions
# ---------------------------
def identity_operator_minion(clientsocket, address):
    data = clientsocket.recv(1024)
    if not data:
        clientsocket.close()
        return

    decoded_data = data.decode("utf-8")
    splited = decoded_data.split("|")
    ip = address[0]
    mac, email, phone, password, passcode = splited[:5]

    message = "False"
    if check_passcode_validity(mac, ip, email, passcode):
        base_token = create_base_token(mac, ip, email, password)
        if base_token:
            master_token = create_master_token(mac, ip, base_token)
            if master_token:
                if insert_master_token_expiry(mac, ip, email, password, master_token):
                    if delete_op_passcode(email):
                        message = "𝔄𝔴𝔣𝔢𝔯_𝔥𝔢𝔩𝔩𝔴𝔞𝔩𝔩_" + str(base_token)
    serialized_data = pickle.dumps(message)
    clientsocket.send(serialized_data)
    clientsocket.close()


def identity_operator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVERIP, 7159))
    print("Identity Operator Server is up on port 7159")
    while True:
        sock.listen(1)
        client_socket, addr = sock.accept()
        threading.Thread(
            target=identity_operator_minion, args=(client_socket, addr)
        ).start()


# ---------------------------
# Passcode Operator
# ---------------------------
def insert_passcode(mac, ip, email, passcode):
    try:
        conn = sqlite3.connect("op_passcodes.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passcode_table WHERE email = ?", (email,))
        expiry = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            """
            INSERT INTO passcode_table (mac, ip, phone, email, passcode, expiry)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (mac, ip, "None", email, passcode, expiry),
        )
        conn.commit()
        conn.close()
        return True
    except:
        return False


def passcode_identity_operator_minion(clientsocket, address):
    data = clientsocket.recv(1024)
    if not data:
        clientsocket.close()
        return
    decoded_data = data.decode("utf-8")
    splited = decoded_data.split("|")
    message = "False"
    if splited[0] == "require_passcode":
        ip = address[0]
        mac = splited[1]
        password = splited[2]
        phone = splited[3]
        email = splited[4]
        if check_blank_creds(email, password):
            pcode = random_generate_op_passcode()
            if pcode:
                if insert_passcode(mac, ip, email, pcode):
                    bd = f"Pythonizer MFA Temp Passcode For {email} is: {pcode}"
                    if send_email(bd, email):
                        message = "Passcode is sent"
    clientsocket.send(pickle.dumps(message))
    clientsocket.close()


def passcode_identity_operator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((SERVERIP, 7158))
    print("Passcode Operator Server is up on port 7158")
    while True:
        sock.listen(1)
        client_socket, addr = sock.accept()
        threading.Thread(
            target=passcode_identity_operator_minion, args=(client_socket, addr)
        ).start()


# ---------------------------
# Start Threads
# ---------------------------
threading.Thread(target=passcode_identity_operator, daemon=True).start()
threading.Thread(target=identity_operator, daemon=True).start()
