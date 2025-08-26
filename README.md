Tokenizer Authentication System
📝 Project Overview

This project provides a secure, token-based authentication system for users, enabling multi-factor authentication (MFA) with temporary passcodes and token renewal.

It uses SQLite databases for storage and TCP sockets for communication.

🎯 Purpose

Verify user identity using MFA passcodes sent via email.

Generate and manage session tokens bound to the user’s MAC address and IP.

Automatically renew tokens when expired without requiring re-login.

Maintain a lightweight SQLite database for credentials and passcodes.

Provide threaded TCP servers for concurrent user authentication.

🔄 High-Level Workflow
1️⃣ User Requests a Passcode

User sends: MAC | Email | Password | IP.

Server verifies credentials.

Server generates a 6-character temporary passcode.

Passcode is stored in op_passcodes.db and emailed to the user.

Purpose: Confirm the user’s identity before issuing a token.

2️⃣ User Authenticates with Passcode

User sends: MAC | Email | Phone | Password | Passcode.

Server validates:

Passcode exists and matches

Passcode is not expired

If valid:

Generate a Base Token (hashed credentials + salt)

Generate a Master Token (bound to MAC + IP + Base Token)

Store Master Token in op_creds.db

Delete the used passcode

Response example:

𝔄𝔴𝔣𝔢𝔯_𝔥𝔢𝔩𝔩𝔴𝔞𝔩𝔩_<base_token>


Purpose: Ensure multi-factor authentication and secure login.

3️⃣ User Makes Requests Using Tokens

Requests include:

TOKEN | MAC | REQUEST | DATA...


Server checks:

Recreates Master Token from received token + MAC + IP

Validates token in DB

Checks expiry:

Still valid → "authorized"

Expired → generate new Base Token → "renew|<base_token>"

Invalid → "unauthorized"

Purpose: Users can continue operations securely without re-login.

4️⃣ Token Renewal

If Master Token is expired:

Generate new Base Token from credentials

Replace old DB entry

Return:

renew|<base_token>


Purpose: Seamless workflow while maintaining session security.

🔑 Key Features

MAC + IP Binding: Tokens tied to user device and network.

Passcode Expiry: Temporary codes expire after 3 minutes.

Token Expiry: Master tokens expire after 1 hour, renewable automatically.

Email-Based MFA: Passcodes sent via email.

Lightweight DB: Uses SQLite (op_creds.db, op_passcodes.db).

Threaded TCP Servers: Supports multiple users concurrently.

🛠 Getting Started
Dependencies
pip install sqlite3

Run the Server
python identity_operator_server.py
python passcode_identity_operator_server.py

📂 Database Schema
op_creds.db
Column	Type
mac	TEXT
password	TEXT
email	TEXT
phone	TEXT
token	TEXT
expiry	TEXT
op_passcodes.db
Column	Type
mac	TEXT
ip	TEXT
phone	TEXT
email	TEXT
passcode	TEXT
expiry	TEXT
📝 Example Flow
User requests passcode → receives email → authenticates → gets Base Token → Master Token created
User uses token → server validates → token valid or renewed → user continues
